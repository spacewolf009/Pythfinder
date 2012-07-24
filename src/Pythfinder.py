import libtcodpy as libtcod
import code
import math
import random
import shelve
import textwrap
import time
import dice
import map_gen
import pathfinding
import item_data
import flags

DEBUG = True
# actual size of the window
SCREEN_WIDTH, SCREEN_HEIGHT = 90, 50
# size of the map
MAP_WIDTH, MAP_HEIGHT = SCREEN_WIDTH, SCREEN_HEIGHT - 10
# global constants relevant to the GUI
BAR_WIDTH = 20
PANEL_HEIGHT = 10
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH, MSG_HEIGHT = SCREEN_WIDTH - BAR_WIDTH - 2, PANEL_HEIGHT - 1
INVENTORY_WIDTH = 50
LIMIT_FPS = 20  # 20 frames-per-second maximum
# constants relevant to field of view computation
FOV_ALGO = 0  # default libtcod FOV algorithm
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10
# constants relevant to map generation
MAX_ROOM_MONSTERS, MAX_ROOM_ITEMS = 4, 3

# Constants relevant to various spells and spell-like effects
LIGHTNING_DAMAGE, LIGHTNING_RANGE = 20, 5
CONFUSE_NUM_TURNS, CONFUSE_RANGE = 10, 8
FIREBALL_DAMAGE, FIREBALL_RADIUS = 12, 3

TURN_CLOCK = 0L
SCHEDULE = { }

STRENGTH, DEXTERITY, CONSTITUTION, INTELIGENCE, WISDOM, CHARISMA = 0, 1, 2, 3, 4, 5
#############################################
## Basic game classes
#############################################
class Object:
    def __init__(self, x, y, char, name, color, blocks=False, fighter=None, ai=None, item=None):
        self.x, self.y = x, y
        self.char, self.name, self.color = char, name, color
        self.blocks = blocks
        self.fighter, self.ai, self.item = fighter, ai, item
        # assign the object as the owner of each defined component.
        if self.fighter: self.fighter.owner = self
        if self.ai: self.ai.owner = self
        if self.item: self.item.owner = self

    def move(self, dx, dy):
        # move by the given amount as long as the player is attempting to move onto an unblocked space
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
            return True
        return False

    def draw(self): # set the color and then draw the character that represents this object at its position
        libtcod.console_set_foreground_color(con, self.color)
        libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self): # erase the character that represents this object
        libtcod.console_put_char(con, self.x, self.y, '.', libtcod.BKGND_NONE)

    def move_towards(self, target_x, target_y):
        dx, dy = target_x - self.x, target_y - self.y # vector from this object to the target, and distance
        distance = math.sqrt(dx ** 2 + dy ** 2)
        # normalize it to length 1 (preserving direction), then round it and convert to integer so the movement is restricted to the map grid
        dx, dy = int(round(dx / distance)), int(round(dy / distance))
        self.move(dx, dy)

    def distance_to(self, other): # return the distance to another object
        dx, dy = other.x - self.x, other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance(self, x, y): # return the distance to some coordinates
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def send_to_back(self): # make this object be drawn first, so all others appear above it if they're in the same tile.
        global objects
        objects.remove(self)
        objects.insert(0, self)

#############################################
## Magic Effects
#############################################
def cast_heal():
    if player.fighter.hp == player.fighter.max_hp:
        message('You are already at full health.', libtcod.red)
        return 'cancelled'
    message('Your wounds start to feel better!', libtcod.light_violet)
    player.fighter.heal(dice.roll('1d8')[0])

def cast_lightning(): # find closest enemy (inside a maximum range) and damage it
    monster = closest_monster(LIGHTNING_RANGE)
    if monster is None:  # no enemy found within maximum range
        message('No enemy is close enough to strike.', libtcod.red)
        return 'cancelled'
    message('A lighting bolt strikes the ' + monster.name + ' with a loud thunder! The damage is ' + str(LIGHTNING_DAMAGE) + ' hit points.', libtcod.light_blue)
    monster.fighter.take_damage(LIGHTNING_DAMAGE)

