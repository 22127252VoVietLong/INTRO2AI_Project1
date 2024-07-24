import pygame as pg
import json
from random import randint
from search import *
import sys
pg.init()
pg.font.init()


# class PROBLEM:
#     def __init__(self, ROW, COL, TIME, FUEL, GRAPH, START, GOAL ):
#         self.ROW = ROW
#         self.COL = COL
#         self.TIME = TIME
#         self.FUEL = FUEL
#         self.GRAPH = GRAPH
#         self.START = START
#         self.GOAL = GOAL
        
#     def getAttributeForSearch(self):
#         return (self.ROW, self.COL, self.TIME, self.FUEL, self.GRAPH, self.START, self.GOAL )

ROW, COL, TIME, FUEL, GRAPH, STARTS, GOALS = read_file("input.txt")
START = STARTS[0]
GOAL = GOALS[0]
PROBLEM = (ROW, COL, TIME, FUEL, GRAPH, START, GOAL, STARTS, GOALS)

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
class Game:
    def __init__(self, problem) -> None:
        self.size = (800, 800)
        self.clock = pg.time.Clock()   
        self.screen = pg.display.set_mode((self.size))
        self.ROW, self.COL, self.TIME, self.FUEL, self.GRAPH, self.START, self.GOAL, self.STARTS, self.GOALS = problem
        self.gut = 5
        self.algorithm = {1: [(BFS, "BFS") , (DFS, "DFS") , (UCS, "UCS"), (GBFS, "GBFS") , (A_star, "A*") ]
                          , 2: [(BFS, "BFS") , (DFS, "DFS") , (UCS, "UCS"), (GBFS, "GBFS") , (A_star, "A*"), ]
                          , 3: [(BFS, "BFS") , (DFS, "DFS") , (UCS, "UCS"), (GBFS, "GBFS") , (A_star, "A*"), ]
                          , 4:[(Level4MultiAgent, "Level 4 Search")]}
        self.color = {-1:"#111111","S": "#00CC00", 1: "#0000FF", 0: "#FFFFFF", "G": "#CC0000", "F": "#FFFF00"}
        self.cellW = min(60, self.size[1]//self.ROW ) - self.gut *2
        self.cellH = min(60, self.size[0]//self.COL ) - self.gut *2
        self.boardSize = (int(self.cellH * self.COL + self.gut*(self.ROW)), int(self.cellW * self.ROW + self.gut*(self.COL)))
        self.levelbuttons = [Button("img/button/button_level1.png","img/button/button_level1_hover.png", 1)
                   , Button("img/button/button_level2.png", "img/button/button_level2_hover.png", 2)
                   , Button("img/button/button_level3.png", "img/button/button_level3_hover.png", 3)
                   , Button("img/button/button_level4.png", "img/button/button_level4_hover.png",  4)]
    def getCellSize(self):
        return self.cellW, self.cellH
    def getGraphOffset(self):
        return (self.size[1] - self.boardSize[1]) // 2, (self.size[1] - self.boardSize[1]) // 2
    def getColor(self, type):
        try:
            type = int(type)
            if (type > 0):
                type = 1
            return self.color[type]
        except:
            return(self.color[type[0]])
    def getTexture(self): 
        return "fuel.png"
    def drawCell(self, cell: pg.Rect, content:str, size:int , pos:tuple, color:str, background:str, textalign:str = "center"):
        cell.topleft = pos
        pg.draw.rect(self.screen, background, cell)
        if (content != "" and content != "0" and content != "-1"):
            font = pg.font.Font("Oswald-Regular.ttf",size)
            text = font.render(content, True, color)
            rect = text.get_rect()
            if textalign == "center":
                rect.center = (pos[0]+ self.cellH//2, pos[1]+ self.cellW//2)
            if textalign == "left":
                rect.topleft = pos
            self.screen.blit(text, rect)
    # def drawTextCell(self, cell: pg.Rect, content:str, size:int, pos:tuple, color:str, background:str, textalign:str = "center"):
    #     font = pg.font.Font("Oswald-Regular.ttf",size)
    #     text = font.render(content, True, color)
    #     rect = text.get_rect()
    #     if textalign == "center":
    #         rect.center = (pos[0]+ self.cellH//2, pos[1]+ self.cellW//2)
    #     if textalign == "left":
    #         rect.topleft = pos
    #     self.drawCell(cell, pos, background)
    #     self.screen.blit(text, rect)
    def drawText(self, content:str, size:int, pos:tuple, color, background:str=""):
        font = pg.font.Font("Oswald-Regular.ttf",size)
        text = font.render(content, True, color)
        rect = text.get_rect()
        rect.topleft = pos
        if(background != ""):
            pg.draw.rect(self.screen, background, rect)
        self.screen.blit(text, rect)
    def resetBoard(self):
        offsetX, offsetY = self.getGraphOffset()
        cell = pg.Rect(0,0, self.cellW, self.cellH)
        for i in range(self.ROW):
            for j in range(self.COL):
                cellColor = self.getColor(self.GRAPH[i][j])
                self.drawCell(cell, str(self.GRAPH[i][j]), 24, (j*(self.cellW + self.gut) +  offsetX, i*(self.cellH + self.gut) + offsetY), "#000000", cellColor)
        pg.display.flip()

    def drawSolutionPath(self, path):
        offsetX, offsetY = self.getGraphOffset()
        cell = pg.Rect(0, 0, self.cellW, self.cellH)
        run = True
        draw = False
        index = 0
        pathlen = len(path)
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
            if draw == False:
                self.resetBoard()
            try:
                step = path[index]
                cellColor = "#00FF00"
                self.drawCell(cell, str(self.GRAPH[step[0]][step[1]]), 24, (step[1]*(self.cellW + self.gut) + offsetX, step[0]*(self.cellH + self.gut) + offsetY) , "#000000", cellColor)
                self.clock.tick(24)
                pg.display.flip()
                pg.time.delay(100)
                index+=1
            except:
                continue
            draw = True
        return
    def drawSolutionForLv4(self, path: list, goals: list):
        offsetX, offsetY = self.getGraphOffset()
        cell = pg.Rect(0, 0, self.cellW, self.cellH)
        run = True
        draw = False
        stepindex = 0 #Regulate step in each path
        pathindex = 0 #Regulate path in each paths
        startindex = 0 #regulate each starts I
        pathslen = len(path)
        cellColor = (0, 255, 0)
        for goallist in goals:
            for goal in goallist:
                self.GRAPH[goal[0]][goal[1]] = "G"
        print(self.GRAPH)
        
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
                        stepindex = 0 #Regulate step in each path
                        pathindex = 0 #Regulate path in each paths
                        startindex = 0 #regulate each starts I
            if draw == False:
                self.resetBoard()
            try:
                step = path[startindex][stepindex]
                # print(step)
                cellColor = "#00FF00"
                self.drawCell(cell, str(self.GRAPH[step[0]][step[1]]), 24, (step[1]*(self.cellW + self.gut) + offsetX, step[0]*(self.cellH + self.gut) + offsetY) , "#000000", cellColor)
                self.clock.tick(24)
                pg.display.flip()
                pg.time.delay(100)
                if (stepindex < len(path[startindex]) - 1):
                    stepindex+=1
                    print(stepindex)
                else:
                    startindex+=1
                    stepindex = 0
            except:
                continue
            draw = True
        return
    def showMenu(self):
        for i in range(4):
            size = self.levelbuttons[i].getSize()
            level  = self.levelbuttons[i].draw(self.screen, (self.size[0] -  size[0])/2, (i+1)*(size[1] + 70))
            if level > 0:
                break
        return level
    def printAlgorithmInfo(self, algorithmname, level):
        textholder = pg.Rect(0,0, 320, 32)
        self.drawCell(textholder, "Algorithm: "+ algorithmname, 24, (70, 30), "#000000", "#CCCCCC", "left")
        self.drawText("Level: " + str(level), 24, (350, 30), "#000000", "#CCCCCC")
        
    def run(self): 
        self.screen.fill("#CCCCCC")
        pg.display.set_caption("Search Simulation: Need for Fuel 1")
        run = True
        while run:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
            self.screen.fill("#CCCCCC")
            level = self.showMenu()
            if (level > 0 and level < 4): 
                    self.screen.fill("#CCCCCC")
                    for algorithm in self.algorithm[level]:
                        self.printAlgorithmInfo(algorithm[1], level)
                        path = algorithm[0]((self.ROW, self.COL, self.TIME, self.FUEL, self.GRAPH, self.START, self.GOAL), level)
                        self.drawSolutionPath(path)
                        pg.time.delay(300)
                    level = 0
            if (level == 4):
                    self.screen.fill('#CCCCCC')
                    self.printAlgorithmInfo(self.algorithm[4][0][1], level)
                    paths, goals = self.algorithm[4][0][0]((self.ROW, self.COL, self.TIME, self.FUEL, self.GRAPH, self.START, self.GOAL), self.STARTS, self.GOALS)
                    self.drawSolutionForLv4(paths, goals)
                    print("Debug")
                    print(paths)
                    print(goals)
                    level = 0
            pg.display.flip()
            self.clock.tick(60)

#Get information

main = Game(PROBLEM)
main.run()








    