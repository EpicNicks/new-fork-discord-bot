import random

from player_data.player import Player

# str: name, int: cost
item_list = [
    ("nothing", 0), #does nothing
    ("fork", 5),
    ("knife", 50),
    ("nuke", 10000),
    ("magic cylinder", 100),
    ("lootbox", 100)
]

class Shop:

    MIN_VAL = 3
    MAX_VAL = 7

    def __init__(self):
        self.items = self.randomize()

    def randomize(self):
        items_to_add = random.sample(item_list, 5)
        random_stock = {}
        for item in items_to_add:
            item_name = item[0]
            item_cost = item[1]
            stock = random.randint(self.MIN_VAL, self.MAX_VAL)
            random_stock[item_name] = (item_cost, stock)
        print(random_stock)
        return random_stock


    def buy(self, message, player_list):
        player = player_list[message.sender]
        # TODO log purchases (change prices based on what is purchased more)?
        m = message.content.split()[1:]
        if len(m) == 0: # list items
            shop_inventory = "**Today's Deals:**\n"
            for i in self.items:
                shop_inventory += "**{}**: price: {}, stock left: {}\n".format(i, self.items[i][0], self.items[i][1])
            return shop_inventory
        if len(m) >= 2:
            try:
                amount = int(m[1])
            except:
                amount = 1
        else:
            amount = 1
        item = m[0]
        if player["coins"] >= self.items[item][0] * amount:
            player["coins"] -= self.items[item][0]
            self.items[item] = (self.items[item][0] - 1, self.items[item][1])
            if item in player:
                player[item] = player[item] + amount
            else:
                player[item] = amount
            player_list.serialize_players()
            return "{} {}(s) acquired!".format(amount, item)
        else:
            return "not enough coins to purchase {} {}(s)".format(amount, item)


    def sell(self):
        # TODO
        0
