# weapon flags
# types: simple|martial|[exotic]  light|one handed|two handed|ranged
LIGHT, ONEHAND, TWOHAND, RANGED = 8, 16, 32, 64
# damage types: Bludgeoning, Piercing, Slashing and special properties: trip, brace, reach, [double], disarm
B, P, S = 1, 2, 4
BRACE, REACH, TRIP, DISARM = 128, 256, 512, 1024

# damage flags
DMG_FIRE, DMG_COLD, DMG_GOOD, DMG_EVIL, DMG_ELEC, DMG_ACID, DMG_POIS, DMG_SONIC, DMG_LAW, DMG_CHAOS, DMG_IRES = 8, 16, 32, 64, 128, 256, 512, 1024, 2**11, 2**12, 2**13
# (B, P, S = 1, 2, 4)

# resitance flags - resistance - typically for half damage and immunity 
# fire, cold, elec, sonic, poison, holy, evil
RES_FIRE, IMM_FIRE = 1, 2
RES_COLD, IMM_COLD = 4, 8
RES_ELEC, IMM_ELEC = 16, 32
RES_SONIC, IMM_SONIC = 64, 128
RES_POIS, IMM_POIS = 512, 1024
RES_GOOD, IMM_GOOD = 2**11, 2**12
RES_EVIL, IMM_HOLY = 2**13, 2**14

# Alignments
ALIGN_G, ALIGN_E, ALIGN_L, ALIGN_C = 1, 2, 4, 8 

#monster types
#zombie, seleton, beast, elemental...


# temp effects - on fire, poison