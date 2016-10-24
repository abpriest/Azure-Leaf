# author(s): Taylor Dohmen, Alex Priest, James Murphy
import psycopg2
import psycopg2.extras
from hashlib import md5
from random import randrange

class AuthenticationException(Exception):
    pass

def connectToDB():
    connectionStr = 'dbname=azure_leaf user=azure password=123 host=localhost'
    try:
        return psycopg2.connect(connectionStr)
    except:
        print("Can't connect to database")
        
def isUserAvailable(username):
    """ Queries the database for the presence of `username`
        returns False if not present, True otherwise
    """
    conn = connectToDB()
    if conn == None:
        raise Exception("Database connection failed.")
    cur = conn.cursor()
    # James' SQL contribution
    query = cur.mogrify("SELECT username FROM users WHERE username = %s", (username,))
    cur.execute(query)
    results = cur.fetchall()
    return not bool(results)
    
def createNewUser(username, password, is_dm):
    """ Calls isUserAvailable() to determine whether it's safe to
        create a new user with `username`. If it is safe, the new
        user is created with username `username`, a password salted
        and hashed from `password`, and `is_dm` determining whether
        they are a DM. Returns 0 on success or error codes on failure.
        
        If performance is affected by the nested function calls, we
        should rewrite this to require username availability as a
        precondition.
    """
    if not username or not password:
        raise AuthenticationException("Username or password was left blank.")
    if not isUserAvailable(username):
        raise AuthenticationException("Username is not available.") 
    
    conn = connectToDB()
    
    # pw_hash = hashPassword(password, username)
    cur = conn.cursor()
    
    # is_dm is a boolean, we must make it a '1' or '0' for psql BIT datatype
    # Taylor's SQL contribution
    query = cur.mogrify("INSERT INTO users VALUES (%s, crypt(%s, gen_salt('bf')), %s);", (username, password, str(int(is_dm))))
    cur.execute(query)
    conn.commit()
    return 0
    
def authenticate(username, password):
    """ Attempt to authenticate user with `username`, `password` """
    if not username or not password:
        raise AuthenticationException("Username or password was left blank.")
    conn = connectToDB()
    cur = conn.cursor()
    # Alex's SQL contribution
    query = cur.mogrify("SELECT username FROM users WHERE username = %s AND password = crypt(%s, password);", (username, password))
    cur.execute(query)
    results = cur.fetchall()
    if not bool(results):
        raise AuthenticationException("Incorrect username or password.")
    return 0

def createNewCharacter(username, charname, charclass, charrace, abilities):
    """ Inserts a new character into the database """
    
    # abilities is a dict where (key, value) is "ability score name" : a_number
    conn = connectToDB()
    cur = conn.cursor()
    query = cur.mogrify("INSERT INTO characters VALUES (%s, %s, %s, %s);", username, charname, charclass, charrace)
    cur.execute(query)
    conn.commit()

    
def generateAbilities():
    """ Returns a dictionary of randomly generated ability scores with the form
        'strength' : a_number, etc.
    """
    abilities = [ # ability scores listed in canonical D&D ordering
        'strength', 'dexterity', 'constitution',
        'intelligence', 'wisdom', 'charisma'
    ]
    scores = []
    
    # roll 6 * 4d6d1 ability scores
    for score in xrange(0,6):
        rolls = []
        for die in xrange(0,4):
            rolls.append(randrange(1,6))
        rolls.remove(min(rolls))
        scores.append(sum(rolls))
    return dict(zip(abilities, scores))
        
    