def cast_confuse(): # find closest enemy in-range and confuse it
    monster = closest_monster(CONFUSE_RANGE)
    if monster is None:  # no enemy found within maximum range
        message('No enemy is close enough to confuse.', libtcod.red)
        return 'cancelled'
    # replace the monster's AI with a "confused" one; after some turns it will restore the old AI
    old_ai = monster.ai
    monster.ai = ConfusedMonster(old_ai)
    monster.ai.owner = monster  #tell the new component who owns it
    message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', libtcod.light_green)
    
    libtcod.console_put_char_ex(0, monster.x, monster.y, monster.char, libtcod.black, libtcod.white)
    libtcod.console_flush()
    time.sleep(0.1)
    libtcod.console_put_char_ex(0, monster.x, monster.y, monster.char, monster.color, libtcod.black)
    libtcod.console_flush()
    time.sleep(0.1)
    
def cast_fireball():
    global fov_map
    message('Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan)
    (x, y) = target_tile()
    if x is None: return 'cancelled'
    message('The fireball explodes, burning everything within ' + str(FIREBALL_RADIUS) + ' tiles!', libtcod.orange)
    for obj in objects:  # damage every fighter in range, including the player
        if obj.distance(x, y) <= FIREBALL_RADIUS and obj.fighter:
            if libtcod.map_is_in_fov(fov_map, obj.x, obj.y):
                if obj == player:
                    msg1, msg2 ='', ''
                else:
                    msg1, msg2 = 'The ', 's'
                message(msg1 + obj.name.capitalize() + ' get' + msg2 +' burned for ' + str(FIREBALL_DAMAGE) + ' hit points.', libtcod.orange)
            else:
                message('You hear a cry of pain')
            obj.fighter.take_damage(FIREBALL_DAMAGE, flags.DMG_FIRE)
    render_all()
    # display code
    for num in range(3):
        for x1 in range(x - num, x + num):
            for y1 in range(y - num, y + num):
                if not map[x1][y1].block_sight and libtcod.map_is_in_fov(fov_map, x1, y1):
                    libtcod.console_put_char_ex(0, x1, y1, '*', libtcod.dark_orange, libtcod.red)
        libtcod.console_flush()
        time.sleep(0.1)
    time.sleep(0.25)

#############################################
## Movement and Combat
#############################################
def player_move_or_attack(dx, dy):
    global player, fov_recompute
    # the coordinates the player is attempting to move to/attack
    x, y = player.x + dx, player.y + dy
    # try to find an attackable object there
    target = None
    for object in objects:
        if object.fighter and object.x == x and object.y == y and object != player:
            target = object
            break
    # attack if target found, otherwise move. If the player moves, FoV needs to be recomputed
    if target:
        player.fighter.attack(target)
    else:
        player.move(dx, dy)
        fov_recompute = True

class Fighter:
    # combat-related properties and methods (monster, player, NPC).
    def __init__(self, hp, bab, attributes, base_speed=10, death_function=None, equipment=None, resists=0):
        self.max_hp, self.hp, self.bab = hp, hp, bab
        self.attributes, self.base_speed, self.death_function, self.equipment = attributes, base_speed, death_function, {}
        for slot in ['weapon', 'body', 'shield']:
            if slot in equipment.keys():
                self.equipment[slot] = equipment[slot]
            else:
                self.equipment[slot] = None;
        self.resists = resists

    def ac(self):
        return 10 + self.modifier(DEXTERITY) + self.equipment['body'].item.ac_bonus if self.equipment['body'] is not None else 0 + self.equipment['shield'].item.ac_bonus if self.equipment['shield'] is not None else 0

    def modifier(self, stat):
        mod = (self.attributes[stat] - 10) // 2
        if stat == DEXTERITY:
            if self.equipment['body'] is not None and self.equipment['body'].item.max_dex >= 0:
                mod = min([mod, self.equipment['body'].item.max_dex])
            if self.equipment['shield'] is not None and self.equipment['shield'].item.max_dex >= 0:
                mod = min([mod, self.equipment['shield'].item.max_dex])
        #return max([mod, 0])
        return mod

    def take_damage(self, damage, damage_type):
        assert(not (math.log(damage_type & 0xFFFFFFF8, 2) % 1))
        # apply damage if possible, apply special types of damage
        if damage_type & flags.B: # bludgeoning damage
            pass
        elif damage_type & flags.P: # Piercing damage
            pass
        elif damage_type & flags.S: # Slashing damage
            pass
        elif damage_type & flags.DMG_FIRE:
            if self.resists & flags.IMM_FIRE:
                damage = 0
            elif self.resists & flags.RES_FIRE:
                damage = damage // 2
        elif damage_type & flags.DMG_COLD:
             if self.resists & flags.IMM_COLD:
                damage = 0
             elif self.resists & flags.RES_COLD:
                damage = damage // 2
        elif damage_type & flags.DMG_GOOD:
             if self.resists & flags.IMM_GOOD:
                damage = 0
             elif self.resists & flags.RES_GOOD:
                damage = damage // 2
        elif damage_type & flags.DMG_EVIL:
            if self.resists & flags.IMM_EVIL:
                damage = 0
            elif self.resists & flags.RES_EVIL:
                damage = damage // 2
        elif damage_type & flags.DMG_SONIC:
             if self.resists & flags.IMM_SONIC:
                damage = 0
             elif self.resists & flags.RES_SONIC:
                damage = damage // 2
        elif damage_type & flags.DMG_ELEC:
             if self.resists & flags.IMM_ELEC:
                damage = 0
             elif self.resists & flags.RES_ELEC:
                damage = damage // 2
        elif damage_type & flags.DMG_ACID:
             if self.resists & flags.IMM_ACID:
                damage = 0
             elif self.resists & flags.RES_ACID:
                damage = damage // 2
        elif damage_type & flags.DMG_POIS:
             if self.resists & flags.IMM_POIS:
                damage = 0
             elif self.resists & flags.RES_POIS:
                damage = damage // 2

        if damage > 0:
            self.hp -= damage
        # check if the object is dead, if so apply its death function
        if self.hp <= 0:
            function = self.death_function
            if function is not None:
                function(self.owner)

    def attack(self, target):
        attack_roll, results = dice.roll('1d20 +' + str(self.bab + self.modifier(STRENGTH)))
        if attack_roll > target.fighter.ac() or results[0] == 20:
            damage_roll = dice.roll(self.equipment['weapon'].item.damage + '+' + str(self.modifier(STRENGTH)))
            # Deal with critical threats
            if results[0] >= self.equipment['weapon'].item.crit_range[0]:
                attack_roll, results = dice.roll('1d20 +' + str(self.bab + self.modifier(STRENGTH)))
                if attack_roll > target.fighter.ac() or results[0] == 20:
                    for i in range(self.equipment['weapon'].item.crit_range[1]):
                        damage_roll += dice.roll(self.equipment['weapon'].item.damage + '+' + str(self.modifier(STRENGTH)))
            if damage_roll > 0: # make the target take some damage.
                message(self.owner.name.capitalize() + ' hits ' + target.name + ' with a ' + self.equipment['weapon'].name + ' for ' + str(damage_roll[0]) + ' hit points.')
                target.fighter.take_damage(damage_roll[0])
            else:       # no damage dealt.
                message(self.owner.name.capitalize() + ' hit ' + target.name + ' but it has no effect!')
        else:
            message(self.owner.name.capitalize() + ' misses ' + target.name)

    def heal(self, amount):
        # heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def speed(self):
        # Other modifications to speed calculations go here
        return self.base_speed

def player_death(player): # the game ended!
    global game_state
    message( 'You died!')
    message('--GAME OVER--', libtcod.red)
    game_state = 'dead'
    player.char, player.color = '%', libtcod.dark_red

def monster_death(monster):
    global objects, SCHEDULE
    # transform the monster into a nasty corpse! it doesn't block, can't be attacked and doesn't move
    if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
        message ('The ' + monster.name.capitalize() + ' dies!')
    else:
        message('you hear something die in the distance')
    #monster.char, monster.color = '%', libtcod.dark_red
    #monster.blocks, monster.fighter, monster.ai = False, None, None
    #monster.name += ' corpse'
    #monster.send_to_back
    objects.remove(monster)
    for item in SCHEDULE.values():
        if monster in item:
            item.remove(monster)

#############################################
## ITEMS
#############################################
SCROLLS = {'lightning bolt': (libtcod.light_yellow, cast_lightning), 'fireball':(libtcod.orange, cast_fireball), 'confusion':(libtcod.pink, cast_confuse)}

POTIONS = {'healing': (libtcod.violet, cast_heal)}

class Item:
    # an item that can be picked up and used.
    def __init__(self, use_function=None):
        self.use_function=use_function

    def pick_up(self, char):
        # add to the player's inventory and remove from the map
        if len(inventory) >= 26:
            message('Your inventory is full, cannot pick up ' + self.owner.name + '.', libtcod.red)
        else:
            inventory.append(self.owner)
            map[char.x][char.y].stash.remove(self.owner)
            message('You picked up a ' + self.owner.name, libtcod.green)

    def use(self):
        # just call the "use_function" if it is defined
        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function() != 'cancelled':
                inventory.remove(self.owner)  # destroy after use, unless it was cancelled for some reason

    def drop(self, char):
        global map
        # Remove from the player's inventory, add to the map.
        inventory.remove(self.owner)
        map[char.x][char.y].stash.append(self.owner)
        message('You dropped a ' + self.owner.name + '.', libtcod.yellow)

def create_item(name, x, y):
    if name and type(name) is str:
        if name in POTIONS.keys():
            item_component = Item(POTIONS[name][1])
            char, colour = '!', POTIONS[name][0]
            name = 'Potion of ' + name
        elif name in SCROLLS.keys():
            item_component = Item(SCROLLS[name][1])
            char, colour = '?', SCROLLS[name][0]
            name = 'Scroll of ' + name
        else: return False
        return Object(x, y, char, name, colour, False, None, None, item_component)
    return False

#############################################
## WEAPONS
#############################################
# damage die (for all sizes), crit range, handedness, range, reach(placeholder)
WEAPONS = {'longsword': ('1d8', (19, 2), 2, 0), 'spear': ('1d8', (20, 3), 2, 0), 'shortbow': ('1d6', (20, 3), 2, 0), 'dagger': ('1d4', (19, 2), 1, 0)}

class Weapon(Item):
    def __init__(self, name, damage, crit_range, hands, reach):
        self.item_type = 'weapon'
        self.base_name, self.name = name, name
        self.damage, self.crit_range = damage, crit_range
        self.hands, self.reach = hands, reach

#(self, x, y, char, name, color, blocks=False, fighter=None, ai=None, item=None):
def create_weapon(name, brand=None):
    if name and type(name) is str and name in WEAPONS.keys():
        item_component = Weapon(name, *WEAPONS[name])
        return Object(0, 0, '|', name, libtcod.white, False, None, None, item_component)
    return False

#############################################
## ARMOUR
#############################################
# Armour name: (bonus, max dex, check penalty, speed(placeholder)). (negative max dex = no limit)
ARMOURS = {'leather': (2, 6, 0, None), 'chainmail': (6, 2, -5, None), 'half-plate': (8, 0, -7, None)}
# Shield name: (ac bonus, max_dex, check penalty)
SHIELDS = {'buckler': (1, -1, -1)}

class Armour(Item):
    def __init__(self, name, bonus, max_dex, check_pen, speed):
        self.equip_slot = 'armour' * (name in ARMOURS.keys()) + 'shield' * (name in SHIELDS.keys())
        self.base_name,self. name = name, name
        self.ac_bonus, self.max_dex, self.check_pen, self.speed = bonus, max_dex, check_pen, speed
    
    def use(self, char):
        if self.equip_slot == 'shield' and 'weapon' in char.fighter.equipment.keys() and char.fighter.equipment['weapon'].hands == 2 :
            # can't use shield and 2 handed weapon
            pass
        else:
            # put the previous gear into inventory
            char.fighter.equipment[slot] = self        

def create_armour(name, brand=None):
    if name and type(name) is str:
        if name in ARMOURS.keys():
            item_component = Armour(name, *ARMOURS[name])
        elif name in SHIELDS.keys():
            item_component = Armour(name, *SHIELDS[name], speed=None)
        else: return False
        return Object(0, 0, '[', name, libtcod.white, False, None, None, item_component)
    return False

#############################################
## MONSTERS & AI
#############################################
class BaseMonsterAI:
    # AI for a basic monster and base class for all AIs.
    def take_turn(self):
    # A basic monster takes its turn. If you can see it, it can see you
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
            # move towards player if far away
            if monster.distance_to(player) > 1:
                monster.move_towards(player.x, player.y)
            # close enough: attack! (if the player is still alive.)
            elif player.fighter.hp > 0:
                 monster.fighter.attack(player)
        return 1

class ConfusedMonster(BaseMonsterAI):
    # AI for a temporarily confused monster (reverts to previous AI after a while).
    def __init__(self, old_ai, num_turns=CONFUSE_NUM_TURNS):
        self.old_ai = old_ai
        self.num_turns = num_turns

    def take_turn(self):
        if self.num_turns > 0:  # still confused...
            # move in a random direction, and decrease the number of turns confused
            self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1

        else:  # restore the previous AI (this one will be deleted because it's not referenced anymore)
            self.owner.ai = self.old_ai
            message('The ' + self.owner.name + ' is no longer confused!', libtcod.red)
        return 1

# (char, colour, ai), (hp, bab, (attribs), speed, death) #SIZE, probablity weight
MONSTERS = {'troll': (('T', libtcod.light_green, BaseMonsterAI), (25, 2, (20, 12, 14, 8, 8, 5), 12, monster_death)), 
            'kobold': (('k', libtcod.red, BaseMonsterAI), (8, 1, (10, 10, 10, 9, 9, 7), 10, monster_death)), 
            'orc': (('o', libtcod.blue, BaseMonsterAI), (10, 1, (12, 12, 11, 10, 9, 6), 9, monster_death)),
            'bat': (('b', libtcod.gray, BaseMonsterAI), (5, 1, (8, 18, 8, 8, 8, 8), 5, monster_death))}

def create_monster(name, x, y):
    data = MONSTERS[name]
    if name and type(name) is str and name in MONSTERS.keys():
        fighter_component = Fighter(*data[1], equipment={'weapon': create_weapon(name=random.choice(WEAPONS.keys()))})
        monster = Object(x=x, y=y, char=data[0][0], name=name, color=data[0][1], blocks=True, fighter=fighter_component, ai=data[0][2](), )
        return monster
    return False

#############################################
## Map Generation
#############################################
def new_level():
    global map, player, stairs, depth, objects, TURN_CLOCK, SCHEDULE
    depth += 1
    objects = []
    map, rooms = map_gen.make_map(MAP_WIDTH, MAP_HEIGHT)
    for room in rooms:
        place_objects(room)
    player.x, player.y = 0, 0
    while is_blocked(player.x, player.y):
        player.x, player.y = dice.roll('1d'+ str(MAP_WIDTH) + '-1')[0], dice.roll('1d' + str(MAP_HEIGHT) + '-1')[0]
    objects += [player]
    stair_x, stair_y = 0, 0
    while is_blocked(stair_x, stair_y):
        stair_x, stair_y = dice.roll('1d'+ str(MAP_WIDTH) + '-1')[0], dice.roll('1d' + str(MAP_HEIGHT) + '-1')[0]
    map[stair_x][stair_y].char = '>'
    stairs = (stair_x, stair_y)
    initialize_fov()
    TURN_CLOCK = 0L
    SCHEDULE = { }
    for item in objects:
        if item.fighter.speed() not in SCHEDULE:
            SCHEDULE[item.fighter.speed()] = [item]
        else:
            SCHEDULE[item.fighter.speed()] += [item]

def place_objects(room):
    # choose random number of monsters
    num_monsters = libtcod.random_get_int(0, 0, MAX_ROOM_MONSTERS)
    for i in range(num_monsters):
        # choose random spot for this monster
        x, y = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1), libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
        if not is_blocked(x,y):
            place_monster(x,y)
    # choose random number of items
    num_items = libtcod.random_get_int(0, 0, MAX_ROOM_ITEMS)

    for i in range(num_items):
        #choose random spot for this item
        x, y = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1), libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

        # only place it if the tile is not blocked
        if not is_blocked(x, y):
            place_object(x,y)

