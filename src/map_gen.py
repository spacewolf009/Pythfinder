import libtcodpy as libtcod
import dice

MAX_ROOMS = 30
ROOM_MAX_SIZE, ROOM_MIN_SIZE = 10, 6
color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)

class Tile: # A tile of the map and its properties
    def __init__(self, blocked, block_sight = None, char = None):
        self.blocked, self.char = blocked, char
        self.block_sight = block_sight if block_sight else self.blocked # by default, if a tile is blocked, it also blocks sight
        self.explored, self.stash = False, []

    def render_data(self, in_fov): # Sort the stash at this point so the most important is at the head of the list and it's character will be displayed
        if not in_fov:
            if self.char is not None:
                return self.char, libtcod.gray, libtcod.black
            elif self.blocked and self.block_sight:
                return '#', libtcod.white, libtcod.dark_gray
            else:
                return '.', libtcod.gray, libtcod.black
        else:
            if self.char is not None:
                return self.char, libtcod.white, libtcod.black
            elif self.blocked and self.block_sight:
                return '#', libtcod.white, color_light_wall
            elif not len(self.stash):
                return '.', libtcod.yellow, libtcod.black
            elif len(self.stash) > 1:
                return '&', libtcod.chartreuse, libtcod.black
            else:
                return self.stash[0].char, self.stash[0].color, libtcod.black

class Rect: # a rectangle on the map. used to characterize a room.
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def centre(self):
        centre_x = (self.x1 + self.x2) / 2
        centre_y = (self.y1 + self.y2) / 2
        return (centre_x, centre_y)

    def intersect(self, other): # returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

def create_room(map, rect): # go through the tiles in a rectangle and make them passable
    for x in range(rect.x1 + 1, rect.x2):
        for y in range(rect.y1 + 1, rect.y2):
            map[x][y].blocked = False
            map[x][y].block_sight = False

def create_h_tunnel(map, x1, x2, y): # unblocks all tiles in a horizantal line
    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def create_v_tunnel(map, y1, y2, x): # unblocks all tiles in a vertical line
    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def make_map(width, height): # fill map with "blocked" tiles
    map = [[Tile(True) for y in range(height)] for x in range(width)]
    rooms, num_rooms = [], 0
    for r in range(MAX_ROOMS):
        # random width and height
        w, h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE), libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        # random position without going out of the boundaries of the map
        x, y = libtcod.random_get_int(0, 0, width - w - 1), libtcod.random_get_int(0, 0, height - h - 1)

        new_room = Rect(x, y, w, h)

        # run through the other rooms and see if they intersect with this one
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break
        if not failed:
            # No intersections; add to map.
            create_room(map, new_room)
            # center coordinates of new room, useful in generating new room
            (new_x, new_y) = new_room.centre()

            # Connect all rooms after the first to the previous room with a tunnel between the rooms' centres
            if num_rooms:
                (prev_x, prev_y) = rooms[num_rooms - 1].centre()
                # Randomly select whether to move horizantally or vertically first.
                if dice.roll('1d2')[0] == 1:
                    create_h_tunnel(map, prev_x, new_x, prev_y)
                    create_v_tunnel(map, prev_y, new_y, new_x)
                else:
                    create_v_tunnel(map, prev_y, new_y, prev_x)
                    create_h_tunnel(map, prev_x, new_x, new_y)

            rooms.append(new_room)
            num_rooms += 1
    return (map, rooms)