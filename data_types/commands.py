"""Holds definitions for commands"""

from __future__ import annotations

import logging
import random
import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, List, Optional, Tuple

import twitch

from data_types.rpg.meta_game import PlayerStats
from .events import PollBotEvent
from .user import Level
from .user import User

if TYPE_CHECKING:
    from bot.bot import Twitchy


class Command(ABC):
    """
    Class holding components of a user command.

    Attributes:
        description (str): Description of the command.
        example (str): Example usage of the command.
    """

    def __init__(self, description: str, example: str) -> None:
        """
        Initializes the Command class with a description and an example.

        Args:
            description (str): Description of the command.
            example (str): Example usage of the command.
        """
        self.description: str = description
        self.example: str = example

    def __call__(self, *args: Any) -> None:
        """
        Make Command callable.

        Args:
            *args (Any): Variable arguments.

        Returns:
            None
        """
        logging.debug(
            "Calling Command:%s with args %s", self.__class__.__qualname__, args
        )
        self.execute(*args)

    @abstractmethod
    def execute(self, bot: Twitchy, message: twitch.chat.Message) -> None:
        """
        Abstract method for executing a Command.

        Args:
            bot (Twitchy): Twitchy bot instance.
            message (twitch.chat.Message): Message received as part of the command.

        Returns:
            None
        """


class OnTargetCommand(Command, ABC):
    """
    Class representing an Abstract Command that targets a user to increment some value.
    """

    FORMAT: str = "@{target} was {verb} by @{user}!"
    VERB: str = ""

    @abstractmethod
    def _increment(self, bot: Twitchy, target: str) -> None:
        """
        Increment some value on the user
        Args:
            bot (Twitchy): Twitch bot instance
            target (str): Name of user to be incremented
        Returns:
            None
        """

    def execute(
        self, bot: Twitchy, message: twitch.chat.Message, target: str = ""
    ) -> None:
        """
        Executes the target command
        Args:
            bot (Twitchy): Twitchy bot instance
            message (twitch.chat.Message): Message received as part of the command
            target (str): user to target

        Returns:
            None
        """
        if target in bot.stats:
            self._increment(bot, target)
            bot.send(
                self.FORMAT.format(
                    target=target, user=message.user.display_name, verb=self.VERB
                )
            )
        else:
            bot.send(
                f"Sorry {message.user.display_name} @{target} either doesn't exist "
                f"or hasn't chatted...they should fix that."
            )


class OnGetCountCommand(Command, ABC):
    """
    Class representing an Abstract Command that gets a count for a user.
    """

    FORMAT: str = "@{user} {description} {count} {post}"
    DESCRIPTION: str = ""
    POST: str = "times!"

    @abstractmethod
    def _get(self, bot: Twitchy, user: str) -> Any:
        """
        Gets a value from the User
        Args:
            bot (Twitchy): Twitchy bot instance
            user (str): Invoker
        Returns:
            Any
        """

    def execute(self, bot: Twitchy, message: twitch.chat.Message) -> None:
        """
        Executes the get command response.

        Args:
            bot (Twitchy): Twitchy bot instance.
            message (twitch.chat.Message): Message received as part of the command.

        Returns:
            None
        """
        bot.send(
            self.FORMAT.format(
                user=message.user.display_name,
                description=self.DESCRIPTION,
                count=self._get(bot, message.user.display_name),
                post=self.POST,
            )
        )


class OnInvalidCommand(Command):
    """
    Class representing a default Command for if a non-supported Command is called
    """

    def execute(self, bot: Twitchy, message: twitch.chat.Message) -> None:
        """
        Executes the invalid command response.

        Args:
            bot (Twitchy): Twitchy bot instance.
            message (twitch.chat.Message): Message received as part of the command.

        Returns:
            None
        """
        message.chat.send(
            f"@{message.user.display_name} that was an invalid command..."
        )


