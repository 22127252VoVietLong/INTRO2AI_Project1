from heapq import heappop, heappush
import random
import copy
# CONSTANT VALUE
DIRECTION = [[0, 1, 0, -1], [-1, 0, 1, 0]]

# READING FILE ATTRIBUTES
def read_file(filename):
    with open(filename, "r") as f:
        temp = f.readline().split()
        row, col, time, fuel = map(int, temp)
        graph = []
        for _ in range(row):
            temp = f.readline().split()
            graph.append(temp)
        starts = []
        goals = []
        for i in range(row):
            for j in range(col):
                try:
                    graph[i][j] = int(graph[i][j])
                except:
                    if graph[i][j] == 'S':
                        starts.insert(0, (i, j))
                    elif graph[i][j] == 'G':
                        goals.insert(0, (i, j))
                    elif graph[i][j][0] == 'S':
                        starts.insert(int(graph[i][j][1:]), (i, j))
                    elif graph[i][j][0] == 'G':
                        goals.insert(int(graph[i][j][1:]), (i, j))
    return row, col, time, fuel, graph, starts, goals

#ROW, COL, TIME, FUEL, GRAPH, STARTS, GOALS = read_file("input.txt")
#START = STARTS[0]
#GOAL = GOALS[0]
#PROBLEM = (ROW, COL, TIME, FUEL, GRAPH, START, GOAL)

# MANHATTAN DISTANCE FOR CALCULATING HEURISTIC VALUE:
def manhattan(start, end):
    x1, y1 = start
    x2, y2 = end
    return abs(x1 - x2) + abs(y1 - y2)

# TRACING BACK:
def trace(visited, start, end):
    path = [end]
    while path[-1] != start:
        path.append(visited[path[-1]])
    path.reverse()
    return path

# LEVEL 1 -> 3:
def BFS(problem, level=1):
    row, col, time, fuel, graph, start, end = problem
    visited = {} 
    visited[start] = start   
    queue = [start]
    while queue:
        curR, curC = queue.pop(0)
        for i in range(4):
            neighborX, neighborY = (curR + DIRECTION[0][i], curC + DIRECTION[1][i])
            if neighborX < 0 or neighborX >= row or neighborY < 0 or neighborY >= col:
                continue
            if graph[neighborX][neighborY] != -1 and (neighborX, neighborY) not in visited:
                visited[(neighborX, neighborY)] = (curR, curC)
                if graph[neighborX][neighborY] == "G":
                    return trace(visited, start, end)
                queue.append((neighborX, neighborY))
    return [-1]

def DFS(problem, level=1):
    row, col, time, fuel, graph, start, end = problem
    visited = {} 
    visited[start] = start   
    stack = [start]
    while stack:
        curR, curC = stack.pop()
        for i in range(4):
            neighborX, neighborY = (curR + DIRECTION[0][i], curC + DIRECTION[1][i])
            if neighborX < 0 or neighborX >= row or neighborY < 0 or neighborY >= col:
                continue
            if graph[neighborX][neighborY] != -1 and (neighborX, neighborY) not in visited:
                visited[(neighborX, neighborY)] = (curR, curC)
                if graph[neighborX][neighborY] == "G":
                    return trace(visited, start, end)
                stack.append((neighborX, neighborY))
    return [-1]

def UCS(problem, level=1):
    row, col, _, _, graph, start, end = problem
    visited = {} 
    visited[start] = start   
    x, y = start
    frontier = [(0, x, y)]
    path_cost = {start: 0}
    
    while frontier:
        curCost, curR, curC = heappop(frontier)
        if (curR, curC) == end:
            return trace(visited, start, end)

        for i in range(4):
            neighborX, neighborY = (curR + DIRECTION[0][i], curC + DIRECTION[1][i])
            if neighborX < 0 or neighborX >= row or neighborY < 0 or neighborY >= col:
                continue
            if graph[neighborX][neighborY] != -1:
                new_cost = curCost + 1
                if (neighborX, neighborY) in path_cost and path_cost[(neighborX, neighborY)] <= new_cost:
                    continue
                visited[(neighborX, neighborY)] = (curR, curC)
                path_cost[(neighborX, neighborY)] = new_cost
                heappush(frontier, (new_cost, neighborX, neighborY))
    return [-1]         

