def get_path(map, start, end, print_out=False):
    if map[end[1]][end[0]].blocked: # don't even try to find a path to a blocked tile
        return None
        
    map = [[[1000,  map[x][y].blocked or map[x][y].encounter] for x in range(len(map[0]))] for y in range(len(map))]
        
    map[end[0]][end[1]] = [0, False, True]
    for num in range(2):
        for y in range(len(map)):
            for x in range(len(map[y])):
                point = map[x][y]
                if point[0]:
                    lowest = 1000
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            op_x, op_y = x + dx, y + dy
                            if not point[1] and op_x >= 0 and op_x < len(map[y]) and op_y >= 0 and op_y < len(map) and map[op_x][op_y][0] < lowest:
                                lowest = map[op_x][op_y][0]
                    if lowest < 1000:
                        point[0] = lowest + 1
                    
        y_list, x_list = range(len(map)), range(len(map[y]))
        y_list.reverse()
        x_list.reverse()
        for y in y_list:
            for x in x_list:
                point = map[x][y]
                if point[0]:
                    lowest = 1000
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            op_x, op_y = x + dx, y + dy
                            if not point[1] and op_x >= 0 and op_x < len(map[y]) and op_y >= 0 and op_y < len(map) and map[op_x][op_y][0] < lowest:
                                lowest = map[op_x][op_y][0]
                    if lowest < 1000:
                        point[0] = lowest + 1
    
    for line in map:
        text = ''
        for entry in line:
            value = entry[0]
            if value == 1000:
                text += ' '
            elif value > 15 and value < 25:
                text += ['g','h','i','j','k','l','m','o','p'][value - 16]
            else:
                text += str(hex(value))[-1] 
        text +=' | '
        for entry in line:
            if entry[1]:
                text += '#'
            else:
                text += '.'
        if print_out: print text
    if print_out: print ''
    
    path = [start]
    while not path[len(path)-1] == end:
        point, done = path[len(path) - 1], False
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                op_x, op_y = point[0] + dx, point[1] + dy
                if not map[op_x][op_y][1] and map[op_x][op_y][0] < map[point[0]][point[1]][0]:
                    path.append((op_x, op_y))
                    done = True
                    break
                if dx == 1 and dy == 1: # if break hasn't been executed and the last adjacent point (x+1,y+1) has just been tested, there is no path to be found.
                    return None
            if done:
                break
    
    return path