class OnHelpCommand(Command):
    """
    Class used when a Command definition is requested
    """

    def execute(
        self, bot: Twitchy, message: twitch.chat.Message, command: Command = None
    ) -> None:
        """
        Executes the help command response.

        Args:
            bot (Twitchy): Twitchy bot instance.
            message (twitch.chat.Message): Message received as part of the command.
            command (Command, optional): Command instance to provide help for.

        Returns:
            None
        """
        message.chat.send(
            f"Hey @{message.user.display_name} here's your help:"
            f" {command.description} - {command.example}"
        )


class OnDelayNotMetCommand(Command):
    """
    Class representing a fallback command for if a user invokes a command too soon.
    """

    def execute(
        self,
        bot: Twitchy,
        message: twitch.chat.Message,
        user_command_delta: float = 0,
        level: Level = Level.USER,
    ) -> None:
        """
        Executes the response when a command delay is not met.

        Args:
            bot (Twitchy): Twitchy bot instance.
            message (twitch.chat.Message): Message received as part of the command.
            user_command_delta (float, optional): Time difference since the last command.
            level (Level, optional): User level.

        Returns:
            None
        """
        if level == Level.VIP:
            message.chat.send(
                f"@{message.user.display_name} we know you're important but you"
                f" cannot use a command again that soon!"
                f"Wait {int(User.VIP_COMMAND_DELAY - user_command_delta)} seconds"
            )
        else:
            message.chat.send(
                f"@{message.user.display_name} you cannot use a command again that soon!"
                f"Wait {int(User.COMMAND_DELAY - user_command_delta)} seconds"
            )


class OnMessagesCommand(Command):
    """
    Class representing a Command which returns the number of messages a user has sent
    in the chat.
    """

    def execute(self, bot: Twitchy, message: twitch.chat.Message) -> None:
        """
        Executes the messages command response.

        Args:
            bot (Twitchy): Twitchy bot instance.
            message (twitch.chat.Message): Message received as part of the command.

        Returns:
            None
        """
        message.chat.send(
            f"@{message.user.display_name}, you have sent "
            f"{bot.stats[message.user.display_name].messages_sent} messages."
        )


class OnSetVipsCommand(Command):
    """
    Class representing a Command that sets a list of users to VIP status
    """

    def execute(self, bot: Twitchy, message: twitch.chat.Message, *to_vip: Any) -> None:
        """
        Executes the set VIPs command response.

        Args:
            bot (Twitchy): Twitchy bot instance.
            message (twitch.chat.Message): Message received as part of the command.
            *to_vip (Any): Users to set as VIP.

        Returns:
            None
        """
        _set_levels(bot, to_vip, Level.VIP)


class OnSetModsCommand(Command):
    """
    Class representing a Command that sets a list of users to MOD staus
    """

    def execute(self, bot: Twitchy, message: twitch.chat.Message, *to_mod: Any) -> None:
        """
        Executes the set moderators command response.

        Args:
            bot (Twitchy): Twitchy bot instance.
            message (twitch.chat.Message): Message received as part of the command.
            *to_mod (Any): Users to set as moderators.

        Returns:
            None
        """
        to_mod = [] if not to_mod else to_mod
        _set_levels(bot, to_mod, Level.MOD)


class OnRollCommand(Command):
    """
    Class that represents a Command that rolls n d[sides] dice.
    """

    def execute(
        self, bot: Twitchy, message: twitch.chat.Message, roll_str: str = ""
    ) -> None:
        """
        Executes the roll command response.

        Args:
            bot (Twitchy): Twitchy bot instance.
            message (twitch.chat.Message): Message received as part of the command.
            roll_str (str, optional): Roll string.

        Returns:
            None
        """
        try:
            split_roll: List[str] = roll_str.split("d")
            roll_string: str = _roll_dice(int(split_roll[1]), int(split_roll[0]))
            message.chat.send(
                f"@{message.user.display_name} rolled {roll_string} for: {roll_string}"
            )
        except IndexError as error:
            logging.error("Error parsing roll command: %s", error)
            message.chat.send(
                f"@{message.user.display_name} sorry that wasn't"
                f" a valid roll...{roll_str}"
            )
        except TypeError as error:
            logging.error("Error parsing roll command: %s", error)
            message.chat.send(
                f"@{message.user.display_name} sorry that wasn't"
                f" a valid roll...{roll_str}"
            )


