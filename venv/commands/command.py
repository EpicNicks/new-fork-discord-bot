
import discord
from inspect import signature

# class representing commands

# find by title or alias and call execute
# list commands by printing array of commands title + list of aliases
class Command:

    ###
    # args:
    # title: str
    # aliases: List[str]
    # function: function
    # additional_args: List[any], const list of args to be applied in order to the function
    ###
    def __init__(self, title, aliases, function, additional_args = []):
        self.title = title
        self.aliases = aliases
        self.function = function
        self.params = additional_args


    def execute(self, message):
        # in case of zero arg function
        if len(signature(self.function).parameters) == 0:
            return self.function()
        return self.function(message, *self.params)

