# author(s): Taylor Dohmen, Alex Priest, James Murphy
import psycopg2
import psycopg2.extras
from random import randrange

# names of fields for data verification purposes
# made immutable and moved to global scope for function legibility
abilities = (
    'strength', 'constitution', 'dexterity',
    'intelligence', 'wisdom', 'charisma'
)
    
skills = (
    'Athletics', 'Acrobatics', 'Sleight_of_Hand', 'Stealth',
    'Arcana', 'History', 'Investigation', 'Nature', 'Religion',
    'Animal_Handling', 'Insight', 'Medicine', 'Perception',
    'Survival', 'Deception', 'Intimidation', 'Performance',
    'Persuasion'
)

skill_ability_map = {'strength': ('Athletics'), 
                    'dexterity':('Acrobatics','Sleight_of_Hand', 'Stealth'), 
                    'intelligence':('Arcana', 'History', 'Investigation', 'Nature', 'Religion'), 
                    'wisdom':('Animal_Handling', 'Insight', 'Medicine', 'Perception', 'Survival'), 
                    'charisma':('Deception', 'Intimidation', 'Performance', 'Persuasion')}

static_character_data = ('name', 'class', 'race', 'level', 'campaign', 'id')

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

def createPost(session, form):
    """ Inserts a new post into the database """
    if not session['is_dm']:
        raise PostCreationException("User is not a DM")
    conn = connectToDB()
    cur = conn.cursor()
    values = (
        session['username'],
        form['title'],
        form['subtitle'],
        form['body'],
        form['img_url'],
        getCampaignID(session['campaign'], session['username'])
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
    pass

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
    
def createNewCampaign(title, dm, user_data):
    """ Creates a new campaign named `title`, hosted by DM `dm`. """
    conn = connectToDB()
    cur = conn.cursor()
    query = cur.mogrify(
        'insert into campaigns (title, dm) VALUES (%s, %s);',
        (title, dm)
    )
    
    if getCampaignID(title, dm) > -1:
        raise Exception("User already has campaign called '%s'." % title)
    
    try:
        cur.execute(query)
    except Exception as e:
        conn.rollback()
        print e
    conn.commit()
    joinCampaign(user_data, getCampaignID(title, dm))
    
def loadCampaigns():
    """ Returns a list of dictionaries of campaigns:
        [{id : 0, title : "name"} ...]
    """
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    query = 'select id, title from campaigns;'
    cur.execute(query)
    return cur.fetchall()
    
def getCampaign(cid):
    """ Returns a title of a campaign from an id """
    conn = connectToDB()
    cur = conn.cursor()
    query = 'select title from campaigns where id = %s;' % int(cid)
    cur.execute(query)
    return cur.fetchone()

def getCampaignID(title, dm):
    """ Returns the id of a campaign from a dm name and a title """
    conn = connectToDB()
    cur = conn.cursor()
    query = cur.mogrify('select id from campaigns where title = %s and dm = %s;', (title, dm))
    cur.execute(query)
    return cur.fetchone() if cur.fetchone() else -1
    
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
        return 1
    conn.commit()
    return 0
    
def loadDungeonMasters():
    """ Load a mapping of dm username : campaign title """
    conn = connectToDB()
    cur = conn.cursor()
    query = (
        "select users.username, campaigns.title from "
        + "users inner join campaigns on users.username = campaigns.dm;"
    )
    cur.execute(query)
    results = cur.fetchall()
    print results
    return results
    
    
def generateAbility(threshold=7):
    """ Returns a randomly generated integer between threshold and 18 according
        to a 4d6d1 dice distribution.
    """
    score = 0
    while score <= threshold:
        # ability score = sum(4d6, drop lowest die)
		score = sum(sorted([randrange(6)+1 for die in xrange(4)])[1:])
    return score
    
def proficiencyBonus(level, expertise=False):
    """ Return proficiency bonus for a given level to apply to a skill. """
    return (((level - 1) / 4) + 2) * (1, 2)[expertise]
    
def abilityModifier(score):
    return (score - 10) / 2
    
# generates a value for a skill check for a character with the id passed
def generateRoll(char_id, skill):
    roll = randrange(1, 20)
    char = loadSingleCharSheet(char_id)
    ability = ''
    
    for key in skill_ability_map:
        if skill in skill_ability_map[key]:
            ability = key
    roll += abilityModifier(char[ability])
    
    if char[skill]:
        roll += proficiencyBonus(char['level'])
    return roll
    
    
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

def createPost(author, title, subtitle, body, img_url):
    db = connectToDB()
    cur = db.cursor()
           
    query = cur.mogrify(
        'insert into posts '
        + '(author, title, subtitle, body, img_url date_posted) '
        + 'values (%s, %s, %s, %s, %s, current_timestamp);',
        (author, title, subtitle, body, img_url)
    )
    
    try:
        cur.execute(query)
    except Exception as e:
        db.rollback()
        print(e)
        return {}
    db.commit()
    
def getPosts(session):
    db = connectToDB()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    query = cur.mogrify(
        'select posts.*, (select count(*) from messages where messages.related_post = posts.id) as post_count'
        + ' from posts;'
    )
    try:
        cur.execute(query)
    except Exception as e:
        print(e)
    return cur.fetchall()
    
def getPost(post_id):
    db = connectToDB()
    cur = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    query = cur.mogrify('select * from posts where id = %s;', (post_id,))
    try:
        cur.execute(query)
    except Exception as e:
        print(e)
    return cur.fetchone()
    