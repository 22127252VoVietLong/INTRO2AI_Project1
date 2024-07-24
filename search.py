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
def TreeSearchBFS(problem, level=1):
    row, col, time, fuel, graph, start, end = problem 
    queue = [(start[0], start[1], time, fuel, [start])]
    while queue:
        curR, curC, curTime, curFuel, curPath = queue.pop(0)
        if (curR, curC) == end:
            return curPath
        if level == 3 and curFuel <= 0:
            continue
        if level >= 2 and curTime <= 0:
            continue
        for i in range(4):
            neighborX, neighborY = (curR + DIRECTION[0][i], curC + DIRECTION[1][i])
            if neighborX < 0 or neighborX >= row or neighborY < 0 or neighborY >= col:
                continue
            if graph[neighborX][neighborY] != -1 and (neighborX, neighborY) not in curPath:
                newTime = curTime - 1
                newFuel = curFuel - 1
                if level == 3 and type(graph[neighborX][neighborY]) == type('a') and graph[neighborX][neighborY][0] == 'F':
                    newFuel = fuel
                    newTime -= int(graph[neighborX][neighborY][1:]) 
                if level >= 2 and type(graph[neighborX][neighborY]) == type(1):
                    newTime -= int(graph[neighborX][neighborY])
                queue.append((neighborX, neighborY, newTime, newFuel, curPath + [(neighborX, neighborY)]))
    return [-1]

# LEVEL 4 - LET KIEN COOK
def copyOfTreeSearchBFS(problem, level=1):
    row, col, time, fuel, graph, start, end = problem 
    queue = [(start[0], start[1], time, fuel, [start])]
    path = []
    h = row * col
    while queue:
        curR, curC, curTime, curFuel, curPath = queue.pop(0)
        if (curR, curC) == end:
            return curPath
        if level == 3 and curFuel <= 0:
            if manhattan((curR, curC), end) < h:
                h = manhattan((curR, curC), end)
                path = curPath
            continue
        if level >= 2 and curTime <= 0:
            if manhattan((curR, curC), end) < h:
                h = manhattan((curR, curC), end)
                path = curPath
            continue
        for i in range(4):
            neighborX, neighborY = (curR + DIRECTION[0][i], curC + DIRECTION[1][i])
            if neighborX < 0 or neighborX >= row or neighborY < 0 or neighborY >= col:
                if manhattan((curR, curC), end) < h:
                    h = manhattan((curR, curC), end)
                    path = curPath
                continue
            if graph[neighborX][neighborY] != -1 and (neighborX, neighborY) not in curPath:
                newTime = curTime - 1
                newFuel = curFuel - 1
                if level == 3 and type(graph[neighborX][neighborY]) == type('a') and graph[neighborX][neighborY][0] == 'F':
                    newFuel = fuel
                    newTime -= int(graph[neighborX][neighborY][1:]) 
                if level >= 2 and type(graph[neighborX][neighborY]) == type(1):
                    newTime -= int(graph[neighborX][neighborY])
                queue.append((neighborX, neighborY, newTime, newFuel, curPath + [(neighborX, neighborY)]))
    return path

