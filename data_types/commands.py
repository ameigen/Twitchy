"""Holds definitions for commands"""

from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Any, List, Optional

import twitch

from data_types.rpg.meta_game import PlayerStats
from .events import PollBotEvent
from .user import Level
from .user import User

if TYPE_CHECKING:
    from bot.bot import Twitchy


@dataclass
class Command:
    """
    Data class holding components of a user command.
    """

    description: str
    example: str
    command: Callable


def on_invalid_command(
    _bot: Twitchy, message: twitch.chat.Message, *_args: Any, **_kwargs
) -> None:
    """
    Fallback function if the command definition is not found.
    Args:
        _bot: Ignored
        message: Message class for the chat message
        *_args: Ignored
        **_kwargs: Ignored

    Returns:
        None

    """
    message.chat.send(f"@{message.user.display_name} that was an invalid command...")


def on_help_command(
    _bot: Twitchy,
    message: twitch.chat.Message,
    command: Command,
) -> None:
    """
    Sends a chat message '@ing' the user with the help text of the requested command
    Args:
        _bot: Unused
        message: Message class for the chat message
        command: Command for the help text to be created from
    Returns:
        None
    """
    message.chat.send(
        f"Hey @{message.user.display_name} here's your help:"
        f" {command.description} - {command.example}"
    )


