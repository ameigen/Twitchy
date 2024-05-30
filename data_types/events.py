from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Dict, Tuple, Optional

if TYPE_CHECKING:
    from bot.bot import Twitchy


class BotEvent(ABC):
    """
    Abstract base class for Events to be handled by the Twitchy bot
    """

    def __init__(self, bot: Twitchy, timeout: float = 0):
        self._bot: Twitchy = bot
        self._timeout: float = timeout
        self._spawn_time: float = time.time()

    def timed_out(self) -> bool:
        """

        Returns:

        """
        if self._timeout != 0:
            return time.time() - self._spawn_time >= self._timeout
        return False

    @abstractmethod
    def finish(self) -> Optional["BotEvent"]:
        """

        Returns:

        """
        raise NotImplementedError


class PollBotEvent(BotEvent):
    """
    BotEvent for handling PollEvents
    """

    def __init__(
        self, bot: Twitchy, title: str, choices: List[str], timeout: float = 0
    ):
        super().__init__(bot, timeout)
        self._title: str = title
        self._choices: Dict[str, int] = {choice: 0 for choice in choices}

    @property
    def title(self) -> str:
        """

        Returns:

        """
        return self._title

    def vote(self, choice: str) -> None:
        """

        Args:
            choice:

        Returns:

        """
        if choice in self._choices:
            self._choices[choice] += 1

    def current_status(self) -> None:
        """

        Returns:

        """
        status_string: str = ""
        for key, value in self._choices.items():
            status_string += f" {key.title()}:{value}"
        self._bot.send(f"{self._title}: {status_string}")

    def finish(self) -> Optional[BotEvent]:
        """

        Returns:

        """
        if self.timed_out() or not self._timeout:
            winner: Tuple[str, int] = ("", 0)
            for choice, count in self._choices.items():
                winner = (choice, count) if count > winner[1] else winner
            self._bot.send(
                f"{self._title} - {winner[0].title()} has won with {winner[1]} votes!"
            )
            for user in self._bot.stats.values():
                user.last_vote = 0
            return self
        return None
