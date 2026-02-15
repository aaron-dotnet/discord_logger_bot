import sqlite3 as sql

DB_NAME: str = "simple.db"

def CreateDB():
    conn = sql.connect(DB_NAME)
    conn.commit()
    conn.close()

def CreateTable():
    conn: sql.Connection = sql.connect(DB_NAME)
    cursor: sql.Cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE users (
            name text,
            id integer,
            email integer
        )"""
    )
    conn.commit()
    conn.close()

def InsertRow(name: str, id: int, email: str):
    conn: sql.Connection = sql.connect(DB_NAME)
    cursor: sql.Cursor = conn.cursor()
    
    cmd: str = f"INSERT INTO users VALUES ('{name}', '{id}', '{email}') "
    cursor.execute(cmd)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    CreateDB()
    CreateTable()
    InsertRow("Will Smith", 9923, "will_smith@gmail.com")