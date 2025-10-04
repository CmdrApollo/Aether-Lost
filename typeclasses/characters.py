"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter
from evennia import AttributeProperty

from .objects import ObjectParent

from random import choice

class Character(ObjectParent, DefaultCharacter):
    """
    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Object child classes like this.

    """

    hp     = AttributeProperty(8)
    hp_max = AttributeProperty(8)

    mp     = AttributeProperty(8)
    mp_max = AttributeProperty(8)

    level  = AttributeProperty(1)
    xp     = AttributeProperty(0)
    copper = AttributeProperty(0)

    posse  = AttributeProperty(None)

    posse_permission = AttributeProperty(False)
    
    invites = AttributeProperty(list)

class NPC(Character):
    friendly_lines = ["Greetings, stranger.", "Greetings, friend.", "How d'ya do?"]
    aggressive_lines = ["You better get lost, friend.", "You better get lost, stranger."]

    friendly = True
    
    def at_char_entered(self, character, **kwargs):
        if not self.friendly:
            if len(self.aggressive_lines):
                self.execute_cmd(f"say {choice(self.aggressive_lines)}")
        else:
            if len(self.friendly_lines):
                self.execute_cmd(f"say {choice(self.friendly_lines)}")