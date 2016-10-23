# author(s): Taylor Dohmen, Alex Priest, James Murphy
import psycopg2
import psycopg2.extras
from hashlib import md5

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
    print (not results[0][0]) * "Username '%s' not available!" % username
    return not results[0][0]
    
def hashPassword(password, username):
    """ Returns an md5 hash of `password` with salt from `username` """
    pw_hash = md5(password)
    return username[0] + username[-1] + pw_hash
    
def createNewUser(username, password, is_dm):
    """ Calls isUserAvailable() to determine whether it's safe to
        create a new user with `username`. If it is safe, the new
        user is created with username `username`, a password salted
        and hashed from `password`, and `is_dm` determining whether
        they are a DM. Returns True if successful, false otherwise.
        
        If performance is affected by the nested function calls, we
        should rewrite this to require username availability as a
        precondition.
    """
    
    if not isUserAvailable(username):
        return False
    
    conn = connectToDB()
    pw_hash = hashPassword(password, username)
    cur = conn.cursor()
    query = cur.mogrify("INSERT INTO users (%s, %s, %s);", username, pw_hash, str(int(is_dm)))
    cur.execute(query)
    conn.commit()
    return True
