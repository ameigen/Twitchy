""" Handles classes and lookups for the 'RPG' chat metagame """

import dataclasses
import random
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple, List

from data_types.rpg.items import Weapon, Spell, Accessory, Armor, Attack


class Species(str, Enum):
    """
    Enum class for chatter species
    """

    HUMAN = "human"
    ELF = "elf"
    DWARF = "dwarf"
    KOBOLD = "kobold"
    FROG = "frog"
    ORC = "orc"
    GNOME = "gnome"
    TROLL = "troll"
    GOBLIN = "goblin"
    DRAGONBORN = "dragonborn"
    TIEFLING = "tiefling"
    HALFLING = "halfling"
    CENTAUR = "centaur"
    MERFOLK = "merfolk"
    FAIRY = "fairy"
    GIANT = "giant"
    MINOTAUR = "minotaur"
    VAMPIRE = "vampire"
    WEREWOLF = "werewolf"
    LYCAN = "lycan"
    UNDEAD = "undead"
    ANGEL = "angel"
    DEMON = "demon"
    NYMPH = "nymph"
    SATYR = "satyr"
    SPHINX = "sphinx"
    HARPY = "harpy"
    OGRE = "ogre"
    SPRITE = "sprite"
    DJINN = "djinn"
    ELEMENTAL = "elemental"
    LIZARDFOLK = "lizardfolk"
    AASIMAR = "aasimar"
    KENKU = "kenku"
    TABAXI = "tabaxi"
    YUAN_TI = "yuan-ti"


SPECIES_LOOKUP: Dict[Species, Tuple[int, int, int, int, int, int]] = {
    Species.HUMAN: (0, 0, 0, 0, 0, 0),
    Species.ELF: (-1, +2, 0, +1, 0, +1),
    Species.DWARF: (+1, -1, +2, 0, +1, -1),
    Species.KOBOLD: (-1, +1, 0, 0, 0, +2),
    Species.FROG: (0, +2, 0, -1, 0, +1),
    Species.ORC: (+2, 0, +1, -1, 0, -1),
    Species.GNOME: (0, +1, 0, +2, -1, 0),
    Species.TROLL: (+2, -1, +2, 0, 0, -2),
    Species.GOBLIN: (0, +2, 0, +1, -1, 0),
    Species.DRAGONBORN: (+2, 0, +1, 0, +1, -1),
    Species.TIEFLING: (0, +1, 0, +2, 0, -1),
    Species.HALFLING: (0, +2, 0, +1, 0, 0),
    Species.CENTAUR: (+2, 0, +1, 0, +1, -1),
    Species.MERFOLK: (0, +2, 0, +1, -1, 0),
    Species.FAIRY: (-1, +2, 0, +2, 0, 0),
    Species.GIANT: (+3, -1, +2, 0, 0, -2),
    Species.MINOTAUR: (+2, 0, +2, -1, 0, -1),
    Species.VAMPIRE: (0, +2, 0, +1, 0, +1),
    Species.WEREWOLF: (+2, 0, +1, 0, +1, -1),
    Species.LYCAN: (+2, 0, +1, 0, +1, -1),
    Species.UNDEAD: (0, 0, +2, 0, 0, +1),
    Species.ANGEL: (0, +2, 0, +2, 0, 0),
    Species.DEMON: (+2, 0, +1, -1, 0, +1),
    Species.NYMPH: (0, +2, 0, +1, 0, 0),
    Species.SATYR: (0, +2, 0, +1, 0, 0),
    Species.SPHINX: (+2, 0, +1, +1, 0, -1),
    Species.HARPY: (0, +2, 0, +1, 0, 0),
    Species.OGRE: (+3, -1, +2, 0, 0, -2),
    Species.SPRITE: (-1, +2, 0, +1, 0, 0),
    Species.DJINN: (0, +2, 0, +2, 0, 0),
    Species.ELEMENTAL: (0, 0, +2, 0, 0, +1),
    Species.LIZARDFOLK: (+1, 0, +2, 0, +1, -1),
    Species.AASIMAR: (0, +2, 0, +1, 0, +1),
    Species.KENKU: (0, +2, 0, +1, 0, 0),
    Species.TABAXI: (0, +2, 0, +1, 0, 0),
    Species.YUAN_TI: (0, +2, 0, +1, 0, 0),
}


