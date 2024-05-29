from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from bot.bot import Twitchy, VIP_COMMAND_DELAY, COMMAND_DELAY

import time
import random
import twitch
from dataclasses import dataclass
from typing import Callable, Any, List

from data_types import User
from data_types.user import Level
from .meta_game import PlayerStats

REROLL_DELAY: float = 2.592e+6


@dataclass
class SplitCommand:
    command: str
    args: List[Any]


@dataclass
class Command:
    description: str
    example: str
    command: Callable


def on_invalid_command(
        _bot: Twitchy, message: twitch.chat.Message, *_args: Any, **_kwargs
) -> None:
    message.chat.send(
        f"@{message.user.display_name} that was an invalid command..."
    )


def on_help_command(
        _bot: Twitchy,
        message: twitch.chat.Message,
        command: str,
        help_text: str,
) -> None:
    message.chat.send(
        f"Hey @{message.user.display_name} you can use {command} like this: {help_text}"
    )


def on_delay_not_met(
        _bot: Twitchy,
        message: twitch.chat.Message,
        user_command_delta: float,
        level: Level,
        *_args: Any,
        **_kwargs,
) -> None:
    if level == Level.VIP:
        message.chat.send(
            f"@{message.user.display_name} we knwo you're important but you cannot use a command again that soon!"
            f"Wait {int(VIP_COMMAND_DELAY - user_command_delta)} seconds"
        )
    else:
        message.chat.send(
            f"@{message.user.display_name} you cannot use a command again that soon!"
            f"Wait {int(COMMAND_DELAY - user_command_delta)} seconds"
        )


def on_message(
        bot: Twitchy, message: twitch.chat.Message, *_args: Any, **_kwargs: Any
) -> None:
    message.chat.send(
        f"@{message.user.display_name}, you have sent {bot.stats[message.user.display_name].messages_sent} messages."
    )


def on_set_vips(
        bot: Twitchy, _message: twitch.chat.Message, to_vip: List[str]
) -> None:
    _set_levels(bot, to_vip, Level.VIP)


def on_set_mods(
        bot: Twitchy, _message: twitch.chat.Message, to_mod: List[str]
) -> None:
    _set_levels(bot, to_mod, Level.MOD)


def on_roll(
        _bot: Twitchy, message: twitch.chat.Message, roll_string: List[str]
) -> None:
    unsplit_roll: str = roll_string[0] if roll_string else ""
    try:
        split_roll: List[str] = unsplit_roll.split("d")
        roll_string: str = _roll_dice(int(split_roll[1]), int(split_roll[0]))
        message.chat.send(
            f"@{message.user.display_name} rolled {unsplit_roll} for: {roll_string}"
        )
    except Exception as e:
        message.chat.send(
            f"@{message.user.display_name} sorry that wasn't a valid roll...{unsplit_roll}"
        )


def on_first_sighting(bot: Twitchy, message: twitch.chat.Message, *_, **__) -> None:
    delta: float = time.time() - bot.stats[message.user.display_name].first_sighting
    bot.send(f"@{message.user.display_name} you were first seen {_seconds_to_dhms(delta)} ago! WOW!")


def on_who_am_i(bot: Twitchy, message: twitch.chat.Message, *_, **__) -> None:
    who_am_i: PlayerStats = bot.stats[message.user.display_name].player_stats
    bot.send(f"@{message.user.display_name} {who_am_i.pretty()}")


def on_reroll_me(bot: Twitchy, message: twitch.chat.Message, *_, **__) -> None:
    delta: float = time.time() - bot.stats[message.user.display_name].last_reroll
    if delta > REROLL_DELAY:
        bot.reroll_user_stats(message.user.display_name)
    else:
        bot.send(
            f"@{message.user.display_name} you can't reroll your character yet! You have to wait {_seconds_to_dhms(REROLL_DELAY - delta)}")


def _roll_dice(sides: int, number: int) -> str:
    number = min(number, 15)
    rolls: List[int] = [random.randint(1, sides) for _ in range(number)]
    roll_string: str = "".join(str(roll) + "+" for roll in rolls)
    roll_string = f" = {sum(rolls)}".join(roll_string.rsplit("+", 1))
    return roll_string


def _set_levels(bot: Twitchy, to_list: List[str], level: Level):
    for user in to_list:
        if user not in bot.stats:
            bot.add_user(User(name=user, level=level))
        else:
            bot.set_user_level(user, level)
        bot.send(f"/{level.value} {user}")
        bot.send(f"@{user}, you are recognized as a {level.value}!")
        time.sleep(1)


def _seconds_to_dhms(elapsed: float):
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
