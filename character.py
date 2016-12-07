from _db import *
from _static import *

def getPlayerCharacter(username):
    """ Chat will need to render DM's username, players' character's name """
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    query = cur.mogrify(
        "select users.is_dm as is_dm, characters.name as charname from"
        + " users join characters on users.username = characters.username"
        + " where users.username = %s;",
        (username,)
    )
    try:
        cur.execute(query)
    except Exception as e:
        print e
    results = cur.fetchone()
    is_dm = int(results['is_dm'])
    charname = results['charname']
    if is_dm:
        return username
    return charname

def createCharacter(session, attr):
    """ Inserts a new character into the database """
    conn = connectToDB()
    cur = conn.cursor()
    user = session['username']

    # guarantee correct type for skills
    for skill in skills:
        if skill not in attr:
            attr[skill] = '0'
        else:
            attr[skill] = '1'
    
    # un-nest character name, class, level, etc
    # DO NOT DELETE THIS UNLESS VALUES PASS BY `attr` ARE SENT IN A NON-CONTANER
    # FORMAT
    for datum in static_character_data + abilities:
        try:
            attr[datum] = attr[datum][0]
        except KeyError as e:
            print e
            attr[datum] = 0
    
    print attr
    try:
        del attr['id']
    except KeyError as ke:
        print ke
    
    # the correct number of comma-separated
    # %s format substrings for impending mogrify() call
    mog_number = bool(user) + len(attr)
    mog = "(" + ', '.join(['%s'] * mog_number) + ")"
    
    # create (fields, ...) for INSERT statement formatting
    fields = '(' + ', '.join(attr.keys() + ["username"]) + ')'
    
    # create matching VALUES for INSERT statement
    values = tuple(attr.values() + [user])
    
    # select which version of the query to use
    qformat = "INSERT INTO characters %s VALUES " % fields
    query = cur.mogrify(qformat + mog + ';', values)
    
    print query
    try:
        cur.execute(query)
    except Exception as e:
        print e
        conn.rollback()
    conn.commit()
    return 0

def editCharacter(session, attr):
    """ Updates new character in the database """
    conn = connectToDB()
    cur = conn.cursor()
    user = session['username']

    # guarantee correct type for skills
    for skill in skills:
        if skill not in attr:
            attr[skill] = '0'
        else:
            attr[skill] = '1'
    
    # un-nest character name, class, level, etc
    # DO NOT DELETE THIS UNLESS VALUES PASSED BY `attr` ARE SENT
	# IN A NON-CONTANER FORMAT
    for datum in static_character_data + abilities:
        try:
            attr[datum] = attr[datum][0]
        except KeyError as e:
            print e
            attr[datum] = 0
    
    char_id = attr['id']
    print attr
    try:
        del attr['id']
    except Exception as e:
        print e
    
    # the correct number of comma-separated
    # %s format substrings for impending mogrify() call
    mog_number = bool(user) + len(attr)
    mog = "(" + ', '.join(['%s'] * mog_number) + ")"
    
    # create (fields, ...) for UPDATE statement formatting
    fields = '(' + ', '.join(attr.keys() + ["username"]) + ')'
    
    # create matching VALUES for UPDATE statement
    values = tuple(attr.values() + [user])
    
    # select which version of the query to use
    update = "UPDATE characters SET %s = " % fields
    query = cur.mogrify(update + mog + " where id = %s;", values + (char_id,))
    
    print query
    try:
        cur.execute(query)
    except Exception as e:
        print e
        conn.rollback()
    conn.commit()
    return 0


def loadSingleCharSheet(cid):
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    query = cur.mogrify(
        "select * from characters where id = %s;",
        (cid,)
    )
    cur.execute(query)
    results = cur.fetchall()
    
    # make Alex's life easier and make the HTML side of the site way less ugly
    for result in results:
        for key, value in result.items():
            if value == '1':
                result[key] = 1
            elif value == '0':
                result[key] = 0
    return results
    
def loadCharacterSheets(user, is_dm):
    """ Returns all the character sheets for the current (given) user, or for all
        characters in the user's session if user is DM.
    """
    # TODO:
    #   - check the organization of data for the results
    #   - make is_dm a useful variable
    #   - organize a session table/index in azure-leaf.sql to determine what characters
    #     a DM should be able to view
    
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    query = cur.mogrify(
        "select * from characters where username = %s;",
        (user,)
    )
    cur.execute(query)
    results = cur.fetchall()
    
    # make Alex's life easier and make the HTML side of the site way less ugly
    for result in results:
        for key, value in result.items():
            if value == '1':
                result[key] = 1
            elif value == '0':
                result[key] = 0
    return results
    