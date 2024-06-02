import json
import logging
import os
import time
from datetime import timedelta
from threading import Thread, Event, Lock
from typing import Dict, List, Optional, Union

import twitch

from bot.commands import (
    owner_commands,
    INVALID_COMMAND,
    commands,
    DELAY_NOT_MET_COMMAND,
    HELP_COMMAND,
    mod_commands,
)
from data_types import PlayerStats
from data_types import User
from data_types.chatter import Chatter
from data_types.commands import (
    Command,
)
from data_types.events import PollBotEvent, BotEvent
from data_types.user import Level
from util.constants import (
    SPLIT_COMMAND_NAME,
    SPLIT_COMMAND_ARGS,
    WRITE_DELAY_SECONDS,
    STATS_PATH,
)


class Twitchy:
    """
    Core class for the Twitchy bot
    """

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
                bearer_token=oauth,
                cache_duration=timedelta(minutes=30),
            ),
        )
        self._owner: str = owner
        self._stats: Dict[str, User] = {}
        self._bot.subscribe(self._handle_message)
        self._bot_name: str = nickname
        self._events: Dict[str, Union[BotEvent, PollBotEvent]] = {}
        self._current_chatters: List[Chatter] = []

        self._file_writer: Thread = Thread(target=self._file_write_loop)
        self._watch_thread: Thread = Thread(target=self._monitor_loop)
        self._chatter_thread: Thread = Thread(target=self._monitor_chatters)
        self._file_mutex: Lock = Lock()
        self._queue_mutex: Lock = Lock()
        self._chatters_mutex: Lock = Lock()

        self._end_event: Event = Event()

        self._load_stats()
        self._file_writer.start()
        self._watch_thread.start()
        self._chatter_thread.start()

    @property
    def stats(self) -> Dict[str, User]:
        """
        Get the stats dict
        Returns:
            Dict[str, User]
        """
        return self._stats

    @property
    def chatters(self) -> List[Chatter]:
        """
        Gets the current chatters
        Returns:
            List[Chatter]
        """
        return self._current_chatters

    @property
    def chatters_mutex(self) -> Lock:
        """
        Gets the current chatters mutex
        Returns:
            Lock
        """
        return self._chatters_mutex

    def _handle_message(self, message: twitch.chat.Message) -> None:
        """
        Logic for handling any incoming messages. If a user has not been added to the stats
        recording they will be added with default parameters.
        Args:
            message: Message that was received

        Returns:
            None
        """
        username: str = message.user.display_name
        logging.info("Received message: %s", message.text)
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
        """
        Core logic for handling a '!command'
        Args:
            user: User that invoked the command
            message: Message holding the command
            split_command: List[str] of the command type and any subsequent args
            level: Level of the command

        Returns:
            None
        """
        if not split_command:
            return

        user_command_delta: float = time.time() - user.last_command
        command_name: str = split_command[SPLIT_COMMAND_NAME]

        def execute_command(command_to_execute: Command) -> None:
            try:
                if (
                    len(split_command) > 1
                    and HELP_COMMAND.description
                    in split_command[SPLIT_COMMAND_ARGS].upper()
                ):
                    HELP_COMMAND(
                        self,
                        message,
                        command_to_execute,
                    )
                else:
                    command_to_execute(
                        self, message, *split_command[SPLIT_COMMAND_ARGS:]
                    )
            except Exception as e:
                logging.error("Error executing command: %s", e)

        if level == Level.OWNER:
            command: Command = owner_commands.get(command_name, INVALID_COMMAND)
        elif level == Level.MOD:
            command: Command = mod_commands.get(command_name, INVALID_COMMAND)
        else:
            delay: float = (
                User.VIP_COMMAND_DELAY if level == Level.VIP else User.COMMAND_DELAY
            )
            if user_command_delta <= delay:
                DELAY_NOT_MET_COMMAND(self, message, user_command_delta, level)
                return
            command: Command = commands.get(command_name, INVALID_COMMAND)
        execute_command(command)

    def _update_user(self, user: User) -> None:
        """
        Updates a provided User's stats
        Args:
            user: User to be updated

        Returns:
            None
        """
        with self._file_mutex:
            user.last_chat = time.time()
            user.messages_sent += 1
            self._stats[user.name] = user

    def _file_write_loop(self) -> None:
        """
        Function to be run in a thread, writing the current user stats to file after
        a certain sleep period.
        Returns:
            None
        """
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

    def _monitor_loop(self) -> None:
        """
        Function to be run in a thread, monitoring for something to happen.
        Returns:
            None
        """
        while not self._end_event.is_set():
            time.sleep(1)
            with self._queue_mutex:
                to_clear: List[str] = []
                for name, event in self._events.items():
                    event: Optional[BotEvent] = event.finish()
                    if event:
                        to_clear.append(name)
                [self._events.pop(name) for name in to_clear].clear()

    def _monitor_chatters(self) -> None:
        """
        Function to monitor currently active chatters.
        Returns:
            None
        """
        while not self._end_event.is_set():
            with self._chatters_mutex:
                self._get_chatters()
            time.sleep(5)

    def _load_stats(self) -> None:
        """
        Opens 'stats,json' and loads user statistics data
        Returns:
            None
        """
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

    def _get_chatters(self) -> None:
        data: Dict = self._bot.helix.api.get(
            "/chat/chatters",
            params={
                "broadcaster_id": self._bot.helix.user(self._owner).id,
                "moderator_id": self._bot.helix.user(self._bot_name).id,
            },
        )
        self._current_chatters = [Chatter.from_data(user) for user in data["data"]]
        logging.debug("Current chatters: %s", self._current_chatters)

    def add_user(self, user: User) -> None:
        """
        Adds a new user to the stats dict
        Args:
            user: User to be added

        Returns:
            None
        """
        logging.info("Adding user: %s", user.name)
        self._stats[user.name] = user

    def set_user_level(self, username: str, level: Level) -> None:
        """
        Sets a provided user's level to the provided level
        Args:
            username: str user to be changed
            level: Level to be changed to

        Returns:
            None
        """
        if self._stats[username].level not in (Level.MOD, Level.OWNER):
            logging.info("Setting User: %s 's level to %s", username, level)
            self._stats[username].level = level

    def reroll_user_stats(self, username: str):
        """
        Generates a new metagame player profile
        Args:
            username: str name of the user

        Returns:
            None
        """
        logging.info("Rerolling User: %s 's stats", username)
        self._stats[username].player_stats = PlayerStats.new()
        self._stats[username].last_reroll = time.time()

    def send(self, message: str) -> None:
        """
        Sends a provided message to the chat channel
        Args:
            message: str message to be sent

        Returns:
            None
        """
        logging.debug("Sending message: %s", message)
        self._bot.send(message)

    def add_poll(self, event: PollBotEvent) -> None:
        """

        Args:
            event:

        Returns:

        """
        if self.add_event("current_poll", event):
            self.send(f"Created a new poll for: {event.title}")
        else:
            self.send("There is already a poll running!")

    def add_event(self, name: str, event: BotEvent) -> bool:
        """

        Args:
            name (str):
            event (BotEvent):
        Returns:

        """

        with self._queue_mutex:
            try:
                self._events[name] = event
                return True
            except KeyError as e:
                logging.error("Error inserting event: %s", e)
                return False

    def update_poll(self, user: str, choice: str) -> None:
        """

        Args:
            user (str):
            choice (str):

        Returns:

        """
        with self._queue_mutex:
            try:
                self._events["current_poll"].vote(choice)
                self.send(f"Thank you @{user} for voting for {choice}!")
            except KeyError as e:
                self._bot.send(f"{choice} isn't in this poll...")
                logging.error("Error getting current poll: %s", e)

    def get_current_poll_info(self) -> Optional[PollBotEvent]:
        """

        Returns:

        """
        return self._events.get("current_poll")

    def update_user(self, user: User) -> None:
        """
        Updates a user in the stats Dict
        Args:
            user (User): to be updated

        Returns:
            None
        """
        logging.debug("Updating %s", user.name)
        print("pre", self._stats[user.name])
        self._stats.update({user.name: user})
        print("post", self._stats[user.name])