def on_delay_not_met(
    _bot: Twitchy,
    message: twitch.chat.Message,
    user_command_delta: float,
    level: Level,
    *_args: Any,
    **_kwargs,
) -> None:
    """

    Args:
        _bot:
        message:
        user_command_delta:
        level:
        *_args:
        **_kwargs:

    Returns:

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


def on_message(
    bot: Twitchy, message: twitch.chat.Message, *_args: Any, **_kwargs: Any
) -> None:
    """

    Args:
        bot:
        message:
        *_args:
        **_kwargs:

    Returns:

    """
    message.chat.send(
        f"@{message.user.display_name}, you have sent "
        f"{bot.stats[message.user.display_name].messages_sent} messages."
    )


def on_set_vips(bot: Twitchy, _message: twitch.chat.Message, to_vip: List[str]) -> None:
    """

    Args:
        bot:
        _message:
        to_vip:

    Returns:

    """
    _set_levels(bot, to_vip, Level.VIP)


def on_set_mods(bot: Twitchy, _message: twitch.chat.Message, to_mod: List[str]) -> None:
    """

    Args:
        bot:
        _message:
        to_mod:

    Returns:

    """
    _set_levels(bot, to_mod, Level.MOD)


def on_roll(
    _bot: Twitchy, message: twitch.chat.Message, roll_string: List[str]
) -> None:
    """

    Args:
        _bot:
        message:
        roll_string:

    Returns:

    """
    unsplit_roll: str = roll_string[0] if roll_string else ""
    try:
        split_roll: List[str] = unsplit_roll.split("d")
        roll_string: str = _roll_dice(int(split_roll[1]), int(split_roll[0]))
        message.chat.send(
            f"@{message.user.display_name} rolled {unsplit_roll} for: {roll_string}"
        )
    except IndexError as error:
        logging.error("Error parsing roll command: %s", error)
        message.chat.send(
            f"@{message.user.display_name} sorry that wasn't"
            f" a valid roll...{unsplit_roll}"
        )
    except TypeError as error:
        logging.error("Error parsing roll command: %s", error)
        message.chat.send(
            f"@{message.user.display_name} sorry that wasn't"
            f" a valid roll...{unsplit_roll}"
        )


def on_first_sighting(bot: Twitchy, message: twitch.chat.Message, *_, **__) -> None:
    """

    Args:
        bot:
        message:
        *_:
        **__:

    Returns:

    """
    delta: float = time.time() - bot.stats[message.user.display_name].first_sighting
    bot.send(
        f"@{message.user.display_name} you were first seen"
        f" {_seconds_to_dhms(delta)} ago! WOW!"
    )


def on_who_am_i(bot: Twitchy, message: twitch.chat.Message, *_, **__) -> None:
    """

    Args:
        bot:
        message:
        *_:
        **__:

    Returns:

    """
    who_am_i: PlayerStats = bot.stats[message.user.display_name].player_stats
    bot.send(f"@{message.user.display_name} {who_am_i.pretty()}")


def on_reroll_me(bot: Twitchy, message: twitch.chat.Message, *_, **__) -> None:
    """

    Args:
        bot:
        message:
        *_:
        **__:

    Returns:

    """
    delta: float = time.time() - bot.stats[message.user.display_name].last_reroll
    if delta > User.REROLL_DELAY:
        bot.reroll_user_stats(message.user.display_name)
    else:
        bot.send(
            f"@{message.user.display_name} you can't reroll your character "
            f"yet! You have to wait {_seconds_to_dhms(User.REROLL_DELAY - delta)}"
        )


def on_bonk(
    bot: Twitchy, message: twitch.chat.Message, target: List[str], *_, **__
) -> None:
    """

    Args:
        bot:
        message:
        target:
        *_:
        **__:

    Returns:

    """
    target: str = target[0]
    if target in bot.stats:
        bot.stats[target].bonks += 1
        bot.send(f"@{target} 🔨 was bonked by {message.user.display_name}!")
    else:
        bot.send(
            f"Sorry {message.user.display_name} @{target} either doesn't exist "
            f"or hasn't chatted...they should fix that."
        )


def on_get_bonks(bot: Twitchy, message: twitch.chat.Message, *_, **__) -> None:
    """

    Args:
        bot:
        message:
        *_:
        **__:

    Returns:

    """
    bot.send(
        f"@{message.user.display_name} has been bonked "
        f"🔨{bot.stats[message.user.display_name].bonks}🔨 times!"
    )


def on_create_poll(
    bot: Twitchy, _message: twitch.chat.Message, args: List[str], *_, **__
) -> None:
    """

    Args:
        bot:
        _message:
        args:
        *_:
        **__:

    Returns:

    """
    if len(args) >= 3:
        try:
            poll_name: str = args[0].replace("_", " ").title()
            poll_choices: List[str] = args[1:-1]
            poll_duration: int = int(args[-1])
            poll: PollBotEvent = PollBotEvent(
                bot, poll_name, poll_choices, poll_duration
            )
            bot.add_poll(poll)
        except IndexError as e:
            logging.error("Error creating poll event %s", e)
    else:
        bot.send("You might want to try making that poll again...")


def on_vote(
    bot: Twitchy, message: twitch.chat.Message, args: List[str], *_, **__
) -> None:
    """

    Args:
        bot:
        message:
        args:
        *_:
        **__:

    Returns:

    """
    user: User = bot.stats.get(message.user.display_name)
    delta: float = time.time() - user.last_vote
    if delta > User.VOTE_DELAY:
        bot.update_poll(args[0])
    else:
        bot.send(f"@{message.user.display_name} you already voted!")


def on_current_poll(bot: Twitchy, _message: twitch.chat.Message, *_, **__) -> None:
    """

    Args:
        bot:
        _message:
        *_:
        **__:

    Returns:

    """
    poll_event: Optional[PollBotEvent] = bot.get_current_poll_info()
    if poll_event:
        poll_event.current_status()


def _roll_dice(sides: int, number: int) -> str:
    """

    Args:
        sides:
        number:

    Returns:

    """
    number = min(number, 15)
    rolls: List[int] = [random.randint(1, sides) for _ in range(number)]
    roll_string: str = "".join(str(roll) + "+" for roll in rolls)
    roll_string = f" = {sum(rolls)}".join(roll_string.rsplit("+", 1))
    return roll_string


def _set_levels(bot: Twitchy, to_list: List[str], level: Level):
    """

    Args:
        bot:
        to_list:
        level:

    Returns:

    """
    for user in to_list:
        if user not in bot.stats:
            bot.add_user(User(name=user, level=level))
        else:
            bot.set_user_level(user, level)
        bot.send(f"/{level.value} {user}")
        bot.send(f"@{user}, you are recognized as a {level.value}!")
        time.sleep(1)


def _seconds_to_dhms(elapsed: float):
    """

    Args:
        elapsed:

    Returns:

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
