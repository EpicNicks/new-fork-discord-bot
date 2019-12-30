
from typing import Dict

class Player:

    # for new users
    def __init__(self, id):
        self.data = self.player_default()
        self.id = int(id)


    # typing is Dict[str, int]
    def player_default(self):
        return {
            "level" : 1,
            "luck": 0,
            "coins" : 0
        }

    def add(self, key : str, amount : int):
        # validate somehow
        self.data[key] += amount

    def unconditional_add(self, item, amount):
        if not item in self:
            self[item] = 0
        self[item] += amount


    def __setitem__(self, key : str, amount : int):
        # validate somehow
        self.data[key] = amount


    def __getitem__(self, key : str):
        return self.data[key]


    def __contains__(self, item):
        return item in self.data


    def __str__(self):
        return str(self.data)


    def get_status(self):
        status = ""
        for i in self.data:
            status += "{} : {}\n".format(i, self.data[i])
        return status