class OnFirstSightingCommand(Command):
    """
    Class representing a Command that returns the first time a User was seen in chat.
    """

    def execute(self, bot: Twitchy, message: twitch.chat.Message) -> None:
        """
        Executes the first sighting command response.

        Args:
            bot (Twitchy): Twitchy bot instance.
            message (twitch.chat.Message): Message received as part of the command.

        Returns:
            None
        """
        delta: float = time.time() - bot.stats[message.user.display_name].first_sighting
        bot.send(
            f"@{message.user.display_name} you were first seen"
            f" {_seconds_to_dhms(delta)} ago! WOW!"
        )


class OnWhoAmICommand(Command):
    """
    Class representing a Command that returns the user's 'meta-game' RPG profile.
    """

    def execute(self, bot: Twitchy, message: twitch.chat.Message) -> None:
        """
        Executes the who am I command response.

        Args:
            bot (Twitchy): Twitchy bot instance.
            message (twitch.chat.Message): Message received as part of the command.

        Returns:
            None
        """
        who_am_i: PlayerStats = bot.stats[message.user.display_name].player_stats
        bot.send(f"@{message.user.display_name} {who_am_i.pretty()}")


class OnRerollMeCommand(Command):
    """
    Class representing a Command that re-rolls a user's 'meta-game' RPG profile.
    """

    def execute(self, bot: Twitchy, message: twitch.chat.Message) -> None:
        """
        Executes the reroll me command response.

        Args:
            bot (Twitchy): Twitchy bot instance.
            message (twitch.chat.Message): Message received as part of the command.

        Returns:
            None
        """
        delta: float = time.time() - bot.stats[message.user.display_name].last_reroll
        if delta > User.REROLL_DELAY:
            bot.reroll_user_stats(message.user.display_name)
        else:
            bot.send(
                f"@{message.user.display_name} you can't reroll your character "
                f"yet! You have to wait {_seconds_to_dhms(User.REROLL_DELAY - delta)}"
            )


class OnBonkCommand(OnTargetCommand):
    """
    Class representing a Command that 'bonks' a target user
    """

    VERB: str = "bonked"

    def _increment(self, bot: Twitchy, target: str) -> None:
        bot.stats[target].bonks += 1


class OnGetBonksCommand(OnGetCountCommand):
    """
    Class representing a Command that gets a user's number of times bonked.
    """

    DESCRIPTION: str = "has been 🔨bonked🔨"
    KEY: str = "bonks"

    def _get(self, bot: Twitchy, user: str) -> int:
        return bot.stats[user].bonks


class OnHugCommand(OnTargetCommand):
    """
    Class representing a Command that 'hugs' a target user
    """

    VERB: str = "hugged"

    def _increment(self, bot: Twitchy, target: str) -> None:
        bot.stats[target].hugs += 1


class OnGetHugsCommand(OnGetCountCommand):
    """
    Class representing a Command that gets a user's number of times hugged.
    """

    DESCRIPTION: str = "has been ❤hugged❤"

    def _get(self, bot: Twitchy, user: str) -> int:
        return bot.stats[user].hugs


class OnGetPointsCommand(OnGetCountCommand):
    """
    Class representing a Command that gets a user's number of points.
    """

    DESCRIPTION: str = "has"
    POST: str = "points!"

    def _get(self, bot: Twitchy, user: str) -> Any:
        return bot.stats[user].points


