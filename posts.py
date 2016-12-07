from _db import *
from campaign import getCampaignID

def getPost(post_id):
    db = connectToDB()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    query = cur.mogrify('select * from posts where id = %s;', (post_id,))
    try:
        cur.execute(query)
    except Exception as e:
        print(e)
    return cur.fetchone()

    
def createPost(session, form):
    """ Inserts a new post into the database """
    if not session['is_dm']:
        raise PostCreationException("User is not a DM")
    
    # un-nest HTML form output
    for key in form.keys():
        form[key] = form[key][0]
        url = 'nourl' if 'img_url' not in form else form['img_url']
        
    conn = connectToDB()
    cur = conn.cursor()
    values = (
        session['username'],
        form['title'],
        form['subtitle'],
        form['body'],
        url,
        getCampaignID(session['campaign'])
    )
    fields = "(author, title, subtitle, body, img_url, campaign, date_posted)"
    clause = "insert into posts %s " % fields
    query = cur.mogrify(clause + 'values (%s, %s, %s, %s, %s, %s, current_timestamp);', values)
    try:
        cur.execute(query)
    except Exception as e:
        print e
        conn.rollback()
    conn.commit()
    

    
def loadPosts(cid):
    """ Loads all posts for campaign specified by `cid` """
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    query = cur.mogrify("select posts.*, (select count(*) from messages where messages.related_post = posts.id) as post_count from posts where campaign = %s order by date_posted desc;", (cid,))
    print query
    try:
        cur.execute(query)
        results = cur.fetchall()
    except Exception as e:
        print e
        results = []
    print results
    return results