@dataclass
class PlayerStats:
    """
    Holds RPG stats for chatters
    """

    race: Species
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int
    max_health: int
    current_health: int
    max_mana: int
    current_mana: int
    experience: int
    weapon: Weapon = Weapon()
    spell: Spell = Spell()
    armor: Armor = Armor()
    accessories: List[Accessory] = dataclasses.field(default_factory=lambda: [])

    def _calc_health(self) -> int:
        """
        Handles the calculation of current health based off of stats
        Returns:
            int current health
        """

    def _calc_mana(self) -> int:
        """
        Handles the calculation of current mana based off of stats
        Returns:
            int current mana
        """

    def _calc_damage_received(self, damage: int) -> int:
        """
        Handles calculating the damage received based off of currently equipped items.
        Args:
            damage: int damage received

        Returns:
            int normalized damage
        """

    @classmethod
    def new(cls) -> "PlayerStats":
        """
        Creates a new default PlayerStats object with random stats and species
        Returns:
            PlayerStats
        """
        species: Species = random.choice(list(Species))
        player: PlayerStats = PlayerStats(
            species,
            random.randint(8, 18) + SPECIES_LOOKUP[species][0],
            random.randint(8, 18) + SPECIES_LOOKUP[species][1],
            random.randint(8, 18) + SPECIES_LOOKUP[species][2],
            random.randint(8, 18) + SPECIES_LOOKUP[species][3],
            random.randint(8, 18) + SPECIES_LOOKUP[species][4],
            random.randint(8, 18) + SPECIES_LOOKUP[species][5],
            0,
            0,
            0,
            0,
            0,
        )
        player.max_health = 10 + player.constitution
        player.max_mana = 10 + player.intelligence
        player.current_health = player.max_health
        player.current_mana = player.max_mana
        return player

    @classmethod
    def from_dict(cls, val: Dict[str, int]) -> "PlayerStats":
        """
        Deserializes a Dictionary into a PlayerStats objects
        Args:
            val: Dict[str, int] representing the makeup of a PlayerStats object

        Returns:
            PlayerStats
        """
        species: Species = random.choice(list(Species))
        player: PlayerStats = PlayerStats(
            race=val.get("race", species),
            strength=val.get(
                "strength", random.randint(8, 18) + SPECIES_LOOKUP[species][0]
            ),
            dexterity=val.get(
                "dexterity", random.randint(8, 18) + SPECIES_LOOKUP[species][1]
            ),
            constitution=val.get(
                "constitution", random.randint(8, 18) + SPECIES_LOOKUP[species][2]
            ),
            intelligence=val.get(
                "intelligence", random.randint(8, 18) + SPECIES_LOOKUP[species][3]
            ),
            wisdom=val.get(
                "wisdom", random.randint(8, 18) + SPECIES_LOOKUP[species][4]
            ),
            charisma=val.get(
                "charisma", random.randint(8, 18) + SPECIES_LOOKUP[species][5]
            ),
            max_health=0,
            max_mana=0,
            current_mana=0,
            current_health=0,
            experience=val.get("experience", 0),
        )
        player.max_health = val.get("max_health", 10 + player.constitution)
        player.max_mana = val.get("max_mana", 10 + player.intelligence)
        player.current_health = val.get("current_health", player.max_health)
        player.current_mana = val.get("current_mana", player.max_mana)
        return player

    def pretty(self) -> str:
        """
        Creates a pretty print representation of the PlayerStats
        Returns:
            str
        """
        return (
            f"Race:{self.race.title()} "
            f"Health:{self.current_health}/{self.max_health} "
            f"Mana:{self.current_mana}/{self.max_mana} "
            f"Experience:{self.experience} "
            f"STR:{self.strength} "
            f"DEX:{self.dexterity} "
            f"CON:{self.constitution} "
            f"INT:{self.intelligence} "
            f"WIS:{self.wisdom} "
            f"CHA:{self.charisma} "
            f"Weapon:{self.weapon} "
            f"Spell:{self.spell} "
            f"Armor:{self.armor} "
            f"Accessory:{self.accessories} "
        )

    def get_adjusted_stats(self) -> "PlayerStats":
        """
        Returns a temporary snapshot of the Player's current stats modified based off of
        current equipment.
        Returns:
            PlayerStats object
        """
        temp_stats: PlayerStats = self

        temp_stats.strength += temp_stats.armor.stats[0] + sum(
            accessory.stats[0] for accessory in temp_stats.accessories
        )
        temp_stats.dexterity += temp_stats.armor.stats[1] + sum(
            accessory.stats[1] for accessory in temp_stats.accessories
        )
        temp_stats.constitution += temp_stats.armor.stats[2] + sum(
            accessory.stats[2] for accessory in temp_stats.accessories
        )
        temp_stats.intelligence += temp_stats.armor.stats[3] + sum(
            accessory.stats[3] for accessory in temp_stats.accessories
        )
        temp_stats.wisdom += temp_stats.armor.stats[4] + sum(
            accessory.stats[4] for accessory in temp_stats.accessories
        )
        temp_stats.charisma += temp_stats.armor.stats[5] + sum(
            accessory.stats[5] for accessory in temp_stats.accessories
        )

        return temp_stats

    def attack(self) -> Attack:
        """
        Generates an Attack object based off of the character's current Weapon
        Returns:
            Attack object
        """
        damage: int = self.weapon.damage.roll()
        return Attack(
            damage,
            f" attacks with {self.weapon.name} for {damage}! '{self.weapon.description}'",
        )

    def cast(self) -> Attack:
        """
        Generates an Attack object based off of the character's current Spell
        Returns:
            Attack object
        """
        damage: int = self.spell.damage.roll()
        return Attack(
            damage, f" casts {self.spell.name} for {damage}! '{self.spell.description}'"
        )
