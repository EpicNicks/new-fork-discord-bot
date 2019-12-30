
import random
import operator

from enum import Enum
from functools import reduce

from player_data.player import Player

# TODO: games: BlackJack, Cee-lo, five card draw (Poker)

games = [
    "blackjack",
    "5-card-draw",
    "ceelo"
]

# will manage state with player id to ensure no loss of track of game
# command -casino will pass methods to player's casino instance
class Casino:

    def __init__(self, player_id):
        self.p_id = player_id
        self.active_game = None


    def process_command(self, message, player_list):
        if self.active_game is None:
            game = message.words[1]
            bet = int(message.words[2])
            if game.casefold() == "blackjack".casefold():
                self.active_game = self.BlackJack(bet, message, player_list)
            elif game.casefold() == "ceelo".casefold():
                self.active_game = self.CeeLo(bet, message, player_list)
            elif game.casefold() == "5-card-draw".casefold():
                self.active_game = self.FiveCardDraw(bet, message, player_list)
            return "Started game of {}\nCommands are: {}".format(game, self.active_game.get_commands())
        else:
            return self.active_game.process_command(message, player_list)


    class BlackJack:

        class GameState(Enum):
            LOSE = -1
            NONE = 0
            DRAW = 1
            WIN = 2
            DEALER_BUST = 3
            PLAYER_BUST = 4
            HAS_PLAYED = 10


        def __init__(self, player_bet, message, player_list):
            self.dealer_hand = []
            self.player_hand = []
            self.deck = [(2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4), (10, 16), (11, 4)]
            self.game_state = self.GameState.NONE
            self.player_bet = player_bet
            player_list[message.sender]["coins"] -= self.player_bet


        def get_commands(self):
            return "\n> hit\n> stay\n> rules\n> exit"

        def get_rules(self):
            return "Rules:\n*hit* to add a card to your hand. *stay* to keep your hand.\nIf the total value of your hand is higher than the " \
                   "dealer's without exceeding 21, you win! If the total value of the dealer's hand higher than your without exceeding 21, you lose!"

        # returns int card
        def draw(self):
            index = random.randint(0, len(self.deck) - 1)
            card = self.deck[index][0]
            self.deck[index] = (self.deck[index][0], self.deck[index][1] - 1)
            if self.deck[index][1] == 0:
                self.deck.pop(index)
            return card


        def hit(self):
            self.player_hand.append(self.draw())
            # check if bust
            if self.has_busted(self.player_hand):
                self.game_state = self.GameState.PLAYER_BUST
                return self
            if reduce(operator.add, self.dealer_hand, 0) < 17:
                self.dealer_hand.append(self.draw())
            # check if dealer bust
                if self.has_busted(self.dealer_hand):
                    self.game_state = self.GameState.DEALER_BUST
                    return self
            return self


        def stay(self):
            if reduce(operator.add, self.dealer_hand) < 17:
                self.dealer_hand.append(self.draw())
                if self.has_busted(self.dealer_hand):
                    self.game_state = self.GameState.DEALER_BUST
                    return
            else:
                dealer_val = reduce(operator.add, self.dealer_hand)
                player_val = reduce(operator.add, self.player_hand)
                if player_val > dealer_val:
                    self.game_state = self.GameState.WIN
                elif player_val < dealer_val:
                    self.game_state = self.GameState.LOSE
                else:
                    self.game_state = self.GameState.DRAW
                return self

        # returns bool
        def has_busted(self, card_list):
            if reduce(operator.add, card_list, 0) >= 22:
                if 11 in card_list:
                    card_list.remove(11)
                    card_list.append(1)
                    return False
                return True
            return False


        def handle_result(self, message, player_list):
            player_total = reduce(operator.add, self.player_hand, 0)
            dealer_total = reduce(operator.add, self.dealer_hand, 0)
            game_status = "your hand: {}={}\ndealer's hand: {}={}".format(self.player_hand, player_total, self.dealer_hand, dealer_total)
            if self.game_state == self.GameState.WIN:
                result = self.apply_and_reset(message, player_list)
                return "{}\n\nHigher Value! You Won!\n".format(game_status) + result
            if self.game_state == self.GameState.DEALER_BUST:
                result = self.apply_and_reset(message, player_list)
                return "{}\n\nDealer Bust! You Win!\n".format(game_status) + result
            if self.game_state == self.GameState.PLAYER_BUST:
                result = self.apply_and_reset(message, player_list)
                return "{}\n\nYou Busted! You Lose!\n".format(game_status) + result
            if self.game_state == self.GameState.LOSE:
                result = self.apply_and_reset(message, player_list)
                return "{}\n\nLower Value! You Lose!\n".format(game_status) + result
            if self.game_state == self.GameState.DRAW:
                result = self.apply_and_reset(message, player_list)
                return "{}\n\nDRAW. EQUAL VALUE\n".format(game_status) + result
            else:
                return game_status

        def process_command(self, message, player_list):
            command = message.words[0]
            # replay check
            if self.game_state == self.GameState.HAS_PLAYED:
                self.game_state = self.GameState.NONE
                player_list[message.sender]["coins"] -= self.player_bet
            if message.words[0].casefold() == "hit".casefold():
                self.hit()
                return self.handle_result(message, player_list)
            elif message.words[0].casefold() == "stay".casefold():
                self.stay()
                return self.handle_result(message, player_list)
            if message.words[0].casefold() == "rules".casefold():
                return self.get_rules() + "\n\nCommands are:\n" + self.get_commands()
            else:
                return "Invalid command. Options are:{}".format(self.get_commands())

        def apply_and_reset(self, message, player_list):
            player = player_list[message.sender]
            if self.game_state == self.GameState.LOSE or self.game_state == self.GameState.PLAYER_BUST:
                res = "lost"
                gain_loss = self.player_bet
            elif self.game_state == self.GameState.DRAW:
                # restore player's coins that were bet
                res = "gained"
                gain_loss = 0
                player["coins"] += self.player_bet
            elif self.game_state == self.GameState.WIN or self.game_state == self.GameState.DEALER_BUST:
                res = "gained"
                gain_loss = self.player_bet
                player["coins"] += 2 * self.player_bet
            player_list.serialize_players()
            return "Coins {}: {}\n{}".format(res, gain_loss, self.reset())

        def reset(self):
            result = "exit or replay with same bet (hit/pass to keep playing with new hand)"
            self.dealer_hand = []
            self.player_hand = []
            self.deck = [(1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4), (10, 16)]
            self.game_state = self.GameState.HAS_PLAYED
            return result




    class FiveCardDraw:

        suits = ["\♦", "\♥", "\♣", "\♠"]
        cards = [
            ("2", 2), ("3", 3), ("4", 4), ("5", 5), ("6", 6), ("7", 7), ("8", 8), ("9", 9), ("10", 10),
            ("J", 11), ("Q", 12), ("K", 13), ("A", 14)
        ]

        class GameState(Enum):
            NONE = 0
            DEALT = 1

        def __init__(self, bet, message, player_list):
            self.game_state = self.GameState.NONE
            self.hand = []
            self.deck_base = [(card[0], suit) for card in self.cards for suit in self.suits]
            self.deck = self.deck_base.copy()
            random.shuffle(self.deck)

        def get_commands(self):
            if self.game_state == self.GameState.NONE:
                return "\n> deal\n" \
                       "> exit\n"
            elif self.game_state == self.GameState.DEALT:
                return "\n> bet <amount>\n" \
                       "> toss <cards by position in hand> ([1-5] separated by commas) ex. toss 1,2,5\n" \
                       "> keep\n" \
                       "> exit\n"
        def get_rules(self):
            pass

        def draw(self):
            return self.deck.pop(0)

        def hand_to_string(self):
            return " ".join("["+card[0]+card[1]+"]" for card in self.hand)

        def process_command(self, message, player_list):
            command_result = ""
            command = message.words[0]
            if command.casefold() == "deal".casefold():
                self.game_state = self.GameState.DEALT
                for i in range(5):
                    self.hand.append(self.draw())
                return "Your hand: " + self.hand_to_string() + self.get_commands()
            elif command.casefold() == "bet".casefold() and self.game_state != self.GameState.NONE:
                if len(message.words) != 2:
                    command_result += "Invalid bet. Command must follow the format: bet <amount>"
                elif not message.words[1].isdigit():
                    command_result += "Invalid bet. Bet amount must be a positive integer"
                else:
                    bet = int(message.words[1])
                    # TODO handle bet
            elif command.casefold() == "toss".casefold():
                # Convert numbers and commas to a list
                to_toss = "".join("".join(message.words[1:]).split()).split(",")
                # Validate to_toss
                print(to_toss)
                try:
                    nums = []
                    for num in to_toss:
                        n = int(num)
                        if n > 0 and n <= 5:
                            nums.append(n)
                except:
                    return "Invalid toss. Command must follow the format: toss <1-5> separated by commas"
                # Handle toss
                for num in nums:
                    self.hand[num - 1] = self.draw()
                new_hand = self.hand_to_string()
                return "New hand: {}".format(new_hand) + self.compare_score(message, player_list)
            elif command.casefold() == "keep".casefold():
                new_hand = self.hand_to_string()
                return "Your hand: {}".format(new_hand) + self.compare_score(message, player_list)
            else:
                return "Invalid command. Commands are: {}".format(self.get_commands())

        def compare_score(self, message, player_list):
            # Handle dealer random hand and check score
            return ""


    class CeeLo:

        class GameState(Enum):
            NONE = 2
            DRAW = 0
            WIN = 1
            LOSS = -1

        def __init__(self, bet, message, player_list):
            self.game_state = self.GameState.NONE
            self.player_bet = bet

        def get_commands(self):
            return "\n> roll\n> rules\n> exit\n"

        def get_rules(self):
            return "Roll the dice and win or lose based on the result.\n\n" \
                   "[4, 5, 6] = Instant Win\n" \
                   "[1, 2, 3] = Instant Loss\n" \
                   "[doubles + value], roll is value\n" \
                   "[triples], roll is value of die + 6\n" \
                   "[all unique], reroll\n" \
                   "(Player always rolls first)"

        def roll(self):
            p_roll = [random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)]
            result = ""
            while not self.contains_doubles(p_roll):
                result += "You rolled {}, rerolling...\n".format(p_roll)
                p_roll = [random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)]
            result += "You rolled {}\n\n".format(p_roll)
            if p_roll.sort() == [1, 2, 3]:
                self.game_state = self.GameState.LOSS
                return "You rolled {}, instant loss!".format(p_roll)
            if p_roll.sort() == [4, 5, 6]:
                self.game_state = self.GameState.WIN
                return "You rolled {}, instant win!".format(p_roll)
            opponent_roll = [random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)]
            if opponent_roll.sort() == [1, 2, 3]:
                self.game_state = self.GameState.WIN
                return result + "\nOpponent rolled {}.\nThey lose! You win!\n".format(opponent_roll)
            elif opponent_roll.sort() == [4, 5, 6]:
                self.game_state = self.GameState.LOSS
                return result + "\nOpponent rolled {}.\nThey win! You lose!\n".format(opponent_roll)
            while not self.contains_doubles(opponent_roll):
                result += "Opponent rolled {}, rerolling...\n".format(opponent_roll)
                opponent_roll = [random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)]
            result += "Opponent rolled {}\n".format(opponent_roll)
            # compare rolls
            p_value = 0
            if p_roll[0] == p_roll[1] and p_roll[0] == p_roll[2] and p_roll[1] == p_roll[2]:
                p_value = p_roll[0] + 6
            else:
                if p_roll[0] == p_roll[1]:
                    p_value = p_roll[2]
                elif p_roll[0] == p_roll[2]:
                    p_value = p_roll[1]
                elif p_roll[1] == p_roll[2]:
                    p_value = p_roll[0]
            o_value = 0
            if opponent_roll[0] == opponent_roll[1] and opponent_roll[0] == opponent_roll[2] and opponent_roll[1] == opponent_roll[2]:
                o_value = opponent_roll[0] + 6
            else:
                if opponent_roll[0] == opponent_roll[1]:
                    o_value = opponent_roll[2]
                elif opponent_roll[0] == opponent_roll[2]:
                    o_value = opponent_roll[1]
                elif opponent_roll[1] == opponent_roll[2]:
                    o_value = opponent_roll[0]
            if p_value > o_value:
                result += "You win!\n"
                self.game_state = self.GameState.WIN
            elif p_value < o_value:
                result += "You lose!\n"
                self.game_state = self.GameState.LOSS
            else:
                result += "Tie!"
                self.game_state = self.GameState.DRAW
            return result + "Your total value: {}. Opponent's total value: {}\n".format(p_value, o_value)

        def contains_doubles(self, dice):
            return dice[0] == dice[1] or dice[1] == dice[2] or dice[0] == dice[2]

        def process_command(self, message, player_list):
            command = message.words[0]
            if command.casefold() == "roll".casefold():
                result = self.roll()
                player_list[message.sender]["coins"] -= self.player_bet
            elif command.casefold() == "rules".casefold():
                result = self.get_rules()
            else:
                result = "Invalid command. Options are:{}".format(self.get_commands())
            self.handle_state(message, player_list)
            return result + "\nCommands are: {}(roll to replay with same bet)\n\n" \
                            "old bet: {} coins".format(self.get_commands(), self.player_bet)

        def handle_state(self, message, player_list):
            if self.game_state == self.GameState.LOSS:
                pass
            elif self.game_state == self.GameState.DRAW:
                player_list[message.sender]["coins"] += self.player_bet
            elif self.game_state == self.GameState.WIN:
                player_list[message.sender]["coins"] += self.player_bet
            player_list.serialize_players()
