# author(s): Taylor Dohmen, Alex Priest, James Murphy
from random import randrange
from character import *
from campaign import getCampaign
        
def isUserAvailable(username):
    """ Queries the database for the presence of `username`
        returns False if not present, True otherwise
    """
    conn = connectToDB()
    if conn == None:
        raise Exception("Database connection failed.")
    cur = conn.cursor()
    
    # James' SQL contribution
    query = cur.mogrify(
        "SELECT username FROM users WHERE username = %s",
        (username,)
    )
    cur.execute(query)
    results = cur.fetchall()
    return not bool(results)
    
def createNewUser(username, password, is_dm, campaign):
    """ Inserts new user into database if username is available and password is
        valid.
    """
    if not username or not password:
        raise AuthenticationException("Username or password was left blank.")
    if not isUserAvailable(username):
        raise AuthenticationException("Username is not available.") 
    
    conn = connectToDB()
    cur = conn.cursor()
    
    # is_dm is a boolean, we must make it a '1' or '0' for psql BIT datatype
    # Taylor's SQL contribution
    query = cur.mogrify(
        "INSERT INTO users VALUES (%s, crypt(%s, gen_salt('bf')), %s, %s);",
        (username, password, str(int(is_dm)), campaign)
    )
    try:
        cur.execute(query)
    except Exception as e:
        conn.rollback()
        print e
        return 1
    conn.commit()
    return 0
    
def authenticate(form):
    """ Attempt to authenticate user with `username`, `password` """
    username = form['username']
    password = form['password']
    
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # Alex's SQL contribution
    query = cur.mogrify(
        "SELECT username, is_dm, campaign FROM users WHERE username = %s"
        + "AND password = crypt(%s, password);",
        (username, password)
    )
    
    try:
        cur.execute(query)
        results = cur.fetchall()[0]
        results["campaign"] = getCampaign(results["campaign"])
    except IndexError as e:
        print e
        results = ()
    if not bool(results):
        raise AuthenticationException("Incorrect username or password.")
    return results
    
    