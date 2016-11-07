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

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'username' not in session or not session['username']:
        return render_template('login.html', campaigns = loadCampaigns())
    return render_template('chat.html', details = session, current='chat')

@app.route('/login', methods=['GET', 'POST'])
def login():
    session['username'] = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        campaign = request.form['campaign']
        session['campaign'] = getCampaign(campaign)[0]
        
        if request.form['button'] == 'Sign Up': # Sign Up logic
            try:
                createNewUser(username, password, 'is_dm' in request.form, campaign)
                session['username'] = username
                session['is_dm'] = 'is_dm' in request.form
                return redirect(url_for('index', details = session, current='home'))
            except AuthenticationException as e:
                return render_template('login.html', message = e, campaigns = loadCampaigns())
        else: # Log In logic
            try:
                user = authenticate(request.form['username'], request.form['password'])
                # print user
                session['username'] = username
                session['is_dm'] = user[0][1]
                return redirect(url_for('index', details = session, current='home'))
            except AuthenticationException as e:
                return render_template('login.html', message = e, campaigns = loadCampaigns())
    return render_template('login.html', campaigns = loadCampaigns())
    
@app.route('/characterSheet')
def characterSheet():
    if 'username' not in session or not session['username']:
        return render_template('login.html', campaigns = loadCampaigns())
    loaded = loadCharacterSheets(user = session['username'], is_dm = session['is_dm'])
    if not loaded:
        return redirect(url_for('characterGen'))
    return render_template('characterSheet.html', details = session, current='sheet', characters = loaded)

@app.route('/characterGen', methods = ['GET', 'POST'])
def characterGen():
    if 'username' not in session or not session['username']:
        return render_template('login.html', campaigns = loadCampaigns())
        
    if request.method == 'GET':
        loaded = loadCharacterSheets(user = session['username'], is_dm = session['is_dm'])
        print loaded
        loaded = loaded[0] if loaded else {}
        return render_template('characterGen.html', details=session, current='gen', character=loaded)

    editCharacter(session['username'], dict(request.form))
    return render_template('characterSheet.html', details = session)

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' not in session or not session['username']:
        return redirect(url_for('login'))
    else:
        return render_template('index.html', details = session, current='home', posts = getPosts())

@socketio.on('connect', namespace='/Chat')
def chatConnection():
    session['currentRoom'] = 1 # don't you just have to change this to the post id?
    join_room(session['currentRoom'])
    session['messages'] = getMessages(session['currentRoom'])
    for message in session['messages']:
        message['date_posted'] = str(message['date_posted'])
        emit('message', message)
        
@socketio.on('disconnect', namespace ='/Chat')
def chatDisconnection():
    session['currentRoom'] = None
        
@socketio.on('write', namespace='/Chat')
def writeMessage(temp):
    message = createMessage(session['username'], temp, session['currentRoom'])
    message['date_posted'] = str(message['date_posted'])
    emit('message', message, room=session['currentRoom'])

if __name__ == '__main__':
    # app.run(host = os.getenv('IP', '0.0.0.0'),
    #         port = int(os.getenv('PORT', 8080)),
    #         debug = True)
    socketio.run(app, host=os.getenv('IP', '0.0.0.0'), port =int(os.getenv('PORT', 8080)), debug=True)
