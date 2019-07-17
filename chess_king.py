# -*- coding: utf-8 -*-
"""
Created on Tue May  1 11:30:46 2018

@author: jtrembl3
"""

import os

root = "/home/jm/programming/chess"
gamesfolder = "games"
os.chdir(root)
fnames = os.listdir(gamesfolder)

import chess_jm
    
conn = chess_jm.dbconnect(dbname = "chess", uname = "postgres", pw = "postgres")
conn.set_session(deferrable=True, autocommit=None)
cur = conn.cursor()

# not super efficient but we assign an id to each game before we get started
startid = 1
gameids = {}
for fname in fnames:
    print(fname)
    fullfname = root + "/" + gamesfolder + "/" + fname
    lines = chess_jm.readLines(fullfname)
    starts, ends = chess_jm.chessStartEnd(lines)
    gameids[fname] = list(range(startid,startid + len(starts)))
    startid = startid + len(starts)

#fname = fnames[0]
for fname in fnames:
    print(fname)
    fullfname = root + "/" + gamesfolder + "/" + fname
    lines = chess_jm.readLines(fullfname)
    starts, ends = chess_jm.chessStartEnd(lines)
    #i = 0
    #i = i + 1
    for i in range(len(starts)):
        gameid = gameids[fname][i]
        print(i)
        if(0 == gameid % 10000):
            print(gameid)
        d = chess_jm.readGame(lines[starts[i]:ends[i]])
        d['gameid'] = gameid
        if not chess_jm.checkDesc(d):
            continue
        fens = chess_jm.getFens(d['moves'])
        chess_jm.insertDesc(cur, d)
        # if one move in the moves sequence is illegal we discard
        # the whole move sequuence ... should be very rare
        if len(fens) == 0:
            continue
            
        b = [chess_jm.processFen(f) for f in fens]
        chess_jm.insertMoves(cur, d, b)
        #gameid += 1
    conn.commit()

#conn.rollback()
#conn.close()
conn.commit()    
conn.close()
