import os
from typing import Dict

from data_types.commands import (
    Command,
    on_delay_not_met,
    on_invalid_command,
    on_help_command,
    on_message,
    on_set_vips,
    on_set_mods,
    on_roll,
    on_first_sighting,
    on_who_am_i,
    on_reroll_me,
    on_bonk,
    on_get_bonks,
)

INVALID_COMMAND: Command = Command("ERROR", "", on_invalid_command)
DELAY_NOT_MET_COMMAND: Command = Command("ERROR", "", on_delay_not_met)
HELP_COMMAND: Command = Command("HELP", "", on_help_command)

commands: Dict[str, Command] = {
    "!messages": Command(
        "Returns how many messages a user has sent", "!messages", on_message
    ),
    "!roll": Command("Rolls a die of format #dSides,", "!roll 2d20", on_roll),
    "!first_sighting": Command(
        "Gives the delta from the first time you were seen in chat",
        "!first_sighting",
        on_first_sighting,
    ),
    "!who_am_i": Command("Prints out the user's stat sheet.", "!who_am_i", on_who_am_i),
    "!reroll_me": Command(
        "Rerolls your player stats. ONLY USUABLE ONCE A MONTH",
        "!reroll_me",
        on_reroll_me,
    ),
    "!bonk": Command("Bonks someone!", "!bonk [user]", on_bonk),
    "!bonked?": Command("How many times have you been bonked?", "!bonked?", on_get_bonks),
}

mod_commands: Dict[str, Command] = {
    "!set_vips": Command(
        "Sets user level to VIP.",
        "!set_vips [username1] [username2] ...",
        on_set_vips,
    )
}

owner_commands: Dict[str, Command] = {
    "!set_mods": Command(
        "Sets bot mod level for all provided users.",
        "!set_mods [username1] [username2] ...",
        on_set_mods,
    )
}

mod_commands.update(commands)
owner_commands.update(mod_commands)


def generate_markdown(dictionaries: Dict[str, Dict[str, Command]]):
    os.makedirs("docs", exist_ok=True)
    for dict_name, command_dict in dictionaries.items():
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
