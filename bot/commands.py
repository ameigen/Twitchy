import os
from typing import Dict

from data_types.commands import (
    Command,
    OnInvalidCommand,
    OnDelayNotMetCommand,
    OnWhoAmICommand,
    OnRerollMeCommand,
    OnMessagesCommand,
    OnRollCommand,
    OnVoteCommand,
    OnHelpCommand,
    OnBonkCommand,
    OnGetBonksCommand,
    OnFirstSightingCommand,
    OnCreatePollCommand,
    OnSetVipsCommand,
    OnSetModsCommand,
    OnGetCurrentPoll,
    OnHugCommand,
    OnGetHugsCommand,
    OnGetPointsCommand,
    OnGetCommands,
    OnSetBroadcastCommand,
)

INVALID_COMMAND: Command = OnInvalidCommand("ERROR", "")
DELAY_NOT_MET_COMMAND: Command = OnDelayNotMetCommand("ERROR", "")
HELP_COMMAND: Command = OnHelpCommand("HELP", "")

commands: Dict[str, Command] = {
    "!messages": OnMessagesCommand(
        "Returns how many messages a user has sent", "!messages"
    ),
    "!roll": OnRollCommand("Rolls a die of format #dSides,", "!roll 2d20"),
    "!first_sighting": OnFirstSightingCommand(
        "Gives the delta from the first time you were seen in chat",
        "!first_sighting",
    ),
    "!who_am_i": OnWhoAmICommand("Prints out the user's stat sheet.", "!who_am_i"),
    "!reroll_me": OnRerollMeCommand(
        "Rerolls your player stats. ONLY USUABLE ONCE A MONTH",
        "!reroll_me",
    ),
    "!bonk": OnBonkCommand("Bonks someone!", "!bonk [user]"),
    "!bonked?": OnGetBonksCommand("How many times have you been bonked?", "!bonked?"),
    "!hug": OnHugCommand("Hugs someone!", "!hug [user]"),
    "!hugged?": OnGetHugsCommand("How many times have you been hugged?", "!hugged?"),
    "!points?": OnGetPointsCommand("How many points do you have?", "!points?"),
    "!vote": OnVoteCommand("Votes for a poll choice!", "!vote [choice]"),
    "!current_poll": OnGetCurrentPoll(
        "Gets the current poll information!", "!current_poll"
    ),
    "!commands": OnGetCommands(
        "Returns a link to the current user command sheet!"
        "Try using ![command] help for more info",
        "!commands",
    ),
}

mod_commands: Dict[str, Command] = {
    "!set_vips": OnSetVipsCommand(
        "Sets user level to VIP.",
        "!set_vips [username1],[username2],[username3],...",
    ),
    "!start_poll": OnCreatePollCommand(
        "Starts a new poll",
        "!start_poll [This_is_a_title] [choice1],[choice2],[choice3],... [duration]",
    ),
    "!start_broadcast": OnSetBroadcastCommand(
        "Begins broadcasting a a message after a certain delay",
        "!start_broadcast [message_goes_here] [delay] [repetitions]",
    ),
}

owner_commands: Dict[str, Command] = {
    "!set_mods": OnSetModsCommand(
        "Sets bot mod level for all provided users.",
        "!set_mods [username1],[username2],...",
    )
}

mod_commands.update(commands)
owner_commands.update(mod_commands)


def generate_markdown(our_dicts: Dict[str, Dict[str, Command]]) -> None:
    """
    Creates a series of markdown files detailing the supported commands
    Args:
        our_dicts: Dict of Dicts

    Returns:
        None
    """
    os.makedirs("docs", exist_ok=True)
    for dict_name, command_dict in our_dicts.items():
        filename = f"docs/{dict_name}.md"
        with open(filename, "w") as file:
            file.write(f"# {dict_name.replace('_', ' ').title()}\n\n")
            for command, details in command_dict.items():
                file.write(f"## {command}\n")
                file.write(f"**Description:** {details.description}\n")
                file.write(f"**Usage:** `{details.example}`\n\n")


dictionaries = {
    "commands": commands,
    "mod_commands": mod_commands,
    "owner_commands": owner_commands,
}

generate_markdown(dictionaries)
