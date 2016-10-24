# author(s): Taylor Dohmen, Alex Priest, James Murphy
import os
import db
import sys
reload(sys)
sys.setdefaultencoding("UTF8")
from flask import Flask, render_template, request, session
from db import *
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'


@app.route('/login', methods=['GET', 'POST'])
def logout():
    session['username'] = ''
    return render_template('login.html')
    
# @app.route('/create_char', methods = ['GET', 'POST'])
# def

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if request.form['button'] == 'Sign Up': # Sign Up logic
            try:
                createNewUser(username, password, 'is_dm' in request.form)
                session['username'] = username
                return render_template('index.html')
            except AuthenticationException as e:
                return render_template('login.html', message = e)
        else: # Log In logic
            try:
                authenticate(request.form['username'], request.form['password'])
                session['username'] = username
                return render_template('index.html')
            except AuthenticationException as e:
                return render_template('login.html', message = e)
                
    if not loggedIn:
        return render_template('login.html', message = "")
    else:
        return render_template('index.html', username = session['username'])

if __name__ == '__main__':
    app.run(host = os.getenv('IP', '0.0.0.0'),
            port = int(os.getenv('PORT', 8080)),
            debug = True)
