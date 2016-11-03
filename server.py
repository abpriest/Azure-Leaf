# author(s): Taylor Dohmen, Alex Priest, James Murphy
import os
import db
import sys
reload(sys)
sys.setdefaultencoding("UTF8")
from flask import Flask, render_template, request, session, redirect, url_for
from db import *
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app)

@app.route('/chat')
def chat():
    if 'username' not in session or not session['username']:
        return render_template('login.html', campaigns = loadCampaigns())
    return render_template('chat.html', current='chat')

@app.route('/login', methods=['GET', 'POST'])
def logout():
    session['username'] = ''
    return render_template('login.html', campaigns = loadCampaigns())
    
@app.route('/characterSheet')
def characterSheet():
    if 'username' not in session or not session['username']:
        return render_template('login.html', campaigns = loadCampaigns())
    loaded = loadCharacterSheets(user = session['username'], is_dm = session['is_dm'])
    if not loaded:
        return redirect(url_for('characterGen'))
    return render_template('characterSheet.html', username = session['username'], current='sheet', characters = loaded)


@app.route('/characterGen', methods = ['GET', 'POST'])
def characterGen():
    if 'username' not in session or not session['username']:
        return render_template('login.html', campaigns = loadCampaigns())
        
    if request.method == 'GET':
        return render_template('characterGen.html', username = session['username'], current='gen')

    createNewCharacter(session['username'], dict(request.form))
    return render_template('index.html', username = session['username'])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        campaign = request.form['campaign']
        
        if request.form['button'] == 'Sign Up': # Sign Up logic
            try:
                createNewUser(username, password, 'is_dm' in request.form, campaign)
                session['username'] = username
                session['is_dm'] = 'is_dm' in request.form
                return render_template('index.html', username = session['username'], current='home')
            except AuthenticationException as e:
                return render_template('login.html', message = e, campaigns = loadCampaigns())
        else: # Log In logic
            try:
                user = authenticate(request.form['username'], request.form['password'])
                # print user
                session['username'] = username
                session['is_dm'] = user[0][1]
                return render_template('index.html', username = session['username'], current='home')
            except AuthenticationException as e:
                return render_template('login.html', message = e, campaigns = loadCampaigns())
                
    if 'username' not in session or not session['username']:
        return render_template('login.html', message = "", campaigns = loadCampaigns())
    else:
        return render_template('index.html', username = session['username'], current='home')
        
@socketio.on('connect', namespace='/Chat')
def chatConnection():
    session['currentRoom'] = 1
    join_room(session['currentRoom'])
    session['messages'] = getMessages(session['currentRoom'])
    for message in session['messages']:
        message['date_posted'] = str(message['date_posted'])
        emit('message', message)
        
@socketio.on('write', namespace='/Chat')
def writeMessage(temp):
    message = createMessage(session['username'], temp, session['currentRoom'])
    message['date_posted'] = str(message['date_posted'])
    print(message)
    emit('message', message, room=session['currentRoom'])

if __name__ == '__main__':
    # app.run(host = os.getenv('IP', '0.0.0.0'),
    #         port = int(os.getenv('PORT', 8080)),
    #         debug = True)
    socketio.run(app, host=os.getenv('IP', '0.0.0.0'), port =int(os.getenv('PORT', 8080)), debug=True)
