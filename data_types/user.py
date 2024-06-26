import time
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, Any, ClassVar

from data_types.rpg.meta_game import PlayerStats


class Level(str, Enum):
    """
    Enum representing the 'level' of different chatters.
    """

    OWNER = "owner"
    MOD = "mod"
    VIP = "vip"
    USER = "user"


@dataclass
class User:
    """
    Class representing the serializable data of a chat 'User'
    """

    REROLL_DELAY: ClassVar[float] = 2.592e6
    COMMAND_DELAY: ClassVar[int] = 60
    VIP_COMMAND_DELAY: ClassVar[int] = 30
    VOTE_DELAY: ClassVar[int] = 10000000

    name: str = "__default__"
    level: Level = Level.USER
    last_chat: float = time.time()
    last_command: float = 0
    last_vote: float = 0
    last_battle: float = 0
    messages_sent: int = 0
    first_sighting: int = time.time()
    last_reroll: float = 0
    player_stats: PlayerStats = PlayerStats.new()
    bonks: int = 0
    hugs: int = 0
    points: int = 0

    def to_dict(self) -> Dict[str, Dict]:
        """
        Serializes the User into a dictionary
        Returns:
            Dict[str, Any]
        """
        data: Dict = asdict(self)
        data.pop("name")
        return {self.name: data}

    @classmethod
    def from_dict(cls, name: str, vals: Dict[str, Any]) -> "User":
        """
        Deserializes a provided Dict[str, any] into a User object. If a value is not found
        a default value will be created.
        Args:
            name: str name of the user
            vals: Dict[str, Any] of values

        Returns:
            User
        """
        return User(
            name=name,
            level=Level(vals.get("level", "user")),
            last_chat=vals.get("last_chat", time.time()),
            messages_sent=vals.get("messages_sent", 0),
            first_sighting=vals.get("first_sighting", time.time()),
            last_reroll=vals.get("last_reroll", 0),
            hugs=vals.get("hugs", 0),
            player_stats=PlayerStats.from_dict(
                vals.get("player_stats", asdict(PlayerStats.new()))
            ),
            bonks=vals.get("bonks", 0),
            points=vals.get("points", 0),
        )
