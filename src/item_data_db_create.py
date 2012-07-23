import sqlite3
import flags

conn = sqlite3.connect('items.db')

c = conn.cursor()

try:
	c.execute('''DROP TABLE weapon_base''')
	# c.execute('''DROP TABLE armour_base''')
	# c.execute('''DROP TABLE shield_base''')
	# c.execute('''DROP TABLE potion''')
	# c.execute('''DROP TABLE scroll''')
	# c.execute('''DROP TABLE spell''')
except:
	pass

c.execute('''CREATE TABLE weapon_base (
 name varchar(30) PRIMARY KEY NOT NULL,
 cost int NOT NULL,
 character char(1) NOT NULL,
 damage varchar(5) NOT NULL,
 crit_range int, 
 crit_mult int,
 range int,
 weight int NOT NULL,
 weapon_flags int NOT NULL,
 CHECK (cost >= 0 and damage LIKE "_%" and weapon_flags >= 9)
	)''')

# c.execute('''CREATE TABLE armour_base''')
# c.execute('''CREATE TABLE shield_base''')
# c.execute('''CREATE TABLE potion''')
# c.execute('''CREATE TABLE scroll''')
# c.execute('''CREATE TABLE spell''')

# #char, cost, damage, critical, range, weight, weapon flags (weapon type, damage type, special properties)
# # types: simple|martial|[exotic]  light|one handed|two handed|ranged
# flags.LIGHT, flags.ONEHAND, flags.TWOHAND, flags.RANGED = 1, 2, 4, 8
# # damage types: Bludgeoning, Piercing, Slashing and special properties: trip, brace, reach, [double], disarm
# B, P, flags.S = 16, 32, 64
# flags.BRACE, flags.REACH, flags.TRIP, flags.DISARM = 128, 256, 512, 1024

weapons = {
# Simple Light
'dagger': ('|', 2, '1d4', 19, 2, 10, 1, flags.LIGHT | flags.P),
'light mace': ('/', 5, '1d6', 20, 2, 0, 4, flags.LIGHT | flags.B),
'sickle': ('\\', 5, '1d6', 20, 2, 0, 2, flags.LIGHT | flags.S | flags.TRIP),
# Simple One Handed
'club': ('/', 0, '1d6', 20, 2, 10, 3, flags.ONEHAND | flags.B),
'heavy mace': ('/', 12, '1d8', 20, 2, 0, 8, flags.ONEHAND | flags.B),
'morningstar': ('/', 8, '1d8', 20, 2, 0, 6, flags.ONEHAND | flags.B | flags.P),
'shortspear': ('|', 1, '1d6', 20, 2, 20, 3, flags.ONEHAND | flags.P),
# Simple Two Handed
'longspear': ('|', 5, '1d8', 20, 3, 0, 9, flags.TWOHAND | flags.P | flags.REACH), 
'quarterstaff': ('/', 0, '1d6', 20, 2, 0, 4, flags.TWOHAND | flags.B), 
'spear': ('|', 2, '1d8', 20, 3, 20, 6, flags.TWOHAND | flags.P), 
# Simple Ranged
'blowgun': (')', 2, '1d2', 20, 2, 20, 1, flags.RANGED | flags.P),
'heavy crossbow': (')', 50, '1d10', 19, 2, 120, 8, flags.RANGED | flags.P),
'light crossbow': (')', 35, '1d8', 19, 2, 80, 4, flags.RANGED | flags.P),
'dart': ('(', 0, '1d4', 20, 2, 20, 0.5, flags.RANGED | flags.P),
'javelin': ('(', 1, '1d6', 20, 2, 30, 2, flags.RANGED | flags.P),
'sling': (')', 0, '1d4', 20, 2, 50, 0, flags.RANGED | flags.B),
# Martial Light
'throwing axe': ('\\', 8, '1d6', 20, 2, 10, 2, flags.LIGHT | flags.S),
'light hammer': ('/', 1, '1d4', 20, 2, 20, 2, flags.LIGHT | flags.B),
'hand axe': ('\\', 10, '1d6', 19, 2, 0, 3, flags.LIGHT | flags.S),
'short sword': ('|', 2, '1d4', 19, 2, 0, 2, flags.LIGHT | flags.P),
# Martial One Handed
'longsword': ('|', 15, '1d8', 19, 2, 0, 4, flags.ONEHAND | flags.P | flags.S), 
'battleaxe': ('\\', 10, '1d8', 20, 3, 0, 6, flags.ONEHAND | flags.S),
'flail': ('/', 8, '1d8', 20, 2, 0, 5, flags.ONEHAND | flags.B | flags.DISARM | flags.TRIP),
'rapier': ('|', 20, '1d6', 18, 2, 0, 2, flags.ONEHAND | flags.P),
'scimitar': ('|', 15, '1d6', 18, 2, 0, 4, flags.ONEHAND | flags.S),
'trident': ('|', 15, '1d8', 20, 2, 10, 4, flags.ONEHAND | flags.P),
'warhammer': ('/', 12, '1d8', 20, 3, 0, 5, flags.ONEHAND | flags.B),
# Matial Two Handed
'falchion': ('|', 75, '2d4', 18, 2, 0, 8, flags.TWOHAND | flags.S),
'glaive': ('|', 8, '1d10', 20, 3, 0, 10, flags.TWOHAND | flags.S | flags.REACH),
'greataxe': ('\\', 20, '1d12', 20, 3, 0, 12, flags.TWOHAND | flags.S),
'greatclub': ('/', 5, '1d10', 20, 2, 0, 8, flags.TWOHAND | flags.B),
'greatsword': ('|', 50, '2d6', 19, 2, 0, 8, flags.TWOHAND | flags.S),
'heavy flail': ('/', 15, '1d10', 19, 2, 0, 10, flags.TWOHAND | flags.B | flags.DISARM | flags.TRIP),
'guisarme': ('|', 9, '2d4', 20, 3, 0, 12, flags.TWOHAND | flags.S | flags.REACH | flags.TRIP),
'halberd': ('|', 10, '1d8', 20, 3, 0, 12, flags.TWOHAND | flags.P | flags.S | flags.BRACE | flags.TRIP),
'lance': ('|', 10, '1d8', 20, 3, 0, 10, flags.TWOHAND | flags.P | flags.REACH),
'scythe': ('|', 18, '2d4', 20, 4, 0, 10, flags.TWOHAND | flags.P | flags.S),
# Martial Ranged
'longbow': (')', 75, '1d8', 20, 3, 100, 3, flags.RANGED | flags.P),
'shortbow': (')', 30, '1d6', 20, 3, 60, 2, flags.RANGED | flags.P),
}