def place_monster(x, y):
    seed = dice.roll('d100')[0]
    if  seed < 25:
        name = 'orc'
    elif seed < 60:
        name = 'kobold'
    elif seed < 85:
        name = 'bat'
    else:
        name = 'troll'
    monster = create_monster(name, x, y)
    if monster:  objects.append(monster)

def place_object(x,y):
    global map, objects
    seed = dice.roll('1d100')[0]
    if seed < 40:
        item = create_item('healing', x, y)
    elif seed < 60:
        item = create_item('lightning bolt', x, y)
    elif seed < 80:
        item = create_item('fireball', x, y)
    else:
        item = create_item('confusion', x, y)
    map[x][y].stash += [item]
    item.send_to_back

#############################################
## Targeting and Pathfinding
#############################################
def is_blocked(x, y): # first test the map tile
    global objects, map
    if map[x][y].blocked:
        return True
    #now check for any blocking objects
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True

    return False

def closest_monster(max_range):
    # find closest enemy, up to a maximum range, and in the player's FOV
    closest_enemy, closest_dist = None, max_range + 1  # start 1 greater than max range

    for object in objects:
        if object.fighter and not object == player and libtcod.map_is_in_fov(fov_map, object.x, object.y):
            #calculate distance between this object and the player
            dist = player.distance_to(object)
            if dist < closest_dist:  #it's closer, so remember it
                closest_enemy, closest_dist = object, dist
    return closest_enemy

