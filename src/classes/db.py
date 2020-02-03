import sqlite3


class DBConnectionHandler:
    def __init__(self, db_file):
        try:
            self.con = sqlite3.connect(db_file, check_same_thread=False)
            cursor = self.con.cursor()
            print("Database created and Successfully Connected to SQLite")

            sqlite_select_query = "select sqlite_version();"
            cursor.execute(sqlite_select_query)
            record = cursor.fetchall()
            print("SQLite Database Version is: ", record)

        except sqlite3.Error as error:
            print("Error while connecting to sqlite", error)
            if self.con:
                self.con.close()
                print("The SQLite connection is closed")
        self.cursor = self.con.cursor()

    def execute(self, query):
        result = self.cursor.execute(query)
        return result

    def commit(self):
        self.con.commit()

    def close(self):
        self.con.close()
        print("The SQLite connection is closed")
