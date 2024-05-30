import time
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, Any

from data_types.meta_game import PlayerStats


class Level(str, Enum):
    OWNER = "owner"
    MOD = "mod"
    VIP = "vip"
    USER = "user"


@dataclass
class User:
    name: str = "__default__"
    level: Level = Level.USER
    last_chat: float = time.time()
    last_command: float = 0
    messages_sent: int = 0
    first_sighting: int = time.time()
    last_reroll: float = 0
    player_stats: PlayerStats = PlayerStats.new()
    bonks: int = 0

    def to_dict(self) -> Dict:
        data: Dict = asdict(self)
        data.pop("name")
        return {self.name: data}

    @classmethod
    def from_dict(cls, name: str, vals: Dict[str, Any]) -> "User":
        return User(
            name=name,
            level=Level(vals.get("level", "user")),
            last_chat=vals.get("last_chat", time.time()),
            messages_sent=vals.get("messages_sent", 0),
            last_command=vals.get("last_command", time.time()),
            first_sighting=vals.get("first_sighting", time.time()),
            last_reroll=vals.get("last_reroll", 0),
            player_stats=PlayerStats.from_dict(vals.get("player_stats", asdict(PlayerStats.new()))),
            bonks=vals.get("bonks", 0)
        )