def target_tile(max_range=None):
    # return the position of a tile left-clicked in player's FOV (optionally in a range), or (None,None) if right-clicked.
    while True:
        # render the screen. this erases the inventory and shows the names of objects under the mouse.
        render_all()
        libtcod.console_flush()

        key = libtcod.console_check_for_keypress()
        mouse = libtcod.mouse_get_status()  # get mouse position and click status
        (x, y) = (mouse.cx, mouse.cy)

        # accept the target if the player clicked in FOV, and in case a range is specified, if it's in that range
        if (mouse.lbutton_pressed and libtcod.map_is_in_fov(fov_map, x, y) and
            (max_range is None or player.distance(x, y) <= max_range)):
            return (x, y)
        if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
            return (None, None)  # cancel if the player right-clicked or pressed Escape

#############################################
## User Interface
#############################################
def handle_keys(): # handle key presses
    global map, inventory
    key = libtcod.console_wait_for_keypress(True)
    #key = libtcod.console_check_for_keypress()
    #while key == libtcod.KEY_NONE:
    #    key = libtcod.console_check_for_keypress()
    x, y = 1000, 1000

    if key.vk == libtcod.KEY_ENTER and key.lalt: # Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
        return 0
    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit'  # exit game

    if game_state == 'playing':
        #movement keys
        if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8: x, y = 0, -1
        elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2: x, y = 0, 1
        elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4: x, y = -1, 0
        elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6: x, y = 1, 0
        elif key.vk == libtcod.KEY_KP7: x, y = -1, -1
        elif key.vk == libtcod.KEY_KP9: x, y = 1, -1
        elif key.vk == libtcod.KEY_KP3: x, y = 1, 1
        elif key.vk == libtcod.KEY_KP1: x, y = -1, 1
        elif key.vk == libtcod.KEY_KP5: # rest a turn
            x, y = 0, 0
        else: # test for other keys
            key_char = chr(key.c)
            if key_char == 'g': # pick up an item
                if len(map[player.x][player.y].stash):
                    map[player.x][player.y].stash[0].item.pick_up(player)
                    x, y = 0, 0
                else: message('No item here')
            elif key_char == 'd': # show the inventory; if an item is selected, use it
                chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.drop(player)
                    x, y = 0, 0
            elif key_char == 'i': # show the inventory; if an item is selected, use it
                chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.use()
                    x, y = 0, 0
            elif key_char == 'e':
                equipment_menu()
            elif key_char == '>' and player.x == stairs[0] and player.y == stairs[1]:
                new_level()
                message('You descend deeper into the dungeon', libtcod.white)
                x, y = 0, 0
            elif key_char == '`' and DEBUG:
                try:
                    code.InteractiveConsole(globals()).interact("Enter Debug Commands:")
                except SystemExit, e: print "Got SystemExit!"
        if x != 1000 and y != 1000: # x and y will be have been reassigned if a turn was taken
            player_move_or_attack(x, y)
            return 1
        else:
            fov_recompute = False
    return 0

