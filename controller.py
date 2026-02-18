import sqlite3 as sql

DB_NAME: str = "simple.db"

def connect_db():
    conn: sql.Connection = sql.connect(DB_NAME)
    conn.commit()
    conn.close()

   
def validate_table(table_name: str):
    conn = sql.connect(DB_NAME)
    cursor: sql.Cursor = conn.cursor()
    sql_cmd: str = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
    cursor.execute(sql_cmd)
    
    result = cursor.fetchone()
    if result is not None:
        conn.close()
    else:
        create_users_table()
        conn.close()

    return True
    

def create_users_table():
    cmd: str = "CREATE TABLE users (user_id INTEGER PRIMARY KEY, username TEXT, display_name TEXT, avatar_url TEXT, account_created TEXT, joined_server TEXT, roles TEXT)"
    execute_command(cmd)
    #cmd2: str = "CREATE TABLE messages(user_id INTEGER, content TEXT, datetime TEXT, FOREIGN KEY(user_id) REFERENCES users(user_id))"
    #execute_command(cmd2)


def insert_discord_user(user_id: int, username: str, display_name: str, avatar_url: str, account_created: str, joined_server: str, roles: list[str]):
    cmd: str = f"INSERT INTO users VALUES ('{user_id}', '{username}', '{display_name}', '{avatar_url}', '{account_created}', '{joined_server}', '{','.join(roles)}') "
    execute_command(cmd)



def execute_command(sql_cmd: str) -> bool: 
    try:
        conn: sql.Connection = sql.connect(DB_NAME)
        cursor: sql.Cursor = conn.cursor()
        cursor.execute(sql_cmd)
        
        conn.commit()
        conn.close()
        return True
    except Exception as ex:
        print(ex)
        conn.rollback()
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    connect_db()
    validate_table("users")