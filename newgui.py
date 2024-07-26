import pygame as pg
import json
from random import randint
from search import *
import sys

#initialize important packet
pg.init
pg.font.init()

#Set window property
winW, winH = 1000, 800

#Class button for navigation
class Button:
    def __init__(self, img_src, img_hover, action):
        self.image = pg.image.load(img_src)
        self.image_hover = pg.image.load(img_hover)
        self.rect = self.image.get_rect()
        self.action = action
        self.clicked = False
    def draw(self, screen:pg.Surface, posX, posY):
        mousepos = pg.mouse.get_pos()
        self.rect.topleft = (posX, posY)
        if self.rect.collidepoint(mousepos):
            screen.blit(self.image_hover, self.rect)
            if pg.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                return self.action
            if pg.mouse.get_pressed()[0] == 0 and self.clicked:
                self.clicked = False
        else: 
            screen.blit(self.image, self.rect)
        return 0
    def getSize(self):
        return self.rect.size

#class Simulator for GUI
class Simulator:
    def __init__(self, winW, winH, problem):
        self.winW, self.winH = winW, winH
        self.window = pg.display.set_mode((winW, winH))
        self.clock = pg.time.Clock()
        self.HUD = {"canvas": pg.Rect(200, 200, 800, 600),
                    "info": pg.Rect(0,0, 200, 200),
                    "eventbox": pg.Rect(200, 0, 800, 200),
                    "togglehelp": pg.Rect(0, 200, 200, 600)}
        self.HUDFrame = pg.image.load("img/background/hud.png")
        
        #Problem material
        self.ROW, self.COL, self.TIME, self.FUEL, self.GRAPH, self.START, self.GOAL, self.STARTS, self.GOALS = problem
        self.gut = 5
        self.algorithm = {1: [(BFS, "BFS") , (DFS, "DFS") , (UCS, "UCS"), (GBFS, "GBFS") , (A_star, "A*") ]
                          , 2: [(A_star_level_2, "Super A* 2"), ]
                          , 3: [(A_star_level_3, "Super A* 3"), ]
                          , 4:[(Level4MultiAgent, "Level 4 Search")]}
        self.color = {-1:(1,1,1),"S": (0, 241, 29), 1:(239, 127, 0), 0: (255,255,255)  , "G": (255, 59, 35), "F": (0, 121, 255)}
        self.cellW = min(min(60, self.HUD["canvas"].size[0]//self.ROW ) - self.gut *2, min(60, self.HUD["canvas"].size[1]//self.COL ) - self.gut *2)
        self.cellH = self.cellW
        self.boardSize = (int(self.cellW * self.COL + self.gut*(self.COL)), int(self.cellW * self.ROW + self.gut*(self.ROW)))
        
        #Menu material
        self.levelbuttons = [Button("img/button/button_level1.png","img/button/button_level1_hover.png", 1)
                   , Button("img/button/button_level2.png", "img/button/button_level2_hover.png", 2)
                   , Button("img/button/button_level3.png", "img/button/button_level3_hover.png", 3)
                   , Button("img/button/button_level4.png", "img/button/button_level4_hover.png",  4)]
    def getBoardOffsetOnCanvas(self):
        return (self.HUD["canvas"].size[0] - self.boardSize[0]) // 2 + self.HUD["canvas"].left, (self.HUD["canvas"].size[1] - self.boardSize[1]) // 2 + self.HUD["canvas"].top
    
    def drawBoardCell(self, content, pos:tuple, color, background:str, width = 0):
        offsetX, offsetY = self.getBoardOffsetOnCanvas()
        cell = pg.Rect(0,0, self.cellW, self.cellH)
        cell.left, cell.top  = (pos[1]*(self.cellW + self.gut) +  offsetX, pos[0]*(self.cellH + self.gut) + offsetY)
        pg.draw.rect(self.window, background, cell, width)
        self.drawCellContent(content, pos)

    def drawPassedCellLine(self, startPos, endPos, color, width = 10):
        offsetX, offsetY = self.getBoardOffsetOnCanvas()
        startPixel = (startPos[1]*(self.cellW + self.gut) +  offsetX + self.cellW//2, startPos[0]*(self.cellH + self.gut) + offsetY  + self.cellH//2)
        endPixel = (endPos[1]*(self.cellW + self.gut) +  offsetX +  self.cellW//2, endPos[0]*(self.cellH + self.gut) + offsetY  + self.cellH//2)
        pg.draw.line(self.window, color, startPixel, endPixel, width)
        # self.drawCellContent(content, startPos)
    
    def drawCurrentCursor(self, pos, color):
        offsetX, offsetY = self.getBoardOffsetOnCanvas()
        curW, curH = 18, 18
        curPos = (pos[1]*(self.cellW + self.gut) +  offsetX + (self.cellW - curW)//2, pos[0]*(self.cellH + self.gut) + offsetY  + (self.cellH - curH)//2)
        pg.draw.rect(self.window, color, pg.Rect(curPos, (curW, curH)), 3)

    def drawCellContent(self, content, pos:tuple):
        offsetX, offsetY = self.getBoardOffsetOnCanvas()
        if (content != "" and content != "0" and content != "-1"):
            font = pg.font.Font("Oswald-Regular.ttf", 24)
            text = font.render(content, True, "#000000")
            rect = text.get_rect()
            rect.center = (pos[1]*(self.cellW + self.gut) +  offsetX + self.cellW//2, pos[0]*(self.cellH + self.gut) + offsetY  + self.cellH//2)
            self.window.blit(text, rect)
    def getColor(self, type):   
        try:
            type = int(type)
            if (type > 0):
                type = 1
            return self.color[type]
        except:
            return(self.color[type[0]])
        
    def drawInfo(self, Algorithmname, Level):
        font = pg.font.Font("Oswald-Regular.ttf", 24)
        labeltext, algo = font.render(f"Algorithm: ", True, "#000000"), font.render(Algorithmname, True, "#000000")
        level= font.render(f"Level: {Level}", True, "#000000")
        eraser = pg.Rect(0,0,100,42)
        self.window.blit(labeltext, (24, 24))
        eraser.topleft = (24, 36+24)
        pg.draw.rect(self.window, "#CCCCCC", eraser)
        self.window.blit(algo, (24, 36+36))
        self.window.blit(level, (24, 72+48))


    def drawToggleHelp(self):
        font = pg.font.Font("Oswald-Regular.ttf", 24)
        message = ["A: Auto On/Off", "N: Next round", "R: Reset run", "Q: Next Algo", "Q: Quit (last Algo)"]
        for i in range(len(message)):
            text = font.render(message[i], True, "#000000")
            self.window.blit(text, (24, self.HUD["togglehelp"].top + (i+1)*(36 + 12)))
        pg.display.flip()


    def resetBoard(self):
        for i in range(self.ROW):
            for j in range(self.COL):
                cellColor = self.getColor(self.GRAPH[i][j])
                self.drawBoardCell(str(self.GRAPH[i][j]), (i,j), "#000000", cellColor)
        pg.display.flip()

    def showMenu(self):
        for i in range(4):
            size = self.levelbuttons[i].getSize()
            level  = self.levelbuttons[i].draw(self.window, (self.winW -  size[0])/2, (i+1)*(size[1] + 70))
            if level > 0:
                break
        return level

    def drawSolutionPath(self, path):
        run = True
        draw = False
        index = 0
        cellColor = (103, 209, 82)
        oldColor = [i - 50 for i in cellColor]
        oldstep = []
        mode = {0: False, 1:True}
        while run:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_q:
                        return
                    if event.key == pg.K_r:
                        draw = False
                        index = 0
                        oldstep.clear()
                    if event.key == pg.K_n:
                        mode[0] = True
                    if event.key == pg.K_a:
                        mode[1] = not mode[1]
            if (path[0] != -1):
                if draw == False:
                    pg.draw.rect(self.window, "#CCCCCC", pg.Rect(210, 210, 780, 580))
                    self.resetBoard()
            try:
                step = path[index]
                if len(oldstep) > 0 and oldstep[-1] != step:
                    temp = oldstep.pop()
                    self.drawPassedCellLine(temp, step, oldColor)
                self.drawCurrentCursor( step , cellColor)
                oldstep.append(step)
                if(mode[0] or mode[1]):
                    index+=1
                    mode[0] = False
            except:
                continue
            
            self.clock.tick(12)
            pg.display.flip()
            pg.time.delay(100)
            draw = True
        return
    
    # def drawCurrentNode(self, content, pos:tuple, color, background:str, width = 0):

    
    def drawSolutionForLv4(self, path: list, goals: list):
        cell = pg.Rect(0, 0, self.cellW, self.cellH)
        run = True
        draw = False
        copyGraph = copy.deepcopy(self.GRAPH)
        stepindex = [0]*len(path) #Regulate step in each path
        startindex = 0 #regulate each starts I
        oldstep = dict()
        cellColor = [[208, 189, 127],
                    [138, 215, 159],
                    [241, 191, 135],
                    [167, 216, 132],
                    [206, 216, 173],
                    [220, 232, 180],
                    [174, 182, 225],
                    [216, 209, 131],
                    [129, 223, 132],
                    [237, 198, 158]]
        oldcellColor = [[channel - 50 for channel in color] for color in cellColor]
        mode = {0: True, 1: True} #0 is Manual, #1 is Auto
        print(path)
        #Add new goal to board
        count = 0
        for goallist in goals:
            for goal in goallist:
                if str(self.GRAPH[goal[0]][goal[1]])[0] != "G":
                    self.GRAPH[goal[0]][goal[1]] = f"GX{count}" # Added Goal\
                count += 1
        print(path)
        #Children loop
        debugDraw = True
        while run:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_q:
                        run = False
                        continue
                    if event.key == pg.K_r:
                        draw = False
                        stepindex = 0 #Regulate step in each path
                        startindex = 0 #regulate each starts I
                        stepindex = [0] * len(path)
                        oldstep.clear()
                    if event.key == pg.K_n:
                        mode[0] = True
                    if event.key == pg.K_a:
                        mode[1] = not mode[1]
            if draw == False:
                pg.draw.rect(self.window, "#CCCCCC", pg.Rect(210, 210, 780, 580))
                self.resetBoard()
            # pop = False
            if (startindex == len(path)): # Pass the last start
                startindex = 0
                mode[0] = False
            try:    
                step = path[startindex][stepindex[startindex]]
                # print(step)
                # if (startindex in oldstep):
                #     if (oldstep[startindex] != step):
                #         temp = oldstep[startindex]
                #         self.drawPassedCellLine(str(self.GRAPH[temp[0]][temp[1]]), temp, step, oldcellColor[startindex])
                        # self.drawBoardCell(str(self.GRAPH[temp[0]][temp[1]]), temp, "#000000", oldcellColor[startindex])
                # self.drawBoardCell(str(self.GRAPH[step[0]][step[1]]), step , "#000000", cellColor[startindex])
                self.drawCurrentCursor(step, cellColor[startindex])
                if (startindex in oldstep):
                    if (oldstep[startindex] != step):
                        temp = oldstep[startindex]
                        # self.drawBoardCell(str(self.GRAPH[temp[0]][temp[1]]), temp , "#000000", self.getColor(str(self.GRAPH[temp[0]][temp[1]])))
                        self.drawPassedCellLine(str(self.GRAPH[temp[0]][temp[1]]), temp, step, oldcellColor[startindex])
                self.clock.tick(10)
                pg.display.flip()
                pg.time.delay(100)
                if (mode[0] or mode[1]):
                    oldstep[startindex] = step
                    stepindex[startindex] += 1
                    startindex += 1 #Turn for next start
            except:
                if startindex < len(path):
                    startindex+=1
                continue
            draw = True
        self.GRAPH = copy.deepcopy(copyGraph)
        return

    def run(self):
        run = True
        self.window.fill("#CCCCCC")
        pg.display.set_caption("Search Simulation: Need for Fuel 1")
        run = True
        level = 0
        while run:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
            self.window.fill("#CCCCCC")
            level = self.showMenu()
            # # print(level)
            if (level > 0 and level < 4):
                    self.window.fill("#CCCCCC") 
                    self.window.blit(self.HUDFrame,(0,0))
                    self.drawToggleHelp()
                    pg.display.flip()
                    for algorithm in self.algorithm[level]:
                        self.drawInfo(algorithm[1], level)
                        path = algorithm[0]((self.ROW, self.COL, self.TIME, self.FUEL, self.GRAPH, self.START, self.GOAL))
                        self.drawSolutionPath(path)
                        pg.time.delay(300)
                    level = 0
            if (level == 4):
                    self.window.fill("#CCCCCC")
                    self.window.blit(self.HUDFrame,(0,0))
                    self.drawToggleHelp()
                    self.drawInfo(self.algorithm[4][0][1], level)
                    pg.display.flip()
                    paths, goals = self.algorithm[4][0][0]((self.ROW, self.COL, self.TIME, self.FUEL, self.GRAPH, self.START, self.GOAL), self.STARTS, self.GOALS)
                    self.drawSolutionForLv4(paths, goals)
                    level = 0
            pg.display.flip()
            self.clock.tick(60)

ROW, COL, TIME, FUEL, GRAPH, STARTS, GOALS = read_file("input.txt")
START = STARTS[0]
GOAL = GOALS[0]
PROBLEM = (ROW, COL, TIME, FUEL, GRAPH, START, GOAL, STARTS, GOALS)

sim = Simulator(winW, winH, PROBLEM)
sim.run()