from _db import *

def loadDirectory():
    """ Load a mapping of dm username : campaign title """
    conn = connectToDB()
    cur = conn.cursor()
    query = (
        "select users.username, campaigns.title, campaigns.id from "
        + "users inner join campaigns on users.username = campaigns.dm;"
    )
    cur.execute(query)
    results = cur.fetchall()
    print results
    return results

def joinCampaign(user_data, cid):
    """ User whose details are specified in session dict `user_data` is assigned
        to campaign referenced by campaign id `cid`.
    """
    
    conn = connectToDB()
    cur = conn.cursor()
    # mogrify not necessary here since these inputs are not taken from the user,
    # but elsewhere in the software stack
    query = cur.mogrify("update users set campaign = %s where username = %s;", (
        cid,
        user_data['username']
    ))
    try:
        cur.execute(query)
    except Exception as e:
        print "Issue in joinCampaign():"
        print e
        conn.rollback()
        return -1
    conn.commit()
    return cid

def getCampaign(cid):
    """ Returns a title of a campaign from an id """
    conn = connectToDB()
    cur = conn.cursor()
    query = 'select title, id from campaigns where id = %s;' % int(cid)
    cur.execute(query)
    return cur.fetchone()

def getCampaignID(title):
    """ Returns the id of a campaign from a dm name and a title """
    conn = connectToDB()
    cur = conn.cursor()
    print title
    query = cur.mogrify('select id from campaigns where title = %s;', (title,))
    print query
    cur.execute(query)
    results = cur.fetchone()
    return results[0] if results else -1
    
def loadCampaigns():
    """ Returns a list of dictionaries of campaigns:
        [{id : 0, title : "name"} ...]
    """
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    query = 'select id, title from campaigns;'
    cur.execute(query)
    return cur.fetchall()
    
def createNewCampaign(title, dm, user_data):
    """ Creates a new campaign named `title`, hosted by DM `dm`. """
    conn = connectToDB()
    cur = conn.cursor()
    query = cur.mogrify(
        'insert into campaigns (title, dm) VALUES (%s, %s);',
        (title, dm)
    )
    
    if getCampaignID(title) > -1:
        raise Exception("User already has campaign called '%s'." % title)
    
    try:
        cur.execute(query)
    except Exception as e:
        conn.rollback()
        print e
    conn.commit()
    joinCampaign(user_data, getCampaignID(title))
    
