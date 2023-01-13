#!/usr/bin/env python3

import sqlite3 as sqlite

class Database():
    def __init__(self, dbfile):
        self.conn = sqlite.connect(dbfile)

    def close(self):
        self.conn.close()
        self.conn = None

    def initialise(self):
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE Tags(Tag INT UNIQUE, Name TEXT, Comment TEXT)")
        self.conn.commit()

    def lookup(self, tag):
        cur = self.conn.cursor()
        cur.execute("SELECT Name, Comment FROM Tags WHERE Tag = x'"+tag.hex()+"'")
        res = cur.fetchone()
        if res is None:
            raise ValueError("tag not found")
        return res

    def update(self, tag, name, comment):
        t = (name, comment)
        cur = self.conn.cursor()
        # seems you can't use variables in a where clause...
        cur.execute("UPDATE Tags SET Name=?, Comment=? WHERE Tag=x'"+tag.hex()+"'", t)
        self.conn.commit()
        if cur.rowcount != 1:
            raise Exception("tag update failed - does it exist?")

    def insert(self, tag, name, comment):
        t = (name, comment)
        cur = self.conn.cursor()
        cur.execute("INSERT INTO Tags VALUES(x'"+tag.hex()+"', ?, ?)", t)
        self.conn.commit()
        if cur.rowcount != 1:
            raise Exception("tag insert failed")
