from abc import ABC
from dataclasses import dataclass
from typing import Any, Dict, Tuple

from data_types.rpg.dice import Dice


@dataclass
class Attack:
    """
    Wrapper class for holding an attack's damage and description
    """

    damage: int
    message: str


@dataclass
class AttackItem(ABC):
    """
    Abstract class for items used for attacking.
    """

    name: str = "Fist"
    damage: Dice = Dice(4, 1)
    stat: str = "Strength"
    description: str = "WHAM!"

    @classmethod
    def from_dict(cls, val: Dict[str, Any]) -> "AttackItem":
        """

        Args:
            val:

        Returns:

        """
        return Spell(
            name=val.get("name", cls.name),
            damage=Dice(*val.get("dice", cls.damage.as_list())),
            stat=val.get("stat", cls.stat),
            description=val.get("description", cls.stat),
        )

    def to_dict(self) -> Dict:
        """

        Returns:

        """
        return {
            "name": self.name,
            "dice": [self.damage.sides, self.damage.count],
            "stat": self.stat,
        }


@dataclass
class StatItem(ABC):
    """
    Abstract base class for items that affect stats
    """

    name: str = "None"
    stats: Tuple[int, int, int, int, int, int] = (0, 0, 0, 0, 0, 0)
    armor: int = 0

    @classmethod
    def from_dict(cls, val: Dict[str, Any]) -> "StatItem":
        """

        Args:
            val:

        Returns:

        """
        return StatItem(
            name=val.get("name", cls.name),
            stats=tuple(val.get("stats", cls.stats)),
            armor=val.get("armor", cls.armor),
        )

    def to_dict(self) -> Dict:
        """

        Returns:

        """
        return {"name": self.name, "stats": list(self.stats), "armor": self.armor}


@dataclass
class Spell(AttackItem):
    """
    Class representing a Spell AttackItem
    """

    name: str = "None"
    damage: Dice = Dice(0, 0)
    stat: str = "Intelligence"
    description: str = "Fizzle..."


@dataclass
class Weapon(AttackItem):
    """
    Wrapper class for Weapon AttackItem
    """


@dataclass
class Armor(StatItem):
    """
    Wrapper class for Armor StatItem
    """


@dataclass
class Accessory(StatItem):
    """
    Wrapper class for Accessory StatItem
    """
