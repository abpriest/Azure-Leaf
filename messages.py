from _db import *

def getMessages(room):
    """ Retrieves messages from database based on room """
    db = connectToDB()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    query = cur.mogrify(
        "select id, author, body, date_posted from messages where related_post "
        + "= %s;",
        (room,)
    )
    try:
        cur.execute(query)
    except Exception as e:
        print(e)
        
    temp = cur.fetchall()
    if temp: 
        return temp
    return {}
    
def createMessage(username, message, related_post):
    """ Adds a new message to the message table """
    db = connectToDB()
    cur = db.cursor()
    query = cur.mogrify(
        'insert into messages (author, body, related_post, date_posted) '
        + 'values (%s, %s, %s, current_timestamp);',
        (username, message, related_post)
    )
    
    try:
        cur.execute(query)
    except Exception as e:
        db.rollback()
        print(e)
        return {}
    
    db.commit()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    query = cur.mogrify('select author, body, date_posted from messages ' +
        'order by date_posted desc limit 1;'
    )
    cur.execute(query)
    return cur.fetchone()

