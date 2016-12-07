import psycopg2
import psycopg2.extras

class AuthenticationException(Exception):
    pass

class CharacterCreationException(Exception):
    pass

class PostCreationException(Exception):
    pass

def connectToDB():
    connectionStr = 'dbname=azure_leaf user=azure password=123 host=localhost'
    try:
        return psycopg2.connect(connectionStr)
    except:
        print("Can't connect to database")

