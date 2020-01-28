import discord

from player_data.players import Players, Player
from player_data.player_state import PlayerState
from items.shop import Shop
from items.casinos import Casinos
from commands.command import Command
from commands.command_functions import *
# example perms
# https://discordapp.com/api/oauth2/authorize?client_id=654176688577445898&permissions=322624&scope=bot

with open("token.txt", "r") as f:
    token = f.read()

if token == None:
    raise Exception("token not found")

client = discord.Client()

player_list = Players(client=client)
casinos = Casinos()
shop = Shop()


class Message:
    def __init__(self, message, sender, client):
        self.message = message
        self.content = message.content
        self.words = self.content.split()
        self.sender = sender
        self.client = client

# setup
@client.event
async def on_message(message):
    print(message.content, message.author.id)
    if message.author.bot:
        return
    # check commands
    m = Message(message, str(message.author.id), client)
    command = None

    #0 check general commands
    #1 check if player is registered
    #2 check which state the player is in [none, casino, future_states]
    #3 handle input based on state

    #0 general commands
    if m.sender in player_list:
        p = player_list[m.sender]
        state = casinos.get_casino(m) is None
        if state == True:
            for com in general_commands:
                if m.words[0] == com.title or m.words[0] in com.aliases:
                    result = com.execute(message=m)
                    while len(result) > 2000:
                        await message.channel.send(result[0:2000])
                        result = result[2000:]
                    await message.channel.send(result)
                    return
            for com in registered_commands:
                if m.words[0] == com.title or m.words[0] in com.aliases:
                    result = com.execute(message=m)
                    while len(result) > 2000:
                        await message.channel.send(result[0:2000])
                        result = result[2000:]
                    await message.channel.send(result)
        elif state == False:
            # accept all input
            casino_result = casinos.handle_message(m, player_list)
            while len(casino_result) > 2000:
                await message.channel.send(casino_result[0:2000])
                casino_result = casino_result[2000:]
            await message.channel.send(casino_result)

    else: # restrict non-members to general commands
        for com in general_commands:
            if m.words[0] == com.title or m.words[0] in com.aliases:
                result = com.execute(message=m)
                await message.channel.send(result)
                return
        for com in registered_commands:
            if m.words[0] == com.title or m.words[0] in com.aliases:
                to_send = "must be registered to use command: **{}**, please register with command **-reg**".format(com.title)
                await message.channel.send(to_send)
                return


general_commands = [
    Command("<@!654176688577445898>", ["-howdy"], greet),
    Command("-commands", ["-c", "-com"], pretty_print_commands),
    Command("-help", ["-h", "-halp"], help_dialog),
    Command("-register", ["-reg"], player_list.register_player)
]

registered_commands = [
    Command("-shop", ["-s", "-buy"], shop.buy, [player_list]),
    Command("-give", ["-gift"], gift, [player_list]),
    Command("-players", ["-p"], player_list.to_string),
    Command("-dev-gift", [], dev_gift, [player_list]),
    Command("-inventory", ["-i", "-status", "-s", "-profile"], player_list.get_status),
    Command("-casino", ["-gamble"], casinos.handle_message, [player_list]),
    Command("-description", ["-descr", "-desc"], get_description)
]
# need to do here because can't reference before instantiation
general_commands[1].params = [[general_commands, registered_commands]]

client.run(token)
