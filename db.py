# author(s): Taylor Dohmen, Alex Priest, James Murphy
import psycopg2
import psycopg2.extras
from hashlib import md5

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
    query = cur.mogrify("SELECT username FROM users WHERE username = %s", (username,))
    cur.execute(query)
    results = cur.fetchall()
    # print results
    print (not bool(results)) * ("Username '%s' not available!" % username)
    return not bool(results)
    
def hashPassword(password, username):
    """ Returns an md5 hash of `password` with salt from `username` """
    pw_hash = md5(password).hexdigest()
    return username[0] + username[-1] + str(pw_hash)
    
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
    pw_hash = hashPassword(password, username)
    cur = conn.cursor()
    query = cur.mogrify("INSERT INTO users VALUES (%s, %s, %s);", (username, pw_hash, str(int(is_dm)))) # a banana bunch
    cur.execute(query)
    conn.commit()
    return 0
    
def authenticate(username, password):
    """ Attempt to authenticate user with `username`, `password` """
    if not username or not password:
        raise AuthenticationException("Username or password was left blank.")
    conn = connectToDB()
    pw_hash = hashPassword(password, username)
    cur = conn.cursor()
    query = cur.mogrify("SELECT username FROM users WHERE username = %s AND password = %s;", (username, pw_hash))
    cur.execute(query)
    results = cur.fetchall()
    if not bool(results):
        raise AuthenticationException("Incorrect username or password.")
    return 0

def createNewCharacter(username, charname, charclass, charrace):
    conn = connectToDB()
    cur = conn.cursor()
    query = cur.mogrify("INSERT INTO characters VALUES (%s, %s, %s, %s);", username, charname, charclass, charrace)
    cur.execute(query)
    conn.commit()

    