def Level4MultiAgent(problem, starts, goals):
    row, col, time, fuel, graph, _, _ = problem
    graph[starts[0][0]][starts[0][1]] = 'S0'
    graph[goals[0][0]][goals[0][1]] = 'G0'
    goalss = []
    for u in range(len(goals)):
        goalss.append([goals[u]])
    paths = [[] for _ in range(len(starts))]
    for s in range(len(starts)):
        g = copy.deepcopy(graph)
        for ss in range(len(starts)):
            if ss != s:
                g[starts[ss][0]][starts[ss][1]] = 0
                g[goals[ss][0]][goals[ss][1]] = 0
        paths[s] = copyOfTreeSearchBFS((row, col, time, fuel, g, starts[s], goals[s]), 3)

    if paths[0][-1] != goals[0]:
        return [[-1] for _ in range(len(starts))], goalss
    
    move = [1 for _ in range(len(starts))]
    wt = [0 for _ in range(len(starts))]
    times = [time for _ in range(len(starts))]
    fuels = [fuel for _ in range(len(starts))]
    lost_place = []
    while True:
        for i in range(len(starts)):
            dele = []
            for l in range(len(lost_place)):
                if graph[lost_place[l][1][0]][lost_place[l][1][1]] == 0:
                    graph[lost_place[l][1][0]][lost_place[l][1][1]] = lost_place[l][0]
                    dele.append(l)
            for d in range(len(dele) - 1, -1, -1):
                lost_place.pop(dele[d])
            if times[i] <= 0 or fuels[i] <= 0:
                if i == 0:
                    if times[i] <= 0:
                        print(f'S{i} out of time')
                    elif fuels[i] <= 0:
                        print(f'S{i} out of fuel')
                    return [[-1] for _ in range(len(starts))], goalss
                else:
                    if times[i] <= 0:
                        print(f'S{i} out of time')
                    elif fuels[i] <= 0:
                        print(f'S{i} out of fuel')
                    continue
            print(i, move[i] - 1, (times[i], fuels[i]), starts[i])
            if not wt[i]:
                if type(graph[paths[i][move[i]][0]][paths[i][move[i]][1]]) == str:
                    if graph[paths[i][move[i]][0]][paths[i][move[i]][1]][0] == 'F':
                        wt[i] += int(graph[paths[i][move[i]][0]][paths[i][move[i]][1]][1:])
                        fuels[i] = fuel + 1
                        for _ in range(int(graph[paths[i][move[i]][0]][paths[i][move[i]][1]][1:])):
                            paths[i].insert(move[i], paths[i][move[i]])
                        lost_place.append((graph[paths[i][move[i]][0]][paths[i][move[i]][1]], paths[i][move[i]]))
                    elif graph[paths[i][move[i]][0]][paths[i][move[i]][1]][0] == 'S':
                        print ('here', i , int(graph[paths[i][move[i]][0]][paths[i][move[i]][1]][1:]))
                        if i < int(graph[paths[i][move[i]][0]][paths[i][move[i]][1]][1:]):
                            paths[i].insert(move[i], starts[i])
                            move[i] += 1
                            times[i] -= 1
                            continue
                        else:
                            print('i can go here', i , int(graph[paths[i][move[i]][0]][paths[i][move[i]][1]][1:]))
                            gt = copy.deepcopy(graph)
                            for ss in range(len(starts)):
                                if ss != i:
                                    gt[starts[ss][0]][starts[ss][1]] = 0
                                    gt[goals[ss][0]][goals[ss][1]] = 0
                            gt[paths[i][move[i]][0]][paths[i][move[i]][1]] = -1
                            paths[i][move[i]-1:] = copyOfTreeSearchBFS((row, col, times[i], fuels[i], gt, starts[i], goals[i]), 3)
                            print('mot', paths[i])
                            graph[starts[i][0]][starts[i][1]] = 0
                            starts[i] = paths[i][move[i]]
                            graph[starts[i][0]][starts[i][1]] = f'S{i}'
                            times[i] -= 1
                            fuels[i] -= 1
                            move[i] += 1
                            gt = copy.deepcopy(graph)
                            for ss in range(len(starts)):
                                if ss != i:
                                    gt[starts[ss][0]][starts[ss][1]] = 0
                                    gt[goals[ss][0]][goals[ss][1]] = 0
                            paths[i][move[i]-1:] = copyOfTreeSearchBFS((row, col, times[i], fuels[i], gt, starts[i], goals[i]), 3)
                            print('hai', paths[i])
                            continue
                    elif graph[paths[i][move[i]][0]][paths[i][move[i]][1]][0] == 'G':
                        if i == int(graph[paths[i][move[i]][0]][paths[i][move[i]][1]][1:]):
                            if i == 0:
                                return paths, goalss
                            else:
                                #generate new goals: gn
                                rn = random.randint(0, row - 1)
                                cn = random.randint(0, col - 1)
                                while graph[rn][cn] != 0:
                                    rn = random.randint(0, row - 1)
                                    cn = random.randint(0, col - 1)
                                #generate new goals: gn
                                graph[goals[i][0]][goals[i][1]] = 0
                                goals[i] = (rn, cn)
                                graph[goals[i][0]][goals[i][1]] = f'G{i}'
                                goalss[i].append((rn, cn))
                                gt = copy.deepcopy(graph)
                                for ss in range(len(starts)):
                                    if ss != i:
                                        gt[starts[ss][0]][starts[ss][1]] = 0
                                        gt[goals[ss][0]][goals[ss][1]] = 0
                                paths[i] += copyOfTreeSearchBFS((row, col, times[i], fuels[i], gt, starts[i], goals[i]), 3)
                        else:
                            lost_place.append((graph[paths[i][move[i]][0]][paths[i][move[i]][1]], paths[i][move[i]]))
                else:
                    wt[i] += graph[paths[i][move[i]][0]][paths[i][move[i]][1]]
                    for _ in range(graph[paths[i][move[i]][0]][paths[i][move[i]][1]]):
                        paths[i].insert(move[i], paths[i][move[i]])
                    if graph[paths[i][move[i]][0]][paths[i][move[i]][1]] > 0:
                        lost_place.append((graph[paths[i][move[i]][0]][paths[i][move[i]][1]], paths[i][move[i]]))
            else:
                wt[i] -= 1
                times[i] -= 1
                move[i] += 1
                continue
            graph[starts[i][0]][starts[i][1]] = 0
            starts[i] = paths[i][move[i]]
            graph[starts[i][0]][starts[i][1]] = f'S{i}'
            times[i] -= 1
            fuels[i] -= 1
            move[i] += 1

    return paths, goalss
    
    


# MAIN
#p, g = whatEverItIs(PROBLEM, STARTS, GOALS)
#for i in range(len(p)):
    #print(p[i])
#for i in range(len(p)):
    #print(g[i])
# print(TreeSearchBFS(PROBLEM, 3))
