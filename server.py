# author(s): Taylor Dohmen, Alex Priest, James Murphy
import os
import calendar
import sys
reload(sys)
sys.setdefaultencoding("UTF8")
from flask import Flask, render_template, request, session, redirect, url_for
from db import *
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app)

def inactive_session():
    return 'username' not in session or not session['username']
    
def login_redirect():
    return render_template('login.html', campaigns=loadCampaigns())

@app.route('/chat', methods = ['GET','POST'])
def chat():
    if inactive_session():
        return login_redirect()
    if request.method == 'POST':
        session['currentRoom'] = int(request.form['id'])
    post = getPost(int(session['currentRoom']))
    return render_template(
        'chat.html', 
        details = session, 
        current='chat', 
        post_title=post['title'],
        chars = [{'name':''}] + (loadCharacterSheets(session['username'],session['is_dm']))
    )

@app.route('/campaign', methods=['GET', 'POST'])
def campaignCreation():
    if inactive_session():
        return login_redirect()

    if request.method == 'POST':
        if request.form["button"] == "create":
            campaign = request.form['campaign']
            try: # avoid creating same-name campaigns for a particular user
                createNewCampaign(campaign, session['username'], session)
                session['campaign'] = campaign
                return redirect(url_for('index', details = session, current='home'))
            except Exception as e:
                print e
                return render_template(
                    'campaign.html',
                    details=session,
                    current='campaign',
                    campaigns=loadDirectory(),
                    errmsg=e
                )
        elif request.form["button"] == "join":
            campaignid = request.form["campaign"]
            campaign = getCampaign(campaignid)
            session['campaign'] = campaign[0]
            joinCampaign(session, campaignid)
            return redirect(url_for('index', details = session, current='home'))

    return render_template(
        'campaign.html', 
        details=session, 
        current='campaign', 
        campaigns=loadDirectory()
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()    
    if request.method == 'POST':
        if request.form['button'] == 'Log In':
            try:
                user = authenticate(request.form)
                print(user)
                session['username'] = user["username"]
                session['is_dm'] = user["is_dm"]
                session['campaign'] = user["campaign"][0]
                return redirect(
                    url_for('index', details=session, current='home')
                )
                
            except AuthenticationException as e:
                return render_template(
                    'login.html',
                    message=e
                )
    return render_template('login.html')
    
@app.route('/signup', methods=['GET','POST'])
def signup():
    session['username'] = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        campaign = request.form['campaign']
        is_dm = request.form['is_dm']
        campaign_info = getCampaign(campaign)
        session['campaign'] = campaign_info[0]
        session['cid'] = campaign_info[1]
        
        if request.form['button'] == 'Sign Up':
            try:
                createNewUser(username, password, is_dm, campaign)
                session['username'] = username
                session['is_dm'] = is_dm
                return redirect(
                    url_for('index', details=session, current='home')
                )
            except AuthenticationException as e:
                return render_template(
                    'signup.html',
                    message=e,
                    campaigns=loadCampaigns(),
                )
    return render_template('signup.html', campaigns=loadCampaigns())
    
@app.route('/characterSheet')
def characterSheet():
    if inactive_session():
        return login_redirect()
    
    loaded = loadCharacterSheets(
        user=session['username'],
        is_dm=session['is_dm']
    )
    
    if not loaded:
        return redirect(url_for('characterGen'))
    
    return render_template(
        'characterSheet.html',
        details=session,
        current='sheet',
        characters=loaded
    )
    
@app.route('/characterGen', methods=['GET', 'POST'])
def characterGen():
    if inactive_session():
        return login_redirect()
        
    if request.method == 'GET':
        if not session['is_dm']:
            loaded = loadCharacterSheets(
                user=session['username'],
                is_dm=session['is_dm']
            )
            print loaded
            loaded = loaded[0] if loaded else {}
            if loaded:
                redirect(url_for('characterEdit'))
        else:
            loaded = {};
        
        return render_template(
            'characterGen.html',
            details=session,
            current='gen',
            character=loaded
        )
    
    
    createCharacter(session, dict(request.form))
    return redirect(url_for('characterSheet'))

@app.route('/createPost', methods=['GET', 'POST'])
def genPost():
    if inactive_session():
        return login_redirect()
    if not session['is_dm']:
        return redirect(url_for('index', details=session, current='home'))
    if request.method == 'POST':
        print
        print request.form
        print dict(request.form)
        print 
        createPost(session, dict(request.form))
        return redirect(url_for('index', details=session, current='home'))
    return render_template('createPost.html', details=session, current='createPost')

@app.route('/characterEdit', methods=['GET', 'POST'])
def characterEdit():
    if inactive_session():
        return login_redirect()
        
    if request.method == 'GET':
        if not session['is_dm']:
            loaded = loadCharacterSheets(
                user=session['username'],
                is_dm=session['is_dm']
            )
            print loaded
            loaded = loaded[0] if loaded else {}
        else:
            loaded = {};
        
    if request.method == 'POST':
        print session
        if 'edit' not in session:
            loaded = loadSingleCharSheet(request.form['EditButton'])
            print loaded
            loaded = loaded[0] if loaded else {}
            session['edit'] = ''
            return render_template(
                'characterGen.html',
                details=session,
                current='gen',
                character=loaded
            )
    
    del session['edit']
    editCharacter(session, dict(request.form))
    return redirect(url_for('characterSheet'))
    

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' not in session or not session['username']:
        return redirect(url_for('login'))
    else:
        print session
        return render_template(
            'index.html',
            details=session,
            current='home',
            posts = loadPosts(session.get('cid', 0))
        )

    del session['edit']
    editCharacter(session, dict(request.form))
    return redirect(url_for('characterSheet', current='gen'))
    

@socketio.on('connect', namespace='/Chat')
def chatConnection():
    try:
        if not session['is_dm']:
            session['character'] = loadCharacterSheets(session['username'], session['is_dm'])[0]
        else:
            session['character'] = {'name':session['username']}
            session['charList'] = loadCharacterSheets(session['username'], session['is_dm'])
    except IndexError as e:
        print e
        return render_template('characterSheet', current='gen', details=session)
        
    join_room(session['currentRoom'])
    emit('user', dict(session))
    session['messages'] = getMessages(session['currentRoom'])
    
    for message in session['messages']:
        message['character'] = getPlayerCharacter(message['author'])
        message['date_posted'] = '{0}/{1} [{2}:{3}]'.format( 
            str(message['date_posted'].month),
            str(message['date_posted'].day),
            str(message['date_posted'].hour),
            str(message['date_posted'].minute)
        )
        emit('message', message, broadcast=False)
        
@socketio.on('disconnect', namespace ='/Chat')
def chatDisconnection():
    leave_room(session['currentRoom'])

@socketio.on('write', namespace='/Chat')
def writeMessage(temp):
    
    messageList = temp.split(' ')
    i = 1
    while i < len(messageList):
        if messageList[i-1] == '/roll' and messageList[i] in skills:
            skillcheck = generateSkillCheck(session['character']['id'], messageList[i])
            messageList[i-1] = messageList[i].upper()
            messageList[i] = str(skillcheck)
            i -= 1
        else:
            i += 1
        
    temp = ' '.join(messageList)
    print(temp)
    message = createMessage(session['username'], temp, session['currentRoom'])
    message['character'] = session['character']
    message['date_posted'] = '{0}/{1} [{2}:{3}]'.format( 
        str(message['date_posted'].month),
        str(message['date_posted'].day),
        str(message['date_posted'].hour),
        str(message['date_posted'].minute)
    )
    emit('message', message, room=session['currentRoom'])

if __name__ == '__main__':
    socketio.run(app,
        host=os.getenv('IP', '0.0.0.0'),
        port=int(os.getenv('PORT', 8080)),
        debug=True
    )
