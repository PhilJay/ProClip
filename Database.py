import sqlite3
import os
from Entry import Entry
from os.path import expanduser


class Database:

    def __init__(self):

        home = expanduser("~")
        directory_path = home + "/Library/Application Support/ProClip"

        #  create the directory if it does not exist
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        self.conn = sqlite3.connect(directory_path + "/proclip.db")
        self.c = self.conn.cursor()

        create = """CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY, 
        alias TEXT,
        content TEXT not null,
        unique (alias)
        )"""
        # Create table
        self.c.execute(create)

        # Save (commit) the changes
        self.conn.commit()

    def push(self, content):
        insert = "INSERT INTO entries (content) VALUES (?)"
        self.c.execute(insert, [content])
        self.conn.commit()
        return self.c.lastrowid

    def push_with_alias(self, alias, content):
        self.c.execute("INSERT INTO entries (alias, content) VALUES (?, ?)", [alias, content])
        self.conn.commit()
        return self.c.lastrowid

    def list(self):
        results = self.c.execute("SELECT * FROM entries").fetchall()
        entries = []

        for result in results:
            entries.append(Entry(result))

        return entries

    def get(self, data):
        result = self.c.execute("SELECT * FROM entries WHERE id=?", [data]).fetchone()
        if result is not None:
            return Entry(result)
        else:
            result = self.c.execute("SELECT * FROM entries WHERE alias=?", [data]).fetchone()
            if result is not None:
                return Entry(result)
        return None

    def get_id(self, identifier):
        result = self.c.execute("SELECT * FROM entries WHERE id=?", [identifier]).fetchone()
        if result is not None:
            return Entry(result)
        else:
            return None

    def get_alias(self, alias):
        result = self.c.execute("SELECT * FROM entries WHERE alias=?", [alias]).fetchone()
        if result is not None:
            return Entry(result)
        else:
            return None

    def pop(self):
        top = self.c.execute("SELECT * FROM entries ORDER BY id ASC LIMIT 1").fetchone()
        self.delete(0)
        return top

    def delete(self, offset):
        rows = self.c.execute("SELECT * FROM entries ORDER BY id ASC").fetchmany(offset + 1)
        length = len(rows)
        if length > offset:
            row = rows[offset]
            self.c.execute("DELETE FROM entries WHERE id=?", [row[0]])
        else:
            row = rows[length - 1]
            self.c.execute("DELETE FROM entries WHERE id=?", [row[0]])
        self.conn.commit()

    def delete_alias(self, alias):
        self.c.execute("DELETE FROM entries WHERE alias=?", [alias])
        self.conn.commit()
        return self.c.lastrowid

    def delete_id(self, id):
        self.c.execute("DELETE FROM entries WHERE id=?", [id])
        self.conn.commit()
        return self.c.lastrowid

    def delete_all(self):
        self.c.execute("DROP TABLE entries")
        self.conn.commit()

    def close(self):
        self.conn.close()