def render_all():
    global fov_recompute
    fov_recompute = True
    # go through all tiles, and set their background color according to the FOV
    if fov_recompute: # recompute FOV if needed (the player moved or something)
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            visible = libtcod.map_is_in_fov(fov_map, x, y)
            wall = map[x][y].block_sight
            if not visible: # it's out of the player's FOV
                if map[x][y].explored:
                    libtcod.console_put_char_ex(con, x, y, *map[x][y].render_data(False))
            else: # it's visible
                libtcod.console_put_char_ex(con, x, y, *map[x][y].render_data(True))
                mouse = libtcod.mouse_get_status()
                if x == mouse.cx and y == mouse.cy:
                    libtcod.console_set_back(con, x, y, libtcod.yellow, libtcod.BKGND_SET)
                map[x][y].explored = True    
    for object in objects:
        if libtcod.map_is_in_fov(fov_map, object.x, object.y):
            object.draw()
    player.draw()
    # prepare to render the GUI panel
    libtcod.console_set_background_color(panel, libtcod.black)
    libtcod.console_clear(panel)
    # print the game messages, one line at a time
    y = 1
    for (line, color) in game_msgs:
        libtcod.console_set_foreground_color(panel, color)
        libtcod.console_print_left(panel, MSG_X, y, libtcod.BKGND_NONE, line)
        y += 1
    # show the player's stats
    render_bar(1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp,
        libtcod.dark_green, libtcod.red)

    # display names of objects under the mouse
    libtcod.console_set_foreground_color(panel, libtcod.light_gray)
    libtcod.console_print_left(panel, 1, 0, libtcod.BKGND_NONE, get_names_under_mouse())
    
    # Display on main console
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
    # blit the contents of "panel" to the root console
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):  # render a bar (HP, experience, etc).
    # first calculate the width of the bar
    bar_width = int(float(value) / maximum * total_width)
    # render the background first
    libtcod.console_set_background_color(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False)
    # now render the bar on top
    libtcod.console_set_background_color(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False)
     # finally, some centered text with the values
    libtcod.console_set_foreground_color(panel, libtcod.white)
    libtcod.console_print_center(panel, x + total_width / 2, y, libtcod.BKGND_NONE, name + ': ' + str(value) + '/' + str(maximum))
    # show the player's stats
    libtcod.console_set_foreground_color(con, libtcod.white)
    libtcod.console_print_left(con, 1, SCREEN_HEIGHT - 2, libtcod.BKGND_NONE, 'HP: ' + str(player.fighter.hp) + '/' + str(player.fighter.max_hp) +'   ')

