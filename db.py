# author(s): Taylor Dohmen, Alex Priest, James Murphy
import psycopg2
import psycopg2.extras

def connectToDB():
    connectionStr = 'dbname=world user=waldo password=123 host=localhost'
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
    query = cur.mogrify("SELECT name FROM users WHERE username = %s", (username,))
    results = cur.execute(query)
    print (not results[0][0]) * "Username '%s' not available!" % username
    return not results[0][0]