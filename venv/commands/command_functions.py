
from random import randint

DEV_ID = "161957055903694849"

def greet(message):
    greetings = ["How do you do?", "What's poppin', Jimbo?"]
    return "{} <@{}>".format(greetings[randint(0, len(greetings) - 1)], message.sender)


def pretty_print_commands(message, command_lists):
    output = "**Commands:**\n"
    for command_list in command_lists:
        for command in command_list:
            output += "\t**{}**, alt: **{}**\n".format(command.title, str(command.aliases)[1:-1] if not not command.aliases else "NO ALIASES")
    return output


def help_dialog(message):
    return "help comes to those who help themselves"


# format: -dev-gift <player-id> item amount
def dev_gift(message, player_list):
    if message.sender != DEV_ID:
        return "must be dev to give dev gift"
    if len(message.words) == 4:
        item = message.words[2]
        amount = int(message.words[3])
        if message.words[1] == "everyone":
            for id, player in player_list.items():
                player.unconditional_add(item, amount)
            result = "everyone was gifted: {} {}(s)!".format(amount, item)
        else:
            p_id = message.words[1][3:-1] if message.words[1][3:-1] in player_list else message.words[1][2:-1]
            player_list[p_id].unconditional_add(item, amount)
            result = "<@{}> was gifted: {} {}(s)".format(p_id, amount, item)
        player_list.serialize_players()
        return result
    return "command must follow format: *-dev-gift <player-id> <item> <amount>*"

def get_description(message):
    pass

# format: -give <player-id> <item-name>
def gift(message, player_list):
    if len(message.words) != 3:
        return "Incorrect format. Format is -give <player-mention> <item-name>"
    p_id, item_name = message.words[1], message.words[2]