def message(new_msg, color = libtcod.white):
    # split the message if necessary, among multiple lines
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        # if the buffer is full, remove the first line to make room for the new one
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]
        # add the new line as a tuple, with the text and the color
        game_msgs.append((line, color))

def get_names_under_mouse():
    # return a string with the names of all objects under the mouse
    mouse = libtcod.mouse_get_status()
    (x, y) = (mouse.cx, mouse.cy)
    # create a list with the names of all objects at the mouse's coordinates and in FOV
    names = []
    if x < MAP_WIDTH and y < MAP_HEIGHT and libtcod.map_is_in_fov(fov_map, x, y):
        names = [obj.name for obj in objects if obj.x == x and obj.y == y]
        names += [item.name for item in map[x][y].stash]
        if not len(names):
            if map[x][y].blocked:
                names.append('wall')
            else:
                names.append('floor')
    names = ', '.join(names)  #join the names, separated by commas
    return names.capitalize()

def menu(header, options, width):
    if len(options) > 26:
        raise ValueError('Cannot have a menu with more than 26 options.')
    # calculate total height for the header (after auto-wrap) and one line per option
    header_height = libtcod.console_height_left_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
    height = len(options) + header_height
    # create an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)

    #print the header, with auto-wrap
    libtcod.console_set_foreground_color(window, libtcod.white)
    libtcod.console_print_left_rect(window, 0, 0, width, height, libtcod.BKGND_NONE, header)

    # print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_left(window, 0, y, libtcod.BKGND_NONE, text)
        y += 1
        letter_index += 1

     # blit the contents of "window" to the root console
    x, y = SCREEN_WIDTH / 2 - width / 2, SCREEN_HEIGHT / 2 - height / 2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    # present the root console to the player and wait for a key-press
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

    # convert the ASCII code to an index; if it corresponds to an option, return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index

    if key.vk == libtcod.KEY_ENTER and key.lalt:  # (special case) Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    return None

