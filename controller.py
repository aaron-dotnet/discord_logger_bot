import sqlite3 as sql

DB_NAME: str = "simple.db"


def connect_db() -> sql.Connection:
    return sql.connect(DB_NAME)


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
        message_id INTEGER,
        content_type TEXT,
        filtered_content TEXT,
        PRIMARY KEY (message_id, content_type, filtered_content)
    )"""
    execute_command(t_content)

    execute_command(
        "CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id)"
    )
    execute_command(
        "CREATE INDEX IF NOT EXISTS idx_message_content_type ON message_content(content_type)"
    )


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
    with sql.connect(DB_NAME) as conn:
        try:
            cursor: sql.Cursor = conn.cursor()
            if params:
                cursor.execute(sql_cmd, params)
            else:
                cursor.execute(sql_cmd)
            conn.commit()
            return True
        except Exception as ex:
            print(ex)
            conn.rollback()
            return False


if __name__ == "__main__":
    pass
    # connect_db()
    # validate_table("users")
