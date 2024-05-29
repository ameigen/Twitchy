import random
from dataclasses import dataclass
from typing import Dict, Tuple
from enum import Enum


class Species(str, Enum):
    HUMAN = 'human'
    ELF = 'elf'
    DWARF = 'dwarf'
    KOBOLD = 'kobold'
    FROG = 'frog'
    ORC = 'orc'
    GNOME = 'gnome'
    TROLL = 'troll'
    GOBLIN = 'goblin'
    DRAGONBORN = 'dragonborn'
    TIEFLING = 'tiefling'
    HALFLING = 'halfling'
    CENTAUR = 'centaur'
    MERFOLK = 'merfolk'
    FAIRY = 'fairy'
    GIANT = 'giant'
    MINOTAUR = 'minotaur'
    VAMPIRE = 'vampire'
    WEREWOLF = 'werewolf'
    LYCAN = 'lycan'
    UNDEAD = 'undead'
    ANGEL = 'angel'
    DEMON = 'demon'
    NYMPH = 'nymph'
    SATYR = 'satyr'
    SPHINX = 'sphinx'
    HARPY = 'harpy'
    OGRE = 'ogre'
    SPRITE = 'sprite'
    DJINN = 'djinn'
    ELEMENTAL = 'elemental'
    LIZARDFOLK = 'lizardfolk'
    AASIMAR = 'aasimar'
    KENKU = 'kenku'
    TABAXI = 'tabaxi'
    YUAN_TI = 'yuan-ti'


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
    Species.YUAN_TI: (0, +2, 0, +1, 0, 0)
}


@dataclass
class PlayerStats:
    race: Species
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int

    @classmethod
    def new(cls) -> "PlayerStats":
        species: Species = random.choice(list(Species))
        return PlayerStats(
            species,
            random.randint(8, 18) + SPECIES_LOOKUP[species][0],
            random.randint(8, 18) + SPECIES_LOOKUP[species][1],
            random.randint(8, 18) + SPECIES_LOOKUP[species][2],
            random.randint(8, 18) + SPECIES_LOOKUP[species][3],
            random.randint(8, 18) + SPECIES_LOOKUP[species][4],
            random.randint(8, 18) + SPECIES_LOOKUP[species][5],
        )

    @classmethod
    def from_dict(cls, val: Dict[str, int]) -> "PlayerStats":
        species: Species = random.choice(list(Species))
        return PlayerStats(
            race=val.get("race", species),
            strength=val.get("strength", random.randint(8, 18) + SPECIES_LOOKUP[species][0]),
            dexterity=val.get("dexterity", random.randint(8, 18) + SPECIES_LOOKUP[species][1]),
            constitution=val.get("constitution", random.randint(8, 18) + SPECIES_LOOKUP[species][2]),
            intelligence=val.get("intelligence", random.randint(8, 18) + SPECIES_LOOKUP[species][3]),
            wisdom=val.get("wisdom", random.randint(8, 18) + SPECIES_LOOKUP[species][4]),
            charisma=val.get("charisma", random.randint(8, 18) + SPECIES_LOOKUP[species][5]),
        )

    def pretty(self) -> str:
        return f"Race:{self.race.title()} " \
               f"STR:{self.strength} " \
               f"DEX:{self.dexterity} " \
               f"CON:{self.constitution} " \
               f"INT:{self.intelligence} " \
               f"WIS:{self.wisdom} " \
               f"CHA:{self.charisma}"
