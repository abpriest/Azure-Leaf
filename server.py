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

@app.route('/chat')
def chat():
    if inactive_session():
        return login_redirect()
    return render_template('chat.html', current='chat')

@app.route('/login', methods=['GET', 'POST'])
def logout():
    session['username'] = ''
    return render_template('login.html', campaigns = loadCampaigns())
    
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
    return render_template('characterSheet.html', username = session['username'], current='sheet', characters = loaded)

@app.route('/characterGen', methods=['GET', 'POST'])
def characterGen():
    if inactive_session():
        return login_redirect()
        
    if request.method == 'GET':
        loaded = loadCharacterSheets(
            user=session['username'],
            is_dm=session['is_dm']
        )
        print loaded
        loaded = loaded[0] if loaded else {}
        return render_template(
            'characterGen.html',
            username=session['username'],
            current='gen',
            character=loaded
        )

    editCharacter(session['username'], dict(request.form))
    return render_template('characterSheet.html', username=session['username'])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        campaign = request.form['campaign']
        
        if request.form['button'] == 'Sign Up': # Sign Up logic
            try: # Attempt to register new user
                is_dm = 'is_dm' in request.form
                createNewUser(username, password, is_dm, campaign)
                session['username'] = username
                session['is_dm'] = is_dm
                return render_template(
                    'index.html',
                    username=session['username'],
                    current='home',
                    posts=getPosts(),
                    month_name=calendar.month_name
                )
        
            except AuthenticationException as e: # Registration error
                return render_template(
                    'login.html',
                    message=e,
                    campaigns=loadCampaigns()
                )
        
        else: # Log In logic
            try: # Attempt to authenticate user
                user = authenticate(
                    request.form['username'],
                    request.form['password']
                )
                session['username'] = username
                session['is_dm'] = user[0][1]
                return render_template(
                    'index.html',
                    username=session['username'],
                    current='home',
                    posts=getPosts(),
                    month_name=calendar.month_name
                )
            
            except AuthenticationException as e:
                return render_template(
                    'login.html',
                    message=e,
                    campaigns=loadCampaigns()
                )
                
    if inactive_session():
        return login_redirect()
    else:
        return render_template(
            'index.html',
            username=session['username'],
            current='home',
            posts=getPosts(),
            name=calendar.month_name
        )
        
@socketio.on('connect', namespace='/Chat')
def chatConnection():
    session['currentRoom'] = 1
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
