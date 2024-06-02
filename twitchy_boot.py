""" Entrypoint for Twitchy """

import argparse
import json
import logging
import os
from json import JSONDecodeError
from typing import List, Dict, Optional

import requests
from requests import Response

from bot import Twitchy
from util.constants import TOKENS_PATH


def _get_new_refresh_token(
    client_id: str, client_secret: str, refresh_token: str
) -> str:
    """
    # TODO Figure out why this doesn't properly refresh the tokens
    Args:
        client_id:
        client_secret:
        refresh_token:

    Returns:

    """
    try:
        headers: Dict[str, str] = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data: str = (
            f"grant_type=refresh_token&refresh_token={refresh_token}"
            f"&client_id={client_id}"
            f"&client_secret={client_secret}"
        )

        response: Response = requests.post(
            "https://id.twitch.tv/oauth2/token", headers=headers, data=data
        )
        with open(TOKENS_PATH, "w") as file:
            file.write(json.dumps(json.loads(response.text), indent=4))
        return response.json().get("refresh_token", "")
    except requests.exceptions.RequestException as e:
        logging.error("Unable to get refresh token: %s", e)
        return ""


def _load_tokens(
    client_id: str, client_secret: str, refresh_token: str
) -> Optional[str]:
    access_token: Optional[str] = None
    try:
        with open(TOKENS_PATH, "r") as file:
            data: Dict[str, str] = json.loads(file.read())

        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token", refresh_token)
    except FileNotFoundError as e:
        logging.error("Error opening %s: %s", TOKENS_PATH, e)
    except JSONDecodeError as e:
        logging.error("Error parsing %s: %s", TOKENS_PATH, e)

    if not access_token:
        access_token = _get_new_refresh_token(client_id, client_secret, refresh_token)
    return access_token


def boot() -> None:
    """
    Twitchy entrypoint
    Returns:
        None
    """
    parser = argparse.ArgumentParser(
        description="Initialize Twitchy with command-line arguments."
    )
    parser.add_argument(
        "--username", type=str, help="Twitch username", default="default_username"
    )
    parser.add_argument(
        "--channel", type=str, help="Twitch channel", default="default_channel"
    )
    parser.add_argument(
        "--bot_name", type=str, help="Bot name", default="default_bot_name"
    )
    parser.add_argument(
        "--oauth_token",
        type=str,
        help="OAuth token for Twitch authentication",
        default="default_oauth_token",
    )
    parser.add_argument(
        "--client_id",
        type=str,
        help="Client ID for Twitch API",
        default="default_client_id",
    )
    parser.add_argument(
        "--client_secret",
        type=str,
        help="Client secret for Twitch API",
        default="default_client_secret",
    )
    parser.add_argument(
        "--refresh_token",
        type=str,
        help="Token for refreshing access token",
        default="default_refresh_token",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args: argparse.Namespace = parser.parse_args()

    # Set logging level
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger: logging.Logger = logging.getLogger()

    env_var: Optional[str] = os.getenv("TWITCH_BOT")
    if env_var:
        params: List[str] = env_var.split(",")
        if len(params) != 7:
            raise ValueError(
                "TWITCH_BOT environment variable must contain 7 comma-separated values"
            )
        #
        (
            username,
            channel,
            bot_name,
            oauth_token,
            client_id,
            client_secret,
            refresh_token,
        ) = params
        logger.info("Using parameters from TWITCH_BOT environment variable")
    else:
        (
            username,
            channel,
            bot_name,
            oauth_token,
            client_id,
            client_secret,
            refresh_token,
        ) = (
            args.username,
            args.channel,
            args.bot_name,
            args.oauth_token,
            args.client_id,
            args.client_secret,
            args.refresh_token,
        )
        logger.info("Using parameters from command-line arguments")

    logger.info("Starting Twitchy")

    new_oauth: Optional[str] = _load_tokens(client_id, client_secret, refresh_token)
    oauth_token = new_oauth if new_oauth else oauth_token

    bot: Twitchy = Twitchy(
        username,
        f"#{channel}",
        bot_name,
        oauth_token,
        client_id,
        client_secret,
    )
    logger.info("Twitchy initialized %s", bot)


if __name__ == "__main__":
    boot()
