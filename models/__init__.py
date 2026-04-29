from dataclasses import dataclass
from datetime import datetime


@dataclass
class DiscordUser:
    user_id: int
    user_name: str
    display_names: str
    avatar_url: str
    account_created: datetime
    joined_server: datetime
    roles: list[str]