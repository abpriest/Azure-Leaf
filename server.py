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

@app.route('/Chat')
def chat():
    return render_template('chat.html')

@app.route('/login', methods=['GET', 'POST'])
def logout():
    session['username'] = ''
    return render_template('login.html')
    
@app.route('/characterGen', methods = ['GET', 'POST'])
def characterGen():
    if not session['username']:
        redirect(url_for('/'))
        
    if request.method == 'GET':
        return render_template('characterGen.html', username = session['username'])
        
    createNewCharacter(session['username'], dict(request.form))
    return render_template('index.html', username = session['username'])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if request.form['button'] == 'Sign Up': # Sign Up logic
            try:
                createNewUser(username, password, 'is_dm' in request.form)
                session['username'] = username
                return render_template('index.html', username = session['username'])
            except AuthenticationException as e:
                return render_template('login.html', message = e)
        else: # Log In logic
            try:
                authenticate(request.form['username'], request.form['password'])
                session['username'] = username
                return render_template('index.html', username = session['username'])
            except AuthenticationException as e:
                return render_template('login.html', message = e)
                
    if 'username' not in session:
        return render_template('login.html', message = "")
    else:
        return render_template('index.html', username = session['username'])
        
@socketio.on('connect', namespace='/Chat')
def chatConnection():
    # join_room(session['currentRoom'])
    session['messages'] = getMessages()
    for message in session['messages']:
        emit('message', message)
        
@socketio.on('write', namespace='/Chat')
def writeMessage(temp):
    print(temp)
    createMessage(session['username'], temp, 1)
    session['messages'] = getMessages()
    for message in session['messages']:
        emit('message', message)

if __name__ == '__main__':
    # app.run(host = os.getenv('IP', '0.0.0.0'),
    #         port = int(os.getenv('PORT', 8080)),
    #         debug = True)
    socketio.run(app, host=os.getenv('IP', '0.0.0.0'), port =int(os.getenv('PORT', 8080)), debug=True)
