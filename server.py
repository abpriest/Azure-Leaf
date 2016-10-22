# author(s): Taylor Dohmen, Alex Priest, James Murphy
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

    