def GBFS(problem, level=1):
    row, col, time, fuel, graph, start, end = problem
    visited = {} 
    visited[start] = start   
    x, y = start
    frontier = [(manhattan(start, end), x, y)]
    
    while frontier:
        _, curR, curC = heappop(frontier)
        for i in range(4):
            neighborX, neighborY = (curR + DIRECTION[0][i], curC + DIRECTION[1][i])
            if neighborX < 0 or neighborX >= row or neighborY < 0 or neighborY >= col:
                continue
            if graph[neighborX][neighborY] != -1 and (neighborX, neighborY) not in visited:
                visited[(neighborX, neighborY)] = (curR, curC)
                if graph[neighborX][neighborY] == "G":
                    return trace(visited, start, end)
                heappush(frontier, (manhattan((neighborX, neighborY), end), neighborX, neighborY))
    return [-1]
        

def A_star(problem, level=1):
    row, col, _, _, graph, start, end = problem
    visited = {} 
    visited[start] = start   
    x, y = start
    frontier = [(manhattan(start, end), x, y)]
    path_cost = {start: 0}
    
    while frontier:
        curCost, curR, curC = heappop(frontier)
        curCost = curCost - manhattan((curR, curC), end)

        if (curR, curC) == end:
            return trace(visited, start, end)

        for i in range(4):
            neighborX, neighborY = (curR + DIRECTION[0][i], curC + DIRECTION[1][i])
            if neighborX < 0 or neighborX >= row or neighborY < 0 or neighborY >= col:
                continue
            if graph[neighborX][neighborY] != -1:
                new_cost = curCost + 1
                
                if (neighborX, neighborY) in path_cost and path_cost[(neighborX, neighborY)] <= new_cost:
                    continue
                
                visited[(neighborX, neighborY)] = (curR, curC)
                path_cost[(neighborX, neighborY)] = new_cost
                heappush(frontier, (new_cost + manhattan((neighborX, neighborY), end), neighborX, neighborY))
    return [-1]                    

# LEVEL 2, 3 ONLY
def A_star_level_3(problem, level=1):
    row, col, time, fuel, graph, start, end = problem
    x, y = start
    visited = {} 
    visited[(x, y, time, fuel)] = (x, y, time, fuel)
    path_cost = {(x, y, time, fuel): 0}
    frontier = [(manhattan(start, end), time, fuel, x, y)]
    while frontier:
        curCost, curTime, curFuel, curR, curC = heappop(frontier)
        curCost = curCost - manhattan((curR, curC), end)
        if (curR, curC) == end:
            temp = trace(visited, (x, y, time, fuel), (curR, curC, curTime, curFuel))
            path = [(item[0], item[1]) for item in temp]
            return path
        if level == 3 and curFuel <= 0:
            continue
        if level >= 2 and curTime <= 0:
            continue
        for i in range(4):
            neighborX, neighborY = (curR + DIRECTION[0][i], curC + DIRECTION[1][i])
            if neighborX < 0 or neighborX >= row or neighborY < 0 or neighborY >= col:
                continue
            if graph[neighborX][neighborY] != -1 and (neighborX, neighborY):
                newCost = curCost + 1
                newTime = curTime - 1
                newFuel = curFuel - 1
                if (neighborX, neighborY, newTime, newFuel) in path_cost and path_cost[(neighborX, neighborY, newTime, newFuel)] <= newCost:
                    continue
                if level == 3 and type(graph[neighborX][neighborY]) == type('a') and graph[neighborX][neighborY][0] == 'F':
                    newFuel = fuel
                    newTime -= int(graph[neighborX][neighborY][1:]) 
                if level >= 2 and type(graph[neighborX][neighborY]) == type(1):
                    newTime -= int(graph[neighborX][neighborY])
                visited[(neighborX, neighborY, newTime, newFuel)] = (curR, curC, curTime, curFuel)
                path_cost[(neighborX, neighborY, newTime, newFuel)] = newCost
                heappush(frontier, (newCost + manhattan((neighborX, neighborY), end), newTime, newFuel, neighborX, neighborY))
    return [-1]

