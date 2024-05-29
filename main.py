import logging
import argparse
import os
from typing import List

from bot.bot import Twitchy

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


def main():
    env_var: str = os.getenv('TWITCH_BOT')
    if env_var:
        params: List[str] = env_var.split(',')
        if len(params) != 6:
            raise ValueError("TWITCH_BOT environment variable must contain 6 comma-separated values")

        username, channel, bot_name, oauth_token, client_id, client_secret = params
        logger.info("Using parameters from TWITCH_BOT environment variable")
    else:
        parser = argparse.ArgumentParser(description="Initialize Twitchy with command-line arguments.")
        parser.add_argument('username', type=str, help='Twitch username')
        parser.add_argument('channel', type=str, help='Twitch channel')
        parser.add_argument('bot_name', type=str, help='Bot name')
        parser.add_argument('oauth_token', type=str, help='OAuth token for Twitch authentication')
        parser.add_argument('client_id', type=str, help='Client ID for Twitch API')
        parser.add_argument('client_secret', type=str, help='Client secret for Twitch API')

        args: argparse.Namespace = parser.parse_args()
        username, channel, bot_name, oauth_token, client_id, client_secret = (
            args.username,
            args.channel,
            args.bot_name,
            args.oauth_token,
            args.client_id,
            args.client_secret,
        )
        logger.info("Using parameters from command-line arguments")

    logger.info("Starting Twitchy")

    bot: Twitchy = Twitchy(
        username,
        f"#{channel}",
        bot_name,
        oauth_token,
        client_id,
        client_secret,
    )

    logger.info("Twitchy initialized")


if __name__ == "__main__":
    main()
