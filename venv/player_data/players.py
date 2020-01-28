
import json

import jsonpickle # https://jsonpickle.github.io/#module-jsonpickle

from threading import Thread, Lock
from typing import List, Dict, Type

from .player import Player

# store a list of players with dicts of items, stats

# consts
P_DATA = "player_data.json"
P_DATA_BACKUP = "player_data_backup.json"

class Players:

    # all calls should NOT burn the main thread

    def __init__(self, client):
        self.lock = Lock()
        # list of dicts
        # Dict[str, Type[Player]]
        jsonpickle.set_encoder_options('simplejson', indent=4)
        self.player_data = {}
        # read from JSON
        self.load_players()
        self.client = client


    def __getitem__(self, id):
        if id in self.player_data:
            return self.player_data[id]
        else:
            return None


    def __setitem__(self, id, value):
        self.player_data[id] = value


    def __contains__(self, item):
        return item in self.player_data


    def items(self):
        return self.player_data.items()


    def register_player(self, message):
        if message.sender in self.player_data:
            return "<@{}> you're already registered!".format(message.sender)
        self.player_data[message.sender] = Player(message.sender)
        self.serialize_players()
        return "<@{}> you've been registered successfully!".format(message.sender)


    def __str__(self):
        players = "Players:\n"
        for player in self.player_data:
            players += "{}\n".format(str(player))
        return players


    def to_string(self, message):
        players = "**Players:**\n"
        for p_id, player in self.player_data.items():
            players += "{}\n".format(self.client.get_user(int(player.id)).name)
        return players


    def get_status(self, message):
        if len(message.words) == 1:
            return self.player_data[message.sender].get_status()
        elif len(message.words) == 2:
            p_id = message.words[1][3:-1] if message.words[1][3:-1] in self.player_data else message.words[1][2:-1]
            if p_id:
                return self.player_data[p_id].get_status()
            else:
                return "Player with id: {} not a registered player!".format(message.words[1])
        else:
            return "Invalid input. Must follow format *-status @user*"


    def load_players(self):
        # base case: json doesn't exist / is empty (only ran once probably doesn't need a second thread)
        Thread(target=self._load_players).start()


    def _load_players(self):
        with self.lock:
            with open(P_DATA, "r") as f:
                self.player_data = jsonpickle.decode(f.read())
        print("load of all players complete!")


    def serialize_players(self):
        Thread(target=self._serialize_players).start()


    def _serialize_players(self):
        # back up original in case shit fucks up
        with self.lock:
            with open(P_DATA, "r") as f:
                with open(P_DATA_BACKUP, "w+") as g:
                    copy = f.read()
                    g.write(copy)
            # save new data
            with open(P_DATA, "w+") as f:
                # pretty print workaround
                data = json.dumps(json.loads(jsonpickle.encode(self.player_data)), indent=4)
                f.write(data)

