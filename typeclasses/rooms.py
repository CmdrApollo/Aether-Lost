"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.objects.objects import DefaultRoom

from .objects import ObjectParent

from copy import deepcopy
from evennia import DefaultCharacter
from evennia.utils.utils import inherits_from

from evennia import TICKER_HANDLER, AttributeProperty

from random import choice, random

from evennia import utils

CHAR_SYMBOL = "|w@|n"
CHAR_ALT_SYMBOL = "|w>|n"
ROOM_SYMBOL = "|y$|n"
LINK_COLOR = "|n"

_MAP_GRID = [
    ["+", "-", "-", "-", "-", "-", "+"],
    [";", " ", " ", " ", " ", " ", ";"],
    [";", " ", " ", " ", " ", " ", ";"],
    [";", " ", " ", "@", " ", " ", ";"],
    [";", " ", " ", " ", " ", " ", ";"],
    [";", " ", " ", " ", " ", " ", ";"],
    ["+", "-", "-", "-", "-", "-", "+"],
]
_EXIT_GRID_SHIFT = {
    "north": (0, 1, "||"),
    "east": (1, 0, "-"),
    "south": (0, -1, "||"),
    "west": (-1, 0, "-"),
    "northeast": (1, 1, "/"),
    "southeast": (1, -1, "\\"),
    "southwest": (-1, -1, "/"),
    "northwest": (-1, 1, "\\"),
}

class Room(ObjectParent, DefaultRoom): 
    def at_object_receive(self, arriving_obj, source_location, **kwargs):
        if arriving_obj.account: 
            # this has an active acccount - a player character
            for item in self.contents:
                # get all npcs in the room and inform them
                if utils.inherits_from(item, "typeclasses.characters.NPC"):
                    item.at_char_entered(arriving_obj, **kwargs)

    def format_appearance(self, appearance, looker, **kwargs):
        """Don't left-strip the appearance string"""
        return appearance.rstrip()
 
    def get_display_desc(self, looker, **kwargs):
        exit_string = " ".join([ f"To the {ex.name}, you see {ex.destination.get_display_name(looker)}." for ex in self.exits ])
        return "     " + super().get_display_desc(looker, **kwargs) + " " + exit_string

    def get_display_header(self, looker, **kwargs):
        """
        Display the current location as a mini-map.
 
        """
        # make sure to not show make a map for users of screenreaders.
        # for optimization we also don't show it to npcs/mobs
        if not inherits_from(looker, DefaultCharacter) or (
            looker.account and looker.account.uses_screenreader()
        ):
            return ""
 
        # build a map
        map_grid = deepcopy(_MAP_GRID)
        dx0, dy0 = 3, 3
        map_grid[dy0][dx0] = CHAR_SYMBOL
        for exi in self.exits:
            dx, dy, symbol = _EXIT_GRID_SHIFT.get(exi.key, (None, None, None))
            if symbol is None:
                # we have a non-cardinal direction to go to - indicate this
                map_grid[dy0][dx0] = CHAR_ALT_SYMBOL
                continue
            map_grid[dy0 + dy][dx0 + dx] = f"{LINK_COLOR}{symbol}|n"
            if exi.destination != self:
                map_grid[dy0 + dy + dy][dx0 + dx + dx] = ROOM_SYMBOL
 
        # Note that on the grid, dy is really going *downwards* (origo is
        # in the top left), so we need to reverse the order at the end to mirror it
        # vertically and have it come out right.
        return "  " + "\n  ".join("".join(line) for line in reversed(map_grid))
    
class EchoingRoom(Room):
    """A room that randomly echoes messages to everyone inside it"""

    echoes = AttributeProperty(list)
    echo_rate = AttributeProperty(42)
    echo_chance = AttributeProperty(0.3)

    def send_echo(self): 
        if self.echoes and random() < self.echo_chance: 
            self.msg_contents(choice(self.echoes))

    def start_echo(self): 
        TICKER_HANDLER.add(self.echo_rate, self.send_echo)

    def stop_echo(self): 
        TICKER_HANDLER.remove(self.echo_rate, self.send_echo)