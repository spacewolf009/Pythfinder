import math

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
    TURN_CLOCK = 0L
    SCHEDULE = { }
    for item in objects:
        if item.speed() not in SCHEDULE:
            SCHEDULE[item.speed()] = [item]
        else:
            SCHEDULE[item.speed()] += [item]

def play_game():
    global game_state, plauer, TURN_CLOCK, SCHEDULE
    while not libtcod.console_is_window_closed():
        render_all()
        libtcod.console_flush()
        TURN_CLOCK += 1
        active = SCHEDULE.pop(TURN_CLOCK, False)
        if active is not False:
            for object in active:
                if object is player:
                    keys = handle_keys()
                    if keys == 'exit':
                        break
                    else:
                        turns = int(math.ceil(keys * player.fighter.speed()))
                else:
                    if object.ai:
                        turns = int(math.ceil(object.ai.take_turn()) * object.fighter.speed())
                if turns not in SCHEDULE:
                    SCHEDULE[turns] = [object]
                else:
                    SCHEDULE[turns] += [object]