import dice
import random
import item_data

class EquipmentError(Exception):
    pass

# Base weapon info/stats - name, type, damage/crit, damage type, weight, handedness. base cost/weighting
# Egos - activated, length of effect, targeted/not, passive. cost/weighting

#########################################################################
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
#########################################################################
class Item:
    # an item that can be picked up and used.
    def __init__(self, use_function=None, weight=0):
        self.use_function = use_function
        self.weight = weight

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
#########################################################################

# damage die, (crit range, crit multiplier), handedness, range, reach(placeholder), damage type, weight
BASE_WEAPONS = item_data.weapons
# egos: cost and weighting information. the bane property is special and needs extra data
WEAPON_EGO = item_data.weapon_ego

class Weapon:#(Item):
    def __init__(self, name, type, cost, damage, critical, range, weight, weapon_flags=0, enhancement=0, ego=[]):
        self.item_type, self.weight = 'weapon', weight
        self.base_name, self.name = name, name
        self.damage, self.critical, self.weapon_flags = damage, critical, weapon_flags
        self.type, self.range = type, range
        self.enhancement, self.ego = enhancement, 0
        for item in ego:
            self.add_ego(item)

    def add_ego(ego):
        # Anything that modifies the basic properties of the weapon e.g. extended critical hit range.
        self.ego |= ego

    def on_wield(self, character):
        # Anything that occurs on wielding the weapon e.g. alignment sensitive weapons
        if (AXIOMATIC & self.ego and CHAOTIC & character.alignment) or (ANARCHIC & self.ego and LAWFUL & character.alignment) or (HOLY & self.ego and EVIL & character.alignment) or (UNHOLY & self.ego and GOOD & character.ALIGNMENT):
            # Apply negative level
            pass
    
    def on_unwield(self, character):
        if (AXIOMATIC & self.ego and CHAOTIC & character.alignment) or (ANARCHIC & self.ego and LAWFUL & character.alignment) or (HOLY & self.ego and EVIL & character.alignment) or (UNHOLY & self.ego and GOOD & character.ALIGNMENT):
            # Remove negative level
            pass
    
    def on_hit(self, attacker, defender):
        # do anything triggered by a hit (except regular damage)
        if (AXIOMATIC & self.ego and CHAOTIC & defender.alignment) or (ANARCHIC & self.ego and LAWFUL & defender.alignment) or (HOLY & self.ego and EVIL & defender.alignment) or (UNHOLY & self.ego and GOOD & defender.ALIGNMENT):
            pass
        if FIERY & self.ego:
            defender.take_damage(dice.roll('1d6')[0], 'fire')
        elif FREEZING & self.ego:
            defender.take_damage(dice.roll('1d6')[0], 'cold')
        elif SHOCKING & self.ego:
            defender.take_damage(dice.roll('1d6')[0], 'electric')
        elif WOUNDING & self.ego:
            pass


    def on_critical(self, attacker, defender, natural20=False):
        # do anything triggered by a successful critical hit
        if VORPAL & self.ego and natural20 == True:
            # defender dies if beheading is applicable
            pass
        elif FIERY & self.ego:
            pass
        elif FREEZING & self.ego:
            pass
        elif SHOCKING & self.ego:
            pass
        elif THUNDERING & self.ego:
            pass

    def on_attack(self, attacker, defender):
        # return any special bonus inherent to the weapon to attack rolls and perform other tasks at the time of the attack roll
        bonus = 0
        bonus += max([self.enhancement, 1 if 'masterwork' in self.ego else 0])
        return bonus

#(self, x, y, char, name, color, blocks=False, fighter=None, ai=None, item=None):
def create_weapon(name, enhancement=0, ego=[]):
    for item in ego:
        if item not in WEAPON_EGO.keys():
            raise EquipmentError(str(item) + 'is not valid')
    if name and type(name) is str and name in WEAPONS.keys():
        weapon_data = BASE_WEAPONS[name]
        # check for illegal combinations of ego/ego and ego/weapon
        if ('freezing' in ego and 'fiery' in ego) or ('shocking' in ego and 'fiery' in ego) or ('freezing' in ego and 'shocking' in ego):
            raise EquipmentError('Illegal combination of weapon and egos')
        item_component = Weapon(name, *weapon_data, enhancement=enhancement, ego=ego)
        return Object(0, 0, '|', name, libtcod.white, False, None, None, item_component)
    return False

def generate_weapon(value, base=None, alignment=None, melee=True, ranged=True):
    # creates a random weapon of a given value
    base = random.choice(BASE_WEAPONS.keys())

#########################################################################
# Armour name: (bonus, max dex, check penalty, speed(placeholder)). (negative max dex = no limit)
BASE_ARMOURS = {'leather': (2, 6, 0, None), 'chainmail': (6, 2, -5, None), 'half-plate': (8, 0, -7, None)}
# Shield name: (ac bonus, max_dex, check penalty)
BASE_SHIELDS = {'buckler': (1, -1, -1)}

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

def create_armour(name, ego=None):
    if name and type(name) is str:
        if name in ARMOURS.keys():
            item_component = Armour(name, *ARMOURS[name])
        elif name in SHIELDS.keys():
            item_component = Armour(name, *SHIELDS[name], speed=None)
        else: return False
        return Object(0, 0, '[', name, libtcod.white, False, None, None, item_component)
    return False
#########################################################################


#########################################################################
## TESTING
#########################################################################
