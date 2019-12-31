
from items.casino import Casino
from items import casino
from player_data.player_state import PlayerState

class Casinos:

    def __init__(self):
        self.casinos = []

    # -casino <game-name> optional:description
    def handle_message(self, message, player_list):
        # override
        player = player_list[message.sender]
        if message.words[0].casefold() == "exit".casefold():
            player.state = PlayerState.NONE
            self.exit_casino(message)
            return "<@{}> Exited the casino".format(message.sender)
        if self.get_casino(message) is None:
            words = message.words
            if len(words) == 1:
                return "Welcome to the New Fork Casino!\n" \
                       "Games we have currently:\n" \
                       "blackjack\n" \
                       "5-card-draw <in development>\n" \
                       "ceelo\n\n" \
                       "Type -casino <game-name> <bet-amount> to play that game\n" \
                       "Type -casino <game-name> description for a shot description of that game!"
            elif len(words) == 3:
                if words[1] in casino.games:
                    p_casino = self.add_player(message)
                    return p_casino.process_command(message, player_list)
            else:
                return "Invalid command length: {}".format(len(message.words))
        else:
            result = self.get_casino(message).process_command(message, player_list)
            return result



    def add_player(self, message):
        if self.get_casino(message) is None:
            self.casinos.append(Casino(message.sender))
        return self.get_casino(message)

    def exit_casino(self, message):
        if self.get_casino(message) != None:
            self.casinos.remove(self.get_casino(message))


    def get_casino(self, message):
        for casino in self.casinos:
            if casino.p_id == message.sender:
                return casino