# LEVEL 4 - LET KIEN COOK
def copyOfA_star_level_3(problem, level=1):
    row, col, time, fuel, fuel0, graph, start, end = problem
    x, y = start
    visited = {} 
    visited[(x, y, time, fuel)] = (x, y, time, fuel)
    path_cost = {(x, y, time, fuel): 0}
    frontier = [(manhattan(start, end), time, fuel, x, y)]
    path = []
    min_heuristic = row * col
    while frontier:
        curCost, curTime, curFuel, curR, curC = heappop(frontier)
        curCost = curCost - manhattan((curR, curC), end)
        if (curR, curC) == end:
            return trace(visited, (x, y, time, fuel), (curR, curC, curTime, curFuel))
        if level == 3 and curFuel <= 0:
            temp = trace(visited, (x, y, time, fuel), (curR, curC, curTime, curFuel))
            if manhattan((temp[-1][0], temp[-1][1]), end) < min_heuristic:
                min_heuristic = manhattan((temp[-1][0], temp[-1][1]), end)
                path = temp
            continue
        if level >= 2 and curTime <= 0:
            temp = trace(visited, (x, y, time, fuel), (curR, curC, curTime, curFuel))
            if manhattan((temp[-1][0], temp[-1][1]), end) < min_heuristic:
                min_heuristic = manhattan((temp[-1][0], temp[-1][1]), end)
                path = temp
            continue
        for i in range(4):
            neighborX, neighborY = (curR + DIRECTION[0][i], curC + DIRECTION[1][i])
            if neighborX < 0 or neighborX >= row or neighborY < 0 or neighborY >= col:
                continue
            if graph[neighborX][neighborY] != -1 and (neighborX, neighborY):
                newCost = curCost + 1
                newTime = curTime - 1
                newFuel = curFuel - 1
                if (neighborX, neighborY, newTime, newFuel) in path_cost and path_cost[(neighborX, neighborY, newTime, newFuel)] <= newCost:
                    continue
                if level == 3 and type(graph[neighborX][neighborY]) == type('a') and graph[neighborX][neighborY][0] == 'F':
                    newFuel = fuel0
                    newTime -= int(graph[neighborX][neighborY][1:]) 
                if level >= 2 and type(graph[neighborX][neighborY]) == type(1):
                    newTime -= int(graph[neighborX][neighborY])
                visited[(neighborX, neighborY, newTime, newFuel)] = (curR, curC, curTime, curFuel)
                path_cost[(neighborX, neighborY, newTime, newFuel)] = newCost
                heappush(frontier, (newCost + manhattan((neighborX, neighborY), end), newTime, newFuel, neighborX, neighborY))
    return path

def expand_path(path):
    listi = []
    for i in range(len(path) - 1):
        if path[i][2] - path[i + 1][2] != 1:
            listi.append((i + 1, path[i][2] - path[i + 1][2] - 1))
    for t in range(len(listi) - 1, -1, -1):
        for z in range(listi[t][1]):
            p1, p2, p3, p4 = path[listi[t][0]]
            temp = (p1, p2, p3 + 1, p4)
            path.insert(listi[t][0], temp)
    return path

def returnPath(temp):
    path = [(item[0], item[1]) for item in temp]
    return path
    
