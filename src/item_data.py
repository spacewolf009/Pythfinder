# char, cost, damage, critical, range, weight, weapon flags (weapon type, damage type, special properties)
# types: simple|martial|[exotic]  light|one handed|two handed|ranged
LIGHT, ONEHAND, TWOHAND, RANGED = 1, 2, 4, 8
# damage types: Bludgeoning, Piercing, Slashing and special properties: trip, brace, reach, [double], disarm
B, P, S = 8, 16, 32
BRACE, REACH, TRIP, DISARM = 64, 128, 256, 512

weapons = {
# Simple Light
'dagger': ('|', 2, '1d4', (19, 2), 10, 1, LIGHT | P | 0),
'light mace': ('/', 5, '1d6', (20, 2), 0, 4, LIGHT | B | 0),
'sickle': ('\\', 5, '1d6', (20, 2), 0, 2, LIGHT | S | TRIP),
# Simple One Handed
'club': ('/', 0, '1d6', (20, 2), 10, 3, ONEHAND | B | 0),
'heavy mace': ('/', 12, '1d8' (20, 2), 0, 8, ONEHAND | B | 0),
'morningstar': ('/', 8, '1d8' (20, 2), 0, 6, ONEHAND | B | P | 0),
'shortspear': ('|', 1, '1d6' (20, 2), 20, 3, ONEHAND | P | 0),
# Simple Two Handed
'longspear': ('|', 5, '1d8', (20, 3), 0, 9, TWOHAND | P | REACH), 
'quarterstaff': ('/', 0, '1d6', (20, 2), 0, 4, TWOHAND | B | 0), 
'spear': ('|', 2, '1d8', (20, 3), 20, 6, TWOHAND | P | 0), 
# Simple Ranged
'blowgun': (')', 2, '1d2', (20, 2), 20, 1, RANGED | P | 0),
'heavy crossbow': (')', 50, '1d10', (19, 2), 120, 8, RANGED | P | 0),
'light crossbow': (')', 35, '1d8', (19, 2), 80, 4, RANGED | P | 0),
'dart': ('(', 0.05, '1d4', (20, 2), 20, 0.5, RANGED | P | 0),
'javelin': ('(', 1, '1d6', (20, 2), 30, 2, RANGED | P | 0),
'sling': (')', 0, '1d4', (20, 2), 50, 0, RANGED | B | 0),
# Martial Light
'throwing axe': ('\\', 8, '1d6', (20, 2), 10, 2, LIGHT | S | 0),
'light hammer': ('/', 1, '1d4', (20, 2), 20, 2, LIGHT | B | 0),
'hand axe': ('\\', 10, '1d6', (19, 2), 0, 3, LIGHT | S | 0),
'short sword': ('|', 2, '1d4', (19, 2), 0, 2, LIGHT | P | 0),
# Martial One Handed
'longsword': ('|', 15, '1d8', (19, 2), 0, 4, ONEHAND | P | S | 0), 
'battleaxe': ('\\', 10, '1d8', (20, 3), 0, 6, ONEHAND | S | 0),
'flail': ('/', 8, '1d8', (20, 2), 0, 5, ONEHAND | B | DISARM | TRIP),
'rapier': ('|', 20, '1d6', (18, 2), 0, 2, ONEHAND | P | 0),
'scimitar': ('|', 15, '1d6', (18, 2), 0, 4, ONEHAND | S | 0),
'trident': ('|', 15, '1d8', (20, 2), 10, 4, ONEHAND | P | 0),
'warhammer': ('/', 12, '1d8', (20, 3), 0, 5, ONEHAND | B | 0),
# Matial Two Handed
'falchion': ('|', 75, '2d4', (18, 2), 0, 8, TWOHAND | S | 0),
'glaive': ('|', 8, '1d10', (20, 3), 0, 10, TWOHAND | S | REACH),
'greataxe': ('\\', 20, '1d12', (20, 3), 0, 12, TWOHAND | S | 0),
'greatclub': ('/', 5, '1d10', (20, 2), 0, 8, TWOHAND | B | 0),
'greatsword': ('|', 50, '2d6', (19, 2), 0, 8, TWOHAND | S | 0),
'heavy flail': ('/', 15, '1d10', (19, 2), 0, 10, TWOHAND | B | DISARM | TRIP),
'guisarme': ('|', 9, '2d4', (20, 3), 0, 12, TWOHAND | S | REACH | TRIP),
'halberd': ('|', 10, '1d8', (20, 3), 0, 12, TWOHAND | P | S | BRACE | TRIP),
'lance': ('|', 10, '1d8', (20, 3), 0, 10, TWOHAND | P | REACH),
'scythe': ('|', 18, '2d4', (20, 4), 0, 10, TWOHAND | P | S | 0),
# Martial Ranged
'longbow': (')', 75, '1d8', (20, 3), 100, 3, RANGED | P | 0),
'shortbow': (')', 30, '1d6', (20, 3), 60, 2, RANGED | P | 0),
}


#############################################################################
AXIOMATIC, ANARCHIC, HOLY, UNHOLY, FIERY, FREEZING, SHOCKING, VORPAL, MASTERWORK, WOUNDING, THUNDERING, SPELL_STORING, KEEN, DEFENDING, BANE, DISRUPTION, SPEED, VICIOUS, DANCING, BRILLIANT_ENERGY, GHOST_TOUCH, CLEAVING = 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2 ** 11, 2 ** 12, 2 ** 13, 2 ** 14, 2 ** 15,  2 ** 16, 2 ** 17, 2 ** 18, 2 ** 19, 2 ** 20, 2 ** 21
 
#information about costs and other egos barred or modified by an ego
weapon_ego = {
AXIOMATIC: ('axiomatic', 0, [ANARCHIC]), ANARCHIC: ('anarchic', 0, [AXIOMATIC]), HOLY: ('holy', 0, [UNHOLY]), UNHOLY: ('unholy', 0, [HOLY]), FIERY: ('fiery', 0, [FREEZING]),
FREEZING: ('freezing', 0, [FIERY]), SHOCKING: ('shocking', 0, []), VORPAL: ('vorpal', 0, []), MASTERWORK: ('masterwork', 0, []), WOUNDING: ('wounding', 0, []), 
THUNDERING: ('thundering', 0, []), SPELL_STORING: ('spell storing', 0, []), KEEN: ('keen', 0, []), DEFENDING: ('defending', 0, []), BANE: ('bane', 0, []), 
DISRUPTION: ('disruption', 0, []), SPEED: ('speed', 0, []), VICIOUS: ('vicious', 0, []), DANCING: ('dancing', 0, []), BRILLIANT_ENERGY: ('brilliant energy', 0, []), 
GHOST_TOUCH: ('ghost touch', 0, []), CLEAVING: ('cleaving', 0, [])
 }