def inventory_menu(header):
    # show a menu with each item of the inventory as an option
    options = [item.name for item in inventory]
    if len(options) == 0:
        options = ['<Inventory is empty>']

    index = menu(header, options, INVENTORY_WIDTH)
    # if an item was chosen, return it
    if index is None or len(inventory) == 0: return None
    return inventory[index].item

def equipment_menu():
    options = [player.fighter.equipment[key].char + '  ' + player.fighter.equipment[key].name for key in player.fighter.equipment.keys()]
    if not len(options):
        options = ['<No Equipment>']
    menu('Equipment', options, INVENTORY_WIDTH) 

#############################################
## Saving and Loading
#############################################
def save_game(): # open a new empty shelve (possibly overwriting an old one) to write the game data
    file = shelve.open('savegame', 'n')
    file['map'] = map
    file['objects'] = objects
    file['player_index'] = objects.index(player)  # store index of player in objects list to avoid double storing
    file['inventory'] = inventory
    file['game_msgs'] = game_msgs
    file['game_state'] = game_state
    file.close()

def load_game(): # open the previously saved shelve and load the game data
    global map, objects, player, inventory, game_msgs, game_state
    file = shelve.open('savegame', 'r')
    map = file['map']
    objects = file['objects']
    player = objects[file['player_index']]  # get index of player in objects list and access it
    inventory = file['inventory']
    game_msgs = file['game_msgs']
    game_state = file['game_state']
    file.close()
    initialize_fov()

