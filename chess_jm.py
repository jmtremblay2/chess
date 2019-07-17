# -*- coding: utf-8 -*-
"""
Created on Mon Apr  2 12:10:57 2018

@author: JM Tremblay
"""
import chess
import re
import psycopg2

# RE statement to recognize a game description (as opposed to a moves list)
descriptionRE = '\\[.+\\].*'
player = ['white','black']

SQLd = "INSERT INTO description "
SQLd += "(gameid, Black, BlackElo, Date, ECO, Event, EventDate, Result, Round, Site, White, WhiteElo, played)"
SQLd += "VALUES "
SQLd += "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

SQLb = "INSERT INTO 	board "
SQLb += "(gameid, moveid, player, played, board, enpassant, whitecastlequeen, whitecastleking, blackcastlequeen, blackcastleking)"
SQLb += "VALUES"
SQLb += "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

def getmoves(m):
    """ Converts a string with chess moves into a list of moves

    Args:
        m (str): a string containing the moves of a game

    Returns:
        list: a list of the moves in m

    """
    
    # remove result    
    m = m.replace('1/2-1/2','')
    m = m.replace('1-0','')
    m = m.replace('0-1','')
    m = m.replace('*','')
    
    # remove move numbers
    m = re.sub('[0-9]+\.', ' ', m)
    m = re.sub('^\s*', '', m)
    
    # fix spaces
    m = re.sub('\s*$', '', m)
    m = re.sub('\s+', ' ', m)
    
    # return list of moves
    return(m.split(' '))

def gamedict(d):
    """ builds a dictionary of all the attributes specified is the chess game

    Args:
        d (list): a list of descriptors of the chess game, in string format, using pgn

    Returns:
        dict: a dictionary of all the attributes specified

    """

    dict = {}
    #l = desc[0]
    for l in d:
        l = l.replace('[','')
        l = l.replace(']','')
        key = l.split(' ', 1)[0]
        value = re.search('".+"',l).group(0).replace('"','')
        dict[key] = value
    
    return(dict)

def dbconnect(dbname, uname, pw):
    """ connects to a local postgres database

    Args:
        dbname (str): the name of the database
        uname (str): username on the db
        pw (str): password

    Returns:
        a database connection
    """

    statement = "dbname='" + dbname + "' user='" + uname + "' password='" + pw + "'" + " host='localhost'" + " port=5432"
    try:
        conn=psycopg2.connect(statement)
    except:
        print ("I am unable to connect to the database.")
        conn = None
    return(conn)

def readLines(fullfname):
    lines = [f.replace("\n","") for f in open(fullfname,'r',encoding="ISO-8859-1") if f != "\n"]
    return lines

def chessStartEnd(lines):
    D = [bool(re.search(descriptionRE, line)) for line in lines]

    # find first and last line of each game in the data file
    starts = [i for i in  range(len(D)) if i == 0 or (D[i] and not D[i-1])]
    ends = starts[1:len(starts)] + [len(lines)]
    return starts, ends
    
def readGame(gamelines):
    d = gamedict([l for l in gamelines if bool(re.search(descriptionRE,l))])
    d['moves'] = getmoves(' '.join([l for l in gamelines if not bool(re.search(descriptionRE,l))]))
    return d

def getFens(moves):
    def getOneFen(m):
        board.push_san(m)
        return(board.fen())
    
    board = chess.Board()        
    try:
        fens = [getOneFen(m) for m in moves]
    except ValueError:
        fens = []    
    return fens

def processFen(fen):
    # gets the board layout
    def formatF0(f0):
        f0 = f0.replace('8','00000000')
        f0 = f0.replace('7','0000000')
        f0 = f0.replace('6','000000')
        f0 = f0.replace('5','00000')
        f0 = f0.replace('4','0000')
        f0 = f0.replace('3','000')
        f0 = f0.replace('2','00')
        f0 = f0.replace('1','0')
        return([list(line) for line in f0.split('/')])

    f = fen.split(' ')
    
    # en passant square if applicable       
    f3 = f[3]
    if '-' == f3:
        f3 = None
        
    # castling rights
    f2 = list(f[2])
    K = 'K' in f2
    Q = 'Q' in f2
    k = 'k' in f2
    q = 'q' in f2

    return (formatF0(f[0]),f3,Q,K,q,k)


def checkdate(d):
    """checks if a date is a valid yyyy.mm.dd format

    Args:
        d (str): a date encoded in a string

    Returns:
        str: d if d was a a valid date, None otherwise

    """
    leap = [1904, 1908, 1912, 1916, 1920, 1924, 1928, 1932, 1936, 
        1940, 1944, 1948, 1952, 1956, 1960, 1964, 1968, 1972, 
        1976, 1980, 1984, 1988, 1992, 1996, 2000, 2004, 2008, 
        2012, 2016, 2020]

    if None == d:
        return None
    if not bool(re.search('[1-2][0-9]{3}\.[0-9]{2}\.[0-9]{2}',d)):
        return None
    
    dd = [int(i) for i in d.split('.')]
    if dd[0] < 1900 or dd[0] > 2018:
        return None
    if dd[1] < 1 or dd[1] > 12:
        return None
    if dd[1] in (1,3,5,7,8,10,12) and (dd[2] < 0 or dd[2] > 31):
        return None
    if dd[1] in (4, 6, 9, 11) and (dd[2] < 0 or dd[2] > 30):
        return None
    if dd[1] == 2 and dd[0] in leap and (dd[2] < 0 or dd[2] > 29):
        return None
    if dd[1] == 2 and not(dd[0] in leap) and (dd[2] < 0 or dd[2] > 28):
        return None
            
    return d

def checkDesc(d):
    fields = ['gameid',
              'Black',
              'BlackElo',
              'Date',
              'ECO',
              'Event',
              'EventDate',
              'Result',
              'Round',
              'Site',
              'White',
              'WhiteElo',
              'moves']
    for f in fields:
        if not f in d:
            return False
    return True
    

def insertDesc(cur, d): 
    cur.execute(SQLd, (d.get('gameid'),
                       d.get('Black'),
                       int(d.get('BlackElo')), 
                       checkdate(d.get('Date')), 
                       d.get('ECO'), 
                       d.get('Event'), 
                       checkdate(d.get('EventDate')), 
                       d.get('Result'), 
                       d.get('Round'), 
                       d.get('Site'), 
                       d.get('White'), 
                       int(d.get('WhiteElo')),
                       d.get('moves')))  # correct
    return

def insertMoves(cur, d, b):
    for i in range(len(b)):
        cur.execute(SQLb, (d.get('gameid'), 
                           i // 2 + 1, #move id
                           player[i % 2], # player
                           d.get('moves')[i]) + b[i])
    return