class OnCreatePollCommand(Command):
    """
    Class representing a Command that creates a PollBotEvent according to some title,
    variable number of choices, and a timeout duration.
    """

    TITLE: int = 0
    DURATION: int = -1

    def execute(self, bot: Twitchy, message: twitch.chat.Message, *args: Any) -> None:
        """
        Executes the create poll command response.

        Args:
            bot (Twitchy): Twitchy bot instance.
            message (twitch.chat.Message): Message received as part of the command.
            *args (Any): Poll title, options, and duration.

        Returns:
            None
        """
        args = [] if not args else args
        if len(args) >= 3:
            try:
                poll_name: str = args[self.TITLE].replace("_", " ").title()
                poll_choices: List[str] = args[self.TITLE : self.DURATION]
                poll_duration: int = int(args[self.DURATION])
                poll: PollBotEvent = PollBotEvent(
                    bot, poll_name, poll_choices, poll_duration
                )
                bot.add_poll(poll)
            except IndexError as e:
                logging.error("Error creating poll event %s", e)
        else:
            bot.send("You might want to try making that poll again...")


class OnVoteCommand(Command):
    """
    Class representing a Command that accepts a user's vote on the current poll
    """

    def execute(
        self, bot: Twitchy, message: twitch.chat.Message, choice: str = ""
    ) -> None:
        """
        Executes the vote command response.

        Args:
            bot (Twitchy): Twitchy bot instance.
            message (twitch.chat.Message): Message received as part of the command.
            choice (str, optional): Poll choice to vote for.

        Returns:
            None
        """
        user: User = bot.stats.get(message.user.display_name)
        delta: float = time.time() - user.last_vote
        if delta > User.VOTE_DELAY:
            bot.update_poll(choice)
        else:
            bot.send(f"@{message.user.display_name} you already voted!")


class OnGetCurrentPoll(Command):
    """
    Class representing a Command that returns the currently active poll
    """

    def execute(self, bot: Twitchy, message: twitch.chat.Message) -> None:
        """
        Executes the get current poll command response.

        Args:
            bot (Twitchy): Twitchy bot instance.
            message (twitch.chat.Message): Message received as part of the command.

        Returns:
            None
        """
        poll_event: Optional[PollBotEvent] = bot.get_current_poll_info()
        if poll_event:
            poll_event.current_status()


def _roll_dice(sides: int, number: int) -> str:
    """
    Rolls a specified number of dice with a specified number of sides.

    Args:
        sides (int): Number of sides on the dice.
        number (int): Number of dice to roll.

    Returns:
        str: String representation of the roll results.
    """
    number = min(number, 15)
    rolls: List[int] = [random.randint(1, sides) for _ in range(number)]
    roll_string: str = "".join(str(roll) + "+" for roll in rolls)
    roll_string = f" = {sum(rolls)}".join(roll_string.rsplit("+", 1))
    return roll_string


def _set_levels(bot: Twitchy, to_list: Tuple[str, ...], level: Level) -> None:
    """
    Sets user levels for a list of users.

    Args:
        bot (Twitchy): Twitchy bot instance.
        to_list (Tuple[str, ...]): List of users to set levels for.
        level (Level): Level to set for the users.

    Returns:
        None
    """
    for user in to_list:
        if user not in bot.stats:
            bot.add_user(User(name=user, level=level))
        else:
            bot.set_user_level(user, level)
        bot.send(f"/{level.value} {user}")
        bot.send(f"@{user}, you are recognized as a {level.value}!")
        time.sleep(1)


def _seconds_to_dhms(elapsed: float) -> str:
    """
    Converts elapsed time in seconds to a human-readable string format
     (days, hours, minutes, seconds).

    Args:
        elapsed (float): Elapsed time in seconds.

    Returns:
        str: Human-readable string representation of the elapsed time.
    """
    seconds_to_minute: int = 60
    seconds_to_hour: int = 60 * seconds_to_minute
    seconds_to_day: int = 24 * seconds_to_hour

    days: float = elapsed // seconds_to_day
    elapsed %= seconds_to_day

    hours: float = elapsed // seconds_to_hour
    elapsed %= seconds_to_hour

    minutes: float = elapsed // seconds_to_minute
    elapsed %= seconds_to_minute

    seconds: float = elapsed

    return f"{days} days, {hours} hours, {minutes} minutes, {int(seconds)} seconds"