#############################################
## Initialization & Main Loop Methods
#############################################
def new_game():
    global player, inventory, game_msgs, game_state, depth, objects, TURN_CLOCK, SCHEDULE
    depth = 0
    # create object representing the player
    equipment = {'weapon': create_weapon('longsword'), 'body': create_armour('leather'), 'shield': create_armour('buckler')}
    fighter_component = Fighter(hp=80, bab=2, attributes=(17, 14, 13, 11, 12, 11), base_speed=10, death_function=player_death, equipment=equipment)
    player = Object(0, 0, '@', 'you', libtcod.white, blocks=True, fighter=fighter_component)

    game_state = 'playing'
    inventory, game_msgs = [], []
    message('Welcome to the Dungeons of Doom.', libtcod.red)
    # generate map
    new_level()

def initialize_fov():
    global fov_recompute, fov_map
    fov_recompute = True
    libtcod.console_clear(con)  # unexplored areas start black - the default background color
    # create the FOV map, according to the generated map
    fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            libtcod.map_set_properties(fov_map, x, y, not map[x][y].blocked, not map[x][y].block_sight)
          #game_state = 'no monsters'

def play_game():
    global game_state, player, TURN_CLOCK, SCHEDULE
    exit = False
    render_all()
    libtcod.console_flush()
    while not exit:
        TURN_CLOCK += 1
        active = SCHEDULE.pop(TURN_CLOCK, False)
        if active is not False:
            render_all()
            libtcod.console_flush()
            for object in active:
                if object in objects: # If object not in objects, it has died this turn
                    #print object.name + '\'s turn'
                    if object.name == 'you':
                        turns = 0
                        while not turns:
                            keys = handle_keys()
                            if keys == 'exit':
                                exit = True
                                break
                            else:
                                turns = int(keys * player.fighter.speed())
                            render_all()
                            libtcod.console_flush()
                    else:
                        turns = int(object.ai.take_turn() * object.fighter.speed())
                    if turns + TURN_CLOCK not in SCHEDULE:
                        SCHEDULE[turns + TURN_CLOCK] = [object]
                    else:
                        SCHEDULE[turns + TURN_CLOCK] += [object]

def main_menu():
    img = libtcod.image_load('menu_back.png')
    while 1:
        libtcod.image_blit_2x(img, 0, 0, 0)
        # show options and wait for the player's choice
        choice = menu('', ['Play a new game', 'Continue last game', 'Quit'], 24)
        if choice == 0:  # new game
            new_game()
            play_game()
        elif choice == 1:
            try:
                load_game()
                play_game()
            except:
                menu('\n No saved game to load.\n',[], 24)
        elif choice == 2: break  # quit

#############################################
## System Initialization
#############################################
libtcod.console_set_custom_font('arial12x12.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'MyRL', False)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
libtcod.sys_set_fps(LIMIT_FPS)

main_menu()