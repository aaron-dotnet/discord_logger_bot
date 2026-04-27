import sqlite3 as sql

DB_NAME: str = "simple.db"


def connect_db() -> sql.Connection | None:
    conn: sql.Connection = sql.connect(DB_NAME)
    conn.close()
    return None


def create_tables():
    t_users: str = """CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        display_name TEXT,
        avatar_url TEXT,
        account_created TEXT,
        joined_server TEXT,
        roles TEXT
    )"""
    execute_command(t_users)

    t_messages: str = """CREATE TABLE IF NOT EXISTS messages (
        message_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        content TEXT,
        date TEXT
    )"""
    execute_command(t_messages)

    t_content: str = """CREATE TABLE IF NOT EXISTS message_content (
        message_id INTEGER PRIMARY KEY,
        content_type TEXT,
        filtered_content TEXT
    )"""
    execute_command(t_content)


def insert_discord_user(
    user_id: int,
    username: str,
    display_name: str,
    avatar_url: str,
    account_created: str,
    joined_server: str,
    roles: list[str],
):
    cmd: str = """INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?, ?, ?, ?)"""
    roles_str: str = ",".join(roles)
    execute_command(
        cmd,
        (
            user_id,
            username,
            display_name,
            avatar_url,
            account_created,
            joined_server,
            roles_str,
        ),
    )


def insert_message(message_id: int, user_id: int, content: str, date: str):
    cmd: str = "INSERT OR IGNORE INTO messages VALUES (?, ?, ?, ?)"
    execute_command(cmd, (message_id, user_id, content, date))


def insert_filtered_content(message_id: int, content_type: str, filtered_content: str):
    cmd: str = "INSERT OR IGNORE INTO message_content VALUES (?, ?, ?)"
    execute_command(cmd, (message_id, content_type, filtered_content))


def execute_command(sql_cmd: str, params: tuple = ()) -> bool:
    conn: sql.Connection = None  # type:ignore
    try:
        conn = sql.connect(DB_NAME)
        cursor: sql.Cursor = conn.cursor()
        if params:
            cursor.execute(sql_cmd, params)
        else:
            cursor.execute(sql_cmd)

        conn.commit()
        return True
    except Exception as ex:
        print(ex)
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def user_exists(user_id: int) -> bool:
    """
    Check if a user exists by user_id (int)
    """
    conn: sql.Connection = None  # type:ignore
    conn = sql.connect(DB_NAME)
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE user_id = ? LIMIT 1", (user_id,))

        return cur.fetchone() is not None
    except Exception as ex:
        print(ex)
        return False
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    pass
    # connect_db()
    # validate_table("users")