def Level4MultiAgent(problem, starts, goals):
    row, col, time, fuel, graph, _, _ = problem
    
    # create an empty graph (does not has any start or goal)
    empty_graph = copy.deepcopy(graph)
    for i in range(len(starts)):
        empty_graph[starts[i][0]][starts[i][1]] = 0
        empty_graph[goals[i][0]][goals[i][1]] = 0

    # create goals list
    goal_list = []
    for idx in range(len(goals)):
        goal_list.append([goals[idx]])

    # list of paths (temp)
    paths = [[] for _ in range(len(starts))]
    for s in range(len(starts)):
        graph_temp = copy.deepcopy(empty_graph)
        graph_temp[starts[s][0]][starts[s][1]] = 'S'
        graph_temp[goals[s][0]][goals[s][1]] = 'G'
        # first find an optimized path for each start
        paths[s] = copyOfA_star_level_3((row, col, time, fuel, fuel, graph_temp, starts[s], goals[s]), 3)
        paths[s] = expand_path(paths[s])

    # if there is no possible path from S to G, return -1
    if (paths[0][-1][0], paths[0][-1][1]) != goals[0]:
        return [[-1] for _ in range(len(starts))], goal_list

    # move tracker
    move = [1 for _ in range(len(starts))]
    
    # main loop
    while True:
        for i in range(len(starts)):
            # time and fuel check
            if paths[i][move[i] - 1][2] <= 0 or paths[i][move[i] - 1][3] <= 0:
                if i == 0:
                    len_path = len(paths[i])
                    for pa in range(1, len(starts)):
                        if len(paths[pa]) >= len_path:
                            exceed = len(paths[pa]) - len_path + 1
                            for _ in range(exceed):
                                paths[pa].pop()
                    return [returnPath(paths[x]) for x in range(len(starts))], goal_list
                else:
                    continue

            # if start i dont move, skip
            if (paths[i][move[i]][0], paths[i][move[i]][1]) == (paths[i][move[i] - 1][0], paths[i][move[i] - 1][1]):
                move[i] += 1
                continue

            # get list of current location of all starts and goals
            current_starts = [(paths[j][move[j] - 1][0], paths[j][move[j] - 1][1]) for j in range(len(starts))]
            current_goals = [goal_list[j][-1] for j in range(len(goals))]
            # if next move of start i collide order start
            if (paths[i][move[i]][0], paths[i][move[i]][1]) in current_starts:
                collide_idx = current_starts.index((paths[i][move[i]][0], paths[i][move[i]][1]))
                if i < collide_idx:
                    paths[i].insert(move[i], paths[i][move[i] - 1])
                    for j in range(move[i], len(paths[i])):
                        p1, p2, p3, p4 = paths[i][j]
                        paths[i][j] = (p1, p2, p3 + 1, p4)
                    move[i] += 1
                else:
                    graph_temp = copy.deepcopy(empty_graph)
                    graph_temp[paths[i][move[i] - 1][0]][paths[i][move[i] - 1][1]] = 'S'
                    graph_temp[current_goals[i][0]][current_goals[i][1]] = 'G'
                    while (paths[i][move[i]][0], paths[i][move[i]][1]) in current_starts:
                        graph_temp[paths[i][move[i]][0]][paths[i][move[i]][1]] = -1
                        paths[i][move[i] - 1:] = copyOfA_star_level_3((row, col, paths[i][move[i] - 1][2], paths[i][move[i] - 1][3], fuel, graph_temp, (paths[i][move[i] - 1][0], paths[i][move[i] - 1][1]), current_goals[i]), 3)
                    move[i] += 1
                    graph_temp = copy.deepcopy(empty_graph)
                    graph_temp[paths[i][move[i] - 1][0]][paths[i][move[i] - 1][1]] = 'S'
                    graph_temp[current_goals[i][0]][current_goals[i][1]] = 'G'
                    paths[i][move[i] - 1:] = copyOfA_star_level_3((row, col, paths[i][move[i] - 1][2], paths[i][move[i] - 1][3], fuel, graph_temp, (paths[i][move[i] - 1][0], paths[i][move[i] - 1][1]), current_goals[i]), 3)
                    paths[i] = expand_path(paths[i])
                continue

            # if start i got to goal
            if (paths[i][move[i]][0], paths[i][move[i]][1]) == current_goals[i]:
                if i == 0:
                    len_path = len(paths[i])
                    for pa in range(1, len(starts)):
                        if len(paths[pa]) >= len_path:
                            exceed = len(paths[pa]) - len_path + 1
                            for _ in range(exceed):
                                paths[pa].pop()
                    return [returnPath(paths[x]) for x in range(len(starts))], goal_list
                else:
                    move[i] += 1
                    #generate new goal
                    r = random.randint(0, row - 1)
                    c = random.randint(0, col - 1)
                    while empty_graph[r][c] != 0 or (r, c) in current_starts or (r, c) in current_goals:
                        r = random.randint(0, row - 1)
                        c = random.randint(0, col - 1)
                    goal_list[i].append((r, c))
                    current_goals[i] = (r, c)
                    graph_temp = copy.deepcopy(empty_graph)
                    graph_temp[paths[i][move[i] - 1][0]][paths[i][move[i] - 1][1]] = 'S'
                    graph_temp[current_goals[i][0]][current_goals[i][1]] = 'G'
                    paths[i][move[i] - 1:] = copyOfA_star_level_3((row, col, paths[i][move[i] - 1][2], paths[i][move[i] - 1][3], fuel, graph_temp, (paths[i][move[i] - 1][0], paths[i][move[i] - 1][1]), current_goals[i]), 3)
                    paths[i] = expand_path(paths[i])
                    continue
            move[i] += 1


# MAIN
#paths, goals = Level4MultiAgent(PROBLEM, STARTS, GOALS)
#print('goals', goals)
#for i in range(len(paths)):
    #print(f'path S{i}', paths[i])
