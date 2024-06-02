import random

from dataclasses import dataclass
from typing import List


@dataclass
class Dice:
    """
    Wrapper class for a Dice
    """

    sides: int
    count: int

    def __str__(self) -> str:
        return f"{self.count}d{self.sides}"

    def as_list(self) -> List[int]:
        """
        Returns the parameters of the dice as a list
        Returns:
            List[int]
        """
        return [self.sides, self.count]

    def roll(self) -> int:
        """
        Rolls the dice and returns the result.
        Returns:
            int
        """
        return sum(random.randint(1, self.sides) for _ in range(self.count))
