import os
import psycopg2
import psycopg2.extras
import sys
reload(sys)
sys.setdefaultencoding("UTF8")
from flask import Flask, render_template, request
app = Flask(__name__)

def connectToDB():
    connectionStr = 'dbname=world user=waldo password=123 host=localhost'
    try:
        return psycopg2.connect(connectionStr)
    except:
        print("Can't connect to database")
        
        
        # random words to prove a point