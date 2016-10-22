# author(s): Taylor Dohmen, Alex Priest
import os
import db
import sys
reload(sys)
sys.setdefaultencoding("UTF8")
from flask import Flask, render_template, request
from db import *
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host = os.getenv('IP', '0.0.0.0'),
            port = int(os.getenv('PORT', 8080)),
            debug = True)
        
        # random words to prove a point
        
def is_user_available(username):
    """ Queries the database for the presence of `username`
        returns False if not present, True otherwise
    """
    conn = connectToDB()
    if conn == None:
        raise Exception("Database connection failed.")
    cur = conn.cursor()
    query = cur.mogrify("SELECT name FROM users WHERE username = %s", (username,))
    results = cur.execute(query)
    return not results[0][0]
    
    