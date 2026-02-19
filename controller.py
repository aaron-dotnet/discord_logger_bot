import sqlite3 as sql

DB_NAME: str = "simple.db"

def connect_db():
    conn: sql.Connection = sql.connect(DB_NAME)
    conn.commit()
    conn.close()

   
# def validate_tables(table_name: str):
#     conn = sql.connect(DB_NAME)
#     cursor: sql.Cursor = conn.cursor()
#     sql_cmd: str = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
#     cursor.execute(sql_cmd)
    
#     result = cursor.fetchone()
#     if result is not None:
#         conn.close()
#     else:
#         create_tables()
#         conn.close()

#     return True
    

def create_tables():
    cmd: str = "CREATE TABLE users (user_id INTEGER PRIMARY KEY, username TEXT, display_name TEXT, avatar_url TEXT, account_created TEXT, joined_server TEXT, roles TEXT)"
    execute_command(cmd)
    
    # Get message id and associated with user id.
    cmd2: str = "CREATE TABLE messages (message_id INTEGER PRIMARY KEY, user_id INTEGER, content TEXT, date TEXT)"
    execute_command(cmd2)

    # interesting data
    cmd3: str = "CREATE TABLE message_content (message_id INTEGER PRIMARY KEY, content_type TEXT, filtered_content TEXT)"
    execute_command(cmd3)


def insert_discord_user(user_id: int, username: str, display_name: str, avatar_url: str, account_created: str, joined_server: str, roles: list[str]):
    cmd: str = f"""INSERT INTO users VALUES(
    '{user_id}', '{username}', '{display_name}',
    '{avatar_url}', '{account_created}', '{joined_server}',
    '{','.join(roles)}') 
    """
    execute_command(cmd)

def insert_message(message_id: int, user_id: int, content: str, date: str):
    cmd: str = f"""INSERT INTO messages VALUES(
    '{message_id}', '{user_id}', '{content}', '{date}') 
    """
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

def user_exists(user_id: int) -> bool:
    """
    Check if a user exists by user_id (int)
    """
    conn = sql.connect(DB_NAME)
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE user_id = ? LIMIT 1", (user_id,))
       
        return cur.fetchone() is not None
    except Exception as ex:
        print(ex)
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    pass
    #connect_db()
    #validate_tables("users")