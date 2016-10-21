import psycopg2
import psycopg2.extras

def connectToDB():
    connectionStr = 'dbname=world user=waldo password=123 host=localhost'
    try:
        return psycopg2.connect(connectionStr)
    except:
        print("Can't connect to database")