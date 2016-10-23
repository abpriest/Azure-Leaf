# author(s): Taylor Dohmen, Alex Priest, James Murphy
import os
import db
import sys
reload(sys)
sys.setdefaultencoding("UTF8")
from flask import Flask, render_template, request
from db import *
app = Flask(__name__)

loggedIn = False

@app.route('/', methods=['GET', 'POST'])
def index():
    global loggedIn
    if request.method == 'POST':
        if request.form['button'] == 'Sign Up':
            print 'here'
            if not createNewUser(request.form['username'], request.form['password'], 'is_dm' in request.form):
                return render_template('login.html', message = "That username is taken!")
            else:
                loggedIn = True
                return render_template('index.html')
    if not loggedIn:
        return render_template('login.html', message = "")
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(host = os.getenv('IP', '0.0.0.0'),
            port = int(os.getenv('PORT', 8080)),
            debug = True)
