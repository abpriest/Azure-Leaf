# author(s): Taylor Dohmen, Alex Priest, James Murphy
import psycopg2
import psycopg2.extras
from hashlib import md5
from random import randrange

class AuthenticationException(Exception):
    pass

class CharacterCreationException(Exception):
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
    return results

def createNewCharacter(username, charname, charclass, charrace, abil, skill):
    """ Inserts a new character into the database """
    # abilities is a dict where (key, value) is "ability score name" : a_number
    
    # character must have a name
    if not charname:
        raise CharacterCreationException("Character name left blank.")
    
    # generate the correct number of %s format substrings for impending mogrify() call
    mog_number = bool(username) + bool(charname) + bool(charclass) + bool(charrace) + len(abil) + len(skill)
    mog = "(" + ', '.join(['%s'] * mog_number) + ");"
    
    conn = connectToDB()
    cur = conn.cursor()
    
    # mogrification hell
    qformat = "INSERT INTO characters (username, name, class, race, strength, dexterity, constitution, intelligence, wisdom, charisma) VALUES "
    query = cur.mogrify(qformat + mog, username, charname, charclass, charrace,
        abil['strength'], abil['dexterity'], abil['constitution'],
        abil['intelligence'], abil['wisdom'], abil['charisma']
    )
    cur.execute(query)
    conn.commit()
    return 0
    
def generateAbilities():
    """ Returns a dictionary of randomly generated 4d6d1 ability scores with
        the form {'strength' : a_number, ... }
    """
    scores = []
    abilities = [ # ability scores listed in canonical D&D ordering
        'strength', 'dexterity', 'constitution',
        'intelligence', 'wisdom', 'charisma'
    ]
    
    # roll 6 * 4d6d1 ability scores
    while len(scores) < 6:
        rolls = []
        for d in xrange(4):
            rolls.append(randrange(6) + 1)
        rolls.remove(min(rolls))
        curr = sum(rolls)
        if curr >= 7: # reroll anything lower than 7
        	scores.append(curr)
    return dict(zip(abilities, scores))
    