for key in weapons.keys():
	try:
		s = weapons[key]
		c.execute('''INSERT INTO weapon_base VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (key, s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7]))
	except:
		print 'error entering ' + key

conn.commit()



#############################################################################
AXIOMATIC, ANARCHIC, HOLY, UNHOLY, FIERY, FREEZING, SHOCKING, VORPAL, MASTERWORK, WOUNDING, THUNDERING, SPELL_STORING, KEEN, DEFENDING, BANE, DISRUPTION, SPEED, VICIOUS, DANCING, BRILLIANT_ENERGY, GHOST_TOUCH, CLEAVING = 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2 ** 11, 2 ** 12, 2 ** 13, 2 ** 14, 2 ** 15,  2 ** 16, 2 ** 17, 2 ** 18, 2 ** 19, 2 ** 20, 2 ** 21
 
# Cost, barred egos, weapon flags that must be present, weapon flags that must not be present
weapon_ego = {
AXIOMATIC: ('axiomatic', 0, [ANARCHIC], 0, 0), ANARCHIC: ('anarchic', 0, [AXIOMATIC]), HOLY: ('holy', 0, [UNHOLY]), UNHOLY: ('unholy', 0, [HOLY]), FIERY: ('fiery', 0, [FREEZING]),
FREEZING: ('freezing', 0, [FIERY]), SHOCKING: ('shocking', 0, []), VORPAL: ('vorpal', 0, []), MASTERWORK: ('masterwork', 0, []), WOUNDING: ('wounding', 0, []), 
THUNDERING: ('thundering', 0, []), SPELL_STORING: ('spell storing', 0, []), KEEN: ('keen', 0, []), DEFENDING: ('defending', 0, []), BANE: ('bane', 0, []), 
DISRUPTION: ('disruption', 0, []), SPEED: ('speed', 0, []), VICIOUS: ('vicious', 0, []), DANCING: ('dancing', 0, []), BRILLIANT_ENERGY: ('brilliant energy', 0, []), 
GHOST_TOUCH: ('ghost touch', 0, []), CLEAVING: ('cleaving', 0, [])
 }