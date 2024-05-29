import logging
import os
import time
import json
import twitch

from datetime import timedelta
from threading import Thread, Event, Lock
from typing import Dict, List

from bot.commands import (
    owner_commands,
    INVALID_COMMAND,
    commands,
    DELAY_NOT_MET_COMMAND,
    HELP_COMMAND,
    mod_commands,
)
from data_types import User
from data_types import PlayerStats
from data_types.user import Level
from data_types.commands import (
    Command,
)
from util.constants import SPLIT_COMMAND_NAME, SPLIT_COMMAND_ARGS, COMMAND_DELAY, VIP_COMMAND_DELAY, \
    WRITE_DELAY_SECONDS, STATS_PATH


class TwitchBot:
    def __init__(
            self,
            owner: str,
            channel: str,
            nickname: str,
            oauth: str,
            client_id: str,
            client_secret: str,
    ) -> None:
        self._bot: twitch.Chat = twitch.Chat(
            channel=channel,
            nickname=nickname,
            oauth=oauth,
            helix=twitch.Helix(
                client_id=client_id,
                client_secret=client_secret,
                use_cache=True,
                cache_duration=timedelta(minutes=30),
            ),
        )
        self._owner: str = owner
        self._stats: Dict[str, User] = {}
        self._bot.subscribe(self._handle_message)

        self._file_writer: Thread = Thread(target=self._file_write_loop)
        self._file_mutex: Lock = Lock()
        self._end_event: Event = Event()

        self._load_stats()
        self._file_writer.start()

    @property
    def stats(self) -> Dict[str, User]:
        return self._stats

    def _handle_message(self, message: twitch.chat.Message) -> None:
        username: str = message.user.display_name

        if username not in self._stats:
            self.add_user(User(username))

        user: User = self._stats[username]
        split_command: List[str] = (
            message.text.split(" ") if message.text.startswith("!") else ""
        )
        if username == self._owner:
            self._handle_command(user, message, split_command, Level.OWNER)
        elif self._stats[username].level == Level.MOD:
            self._handle_command(user, message, split_command, Level.MOD)
        else:
            self._handle_command(user, message, split_command, Level.USER)
        self._update_user(user)

    def _handle_command(
            self,
            user: User,
            message: twitch.chat.Message,
            split_command: List[str],
            level: Level,
    ) -> None:
        if not split_command:
            return

        user_command_delta: float = time.time() - user.last_command
        command_name: str = split_command[SPLIT_COMMAND_NAME]

        def execute_command(command_to_execute: Command) -> None:
            if len(split_command) > 1 and HELP_COMMAND.description in split_command[SPLIT_COMMAND_ARGS].upper():
                HELP_COMMAND.command(
                    self, message, split_command[SPLIT_COMMAND_NAME], command_to_execute.description
                )
            else:
                command_to_execute.command(self, message, split_command[SPLIT_COMMAND_ARGS:])

        if level == Level.OWNER:
            command: Command = owner_commands.get(command_name, INVALID_COMMAND)
        elif level == Level.MOD:
            command: Command = mod_commands.get(command_name, INVALID_COMMAND)
        else:
            delay: float = (
                VIP_COMMAND_DELAY if level == Level.VIP else COMMAND_DELAY
            )
            if user_command_delta <= delay:
                DELAY_NOT_MET_COMMAND.command(
                    self, message, user_command_delta, level
                )
                return
            command: Command = commands.get(command_name, INVALID_COMMAND)

        execute_command(command)

    def _update_user(self, user: User) -> None:
        with self._file_mutex:
            user.last_chat = time.time()
            user.messages_sent += 1
            self._stats[user.name] = user

    def _file_write_loop(self) -> None:
        while not self._end_event.is_set():
            time.sleep(WRITE_DELAY_SECONDS)
            with self._file_mutex:
                with open(STATS_PATH, "w") as file:
                    user_list: List[Dict] = [
                        user.to_dict() for user in self._stats.values()
                    ]
                    data: Dict = {}
                    for user in user_list:
                        key: str = list(user.keys())[0]
                        data[key] = user[key]
                    file.write(json.dumps(data, indent=4))

    def _load_stats(self) -> None:
        stats: Dict[str, User] = {}
        if not os.path.exists(STATS_PATH):
            with open(STATS_PATH, "w+") as file:
                default_user = User(self._owner, Level.OWNER, time.time())
                file.write(json.dumps(default_user.to_dict(), indent=4))

        with open(STATS_PATH, "r+") as file:
            data = json.loads(file.read())
            for key, value in data.items():
                stats[key] = User.from_dict(key, value)

        self._stats = stats

    def add_user(self, user: User) -> None:
        logging.info("Adding user: %s", user.name)
        self._stats[user.name] = user

    def set_user_level(self, username: str, level: Level) -> None:
        if self._stats[username].level != Level.MOD and self._stats[username].level != Level.OWNER:
            logging.info("Setting User: %s 's level to %s", username, level)
            self._stats[username].level = level

    def reroll_user_stats(self, username: str):
        logging.info("Rerolling User: %s 's stats", username)
        self._stats[username].player_stats = PlayerStats.new()
        self._stats[username].last_reroll = time.time()

    def send(self, message: str) -> None:
        logging.info("Sending message: %s", message)
        self._bot.send(message)
