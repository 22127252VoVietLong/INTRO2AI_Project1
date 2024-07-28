import pygame as pg
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
                    "togglehelp": pg.Rect(600, 0, 400, 200),
                    "eventbox": pg.Rect(200, 0, 400, 200),
                    "simstat": pg.Rect(0, 200, 200, 600)}
        self.HUDFrame = pg.image.load("img/background/hud.png")
        
        #Problem material
        self.color = {-1:(1,1,1),"S": (0, 241, 29), 1:(239, 127, 0), 0: (255,255,255)  , "G": (255, 59, 35), "F": (0, 121, 255)}
        self.ROW, self.COL, self.TIME, self.FUEL, self.GRAPH, self.START, self.GOAL, self.STARTS, self.GOALS = problem
        self.gut = 5
        self.algorithm = {1: [(BFS, "BFS") , (DFS, "DFS") , (UCS, "UCS"), (GBFS, "GBFS") , (A_star, "A*") ]
                          , 2: [(A_star_level_2, "Super A* 2"), ]
                          , 3: [(A_star_level_3, "Super A* 3"), ]
                          , 4:[(Level4MultiAgent, "Level 4 Search")]}
        self.cellW = min(min(60, max(self.HUD["canvas"].size[0]//self.ROW, 36) ) - self.gut *2, min(60, max(self.HUD["canvas"].size[1]//self.COL, 36 )) - self.gut *2)
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
    
    def drawText(self, text, pos, font = 24, color = (0,0,0)):
        font = pg.font.Font("Oswald-Regular.ttf", font)
        text = font.render(text, True, (0,0,0))
        rect = text.get_rect()
        rect.left = pos[0]
        rect.top  = pos[1]
        self.window.blit(text, rect)

    def drawCurrentCursor(self, pos, color):
        offsetX, offsetY = self.getBoardOffsetOnCanvas()
        curW, curH = 18, 18
        curPos = (pos[1]*(self.cellW + self.gut) +  offsetX + (self.cellW - curW)//2, pos[0]*(self.cellH + self.gut) + offsetY  + (self.cellH - curH)//2)
        pg.draw.rect(self.window, color, pg.Rect(curPos, (curW, curH)), 3)

    def drawCellContent(self, content, pos:tuple):
        offsetX, offsetY = self.getBoardOffsetOnCanvas()
        if (content != "" and content != "0" and content != "-1"):
            font = pg.font.Font("Oswald-Regular.ttf", 20)
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
        pg.display.flip()


    def drawToggleHelp(self):
        font = pg.font.Font("Oswald-Regular.ttf", 24)
        message = ["In simulation control:", "    A: Auto On/Off", "    N: Next round", "    R: Reset run", "    Q: Next Algo / Quit (last Search)"]
        toggleoffset = self.HUD["togglehelp"].left
        for i in range(len(message)):
            text = font.render(message[i], True, "#000000")
            self.window.blit(text, (toggleoffset, self.HUD["togglehelp"].top + (i)*(36) + 12))
        pg.display.flip()


    def resetBoard(self, level):
        for i in range(self.ROW):
            for j in range(self.COL):
                cellColor = self.getColor(self.GRAPH[i][j])
                content = str(self.GRAPH[i][j])
                if (level == 1):
                    if (content == "S" or content == "G" or content == "-1" or content == "0"):
                        self.drawBoardCell(content, (i,j), "#000000", cellColor)
                    else:
                        content = "0"
                        self.drawBoardCell(content, (i,j), "#000000", self.getColor(0))
                elif (level == 2):
                    if (content[0] == 'F' or (content[0] == 'S' and content != "S") or  (content[0] == 'G' and content != "G")): 
                        content = "0"
                        self.drawBoardCell(content, (i,j), "#000000", self.getColor(0))
                    else:
                        self.drawBoardCell(content, (i,j), "#000000", cellColor)
                elif (level == 3):
                    if ((content[0] == 'S' and content != "S") or  (content[0] == 'G' and content != "G")):
                        content = "0"
                        self.drawBoardCell(content, (i,j), "#000000", self.getColor(0))
                    else:
                        self.drawBoardCell(content, (i,j), "#000000", cellColor)
                else:
                    self.drawBoardCell(content, (i,j), "#000000", cellColor)

                       
        pg.display.flip()
    # def 
    def showMenu(self):
        for i in range(4):
            size = self.levelbuttons[i].getSize()
            level  = self.levelbuttons[i].draw(self.window, (self.winW -  size[0])/2, (i+1)*(size[1] + 70))
            if level > 0:
                break
        return level
    
   

    def drawIngameStat(self, key=str, value=int):
        offsetX, offsetY = self.HUD["simstat"].topleft
        self.drawText("Time:", (offsetX + 24, offsetY + 24))
        self.drawText("Fuel:", (offsetX + 24, offsetY + 24 + 2*36 + 12))
        if (key == "time" and value >= 0):
            pg.draw.rect(self.window,"#CCCCCC" , pg.Rect((offsetX + 24, offsetY + 24 + 36), (150, 36)))
            pg.display.flip()
            self.drawText(str(value), (offsetX + 24, offsetY + 24 + 36))
        if (key == "S" or key == "S0"):
            pg.draw.rect(self.window,"#CCCCCC" , pg.Rect((offsetX + 24, offsetY + 24 + 2*36 + 12 + 1*36), (150, 36)))
            pg.display.flip()
            self.drawText(f"S: {str(value)}", (offsetX + 24, offsetY + 24 + 2*36 + 12 + 1*36))
        if (key == "S1"):
            pg.draw.rect(self.window,"#CCCCCC" , pg.Rect((offsetX + 24, offsetY + 24 + 2*36 + 12 + 2*36), (150, 36)))
            pg.display.flip()
            self.drawText(f"{key}: {str(value)}", (offsetX + 24, offsetY + 24 + 2*36 + 12 + 2*36))
        if (key == "S2"):
            pg.draw.rect(self.window,"#CCCCCC" , pg.Rect((offsetX + 24, offsetY + 24 + 2*36 + 12 + 3*36), (150, 36)))
            pg.display.flip()
            self.drawText(f"{key}: {str(value)}", (offsetX + 24, offsetY + 24 + 2*36 + 12 + 3*36))
        if (key == "S3"):
            pg.draw.rect(self.window,"#CCCCCC" , pg.Rect((offsetX + 24, offsetY + 24 + 2*36 + 12 + 4*36), (150, 36)))
            pg.display.flip()
            self.drawText(f"{key}: {str(value)}", (offsetX + 24, offsetY + 24 + 2*36 + 12 + 4*36))
        if (key == "S4"):
            pg.draw.rect(self.window,"#CCCCCC" , pg.Rect((offsetX + 24, offsetY + 24 + 2*36 + 12 + 5*36), (150, 36)))
            pg.display.flip()
            self.drawText(f"{key}: {str(value)}", (offsetX + 24, offsetY + 24 + 2*36 + 12 + 5*36))
        if (key == "S5"):
            pg.draw.rect(self.window,"#CCCCCC" , pg.Rect((offsetX + 24, offsetY + 24 + 2*36 + 12 + 6*36), (150, 36)))
            pg.display.flip()
            self.drawText(f"{key}: {str(value)}", (offsetX + 24, offsetY + 24 + 2*36 + 12 + 6*36))
        if (key == "S6"):
            pg.draw.rect(self.window,"#CCCCCC" , pg.Rect((offsetX + 24, offsetY + 24 + 2*36 + 12 + 7*36), (150, 36)))
            pg.display.flip()
            self.drawText(f"{key}: {str(value)}", (offsetX + 24, offsetY + 24 + 2*36 + 12 + 7*36))
        if (key == "S7"):
            pg.draw.rect(self.window,"#CCCCCC" , pg.Rect((offsetX + 24, offsetY + 24 + 2*36 + 12 + 8*36), (150, 36)))
            pg.display.flip()
            self.drawText(f"{key}: {str(value)}", (offsetX + 24, offsetY + 24 + 2*36 + 12 + 8*36))
        if (key == "S8"):
            pg.draw.rect(self.window,"#CCCCCC" , pg.Rect( (offsetX + 24, offsetY + 24 + 2*36 + 12 + 9*36), (150, 36)))
            pg.display.flip()
            self.drawText(f"{key}: {str(value)}", (offsetX + 24, offsetY + 24 + 2*36 + 12 + 9*36))
        if (key == "S9"):
            pg.draw.rect(self.window,"#CCCCCC" , pg.Rect((offsetX + 24, offsetY + 24 + 2*36 + 12 + 10*36), (150, 36)))
            pg.display.flip()
            self.drawText(f"{key}: {str(value)}", (offsetX + 24, offsetY + 24 + 2*36 + 12 + 10*36))
        pg.display.flip()
            
            
    def drawSolutionPath(self, path, level):

        #Simulation stats initialize
        run = True
        draw = False
        simtime = self.TIME
        simfuel = self.FUEL
        booth = 0
        move = False
        hasold = False
        self.drawIngameStat("time", simtime)
        self.drawIngameStat("S", simfuel)

        index = 0
        cellColor = (204, 204, 204)
        oldColor = (0, 255, 255)
        oldstep = []
        mode = {0: False, 1:True}
        
        while run:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    return False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_q:
                        return True
                    if event.key == pg.K_r:
                        draw = False
                        index = 0
                        simtime = self.TIME
                        simfuel = self.FUEL
                        booth = 0
                        move = False
                        oldstep.clear()
                        hasold = False
                        
                    if event.key == pg.K_n:
                        mode[0] = True
                    if event.key == pg.K_a:
                        mode[1] = not mode[1]
            if (path[0] != -1):
                if draw == False:
                    pg.draw.rect(self.window, "#CCCCCC", pg.Rect(210, 210, 780, 580))
                    pg.draw.rect(self.window, "#CCCCCC", pg.Rect(210, 10, self.HUD["eventbox"].size[0] - 20, self.HUD["eventbox"].size[1] - 20))
                    self.resetBoard(level)
                try:
                    step = path[index]
                    content = str(self.GRAPH[step[0]][step[1]])
                    #Get time booth or fuel value
                    if (level >= 2):
                        if (content.isdigit() and content != "0" and booth == 0 and move ):
                            booth = int(content)
                            move = False
                    if (level == 3):
                        if (content[0] == 'F' and booth == 0 and move):
                            booth = int(content[1:])
                            move = False
                            simfuel = self.FUEL + 1

                    if len(oldstep) > 0 and oldstep[-1] != step:
                        temp = oldstep.pop()
                        if level == 3:
                            simfuel -= 1
                        self.drawPassedCellLine(temp, step, oldColor)

                    self.drawIngameStat("time", simtime)
                    self.drawIngameStat("S", simfuel)
                    self.drawCurrentCursor(step,cellColor)
                    if(mode[0] or mode[1]):
                        if (level == 2 or level == 3):
                            simtime -= 1
                        if(booth == 0):
                            oldstep.append(step)
                            move = True
                            index+=1
                        else:
                            booth -= 1
                        mode[0] = False
                except:
                    if index == len(path):
                        self.drawText("S reached goal", ((self.HUD["eventbox"].left + 24), (self.HUD["eventbox"].size[1] - 36) // 2))
                        pg.display.flip()
                    continue
            else:
                self.drawText("S do not have a path", ((self.HUD["eventbox"].left + 24), ((self.HUD["eventbox"].size[1] - 36) // 2)))
                pg.display.flip()
                

                
            self.clock.tick(4)
            pg.display.flip()
            pg.time.delay(100)
            draw = True
        return

    
    def drawSolutionForLv4(self, path: list, goals: list, flag):
        #Initialize simulation stats
        run = True
        resetDebug = True
        simtime = self.TIME
        simfuel = [self.FUEL] * len(path)
        self.drawIngameStat("time", simtime)
        for i in range(len(path)):
            self.drawIngameStat(f"S{i}", self.FUEL)
        stepindex = [0]*len(path) #Regulate step in each path
        startindex = 0 #regulate each starts I
        endPath = [False]*len(path)
        if (flag == -1):
            endPath[0] = True
        oldstep = dict()
        hasold = dict()
        cellColor = (204, 204, 204)
        oldcellColor = [(255, 0, 0), 
                        (255, 165, 0), 
                        (255, 255, 0), 
                        (0, 128, 0), 
                        (0, 0, 255), 
                        (75, 0, 130), 	
                        (255, 0, 255), 
                        (0, 255, 255), 
                        (238, 130, 238),
                        (227, 157, 159)]
        mode = {0: True, 1: True} #0 is Manual, #1 is Auto
        #Children loop
        while run:
            if (resetDebug):
                startindex = 0 #regulate each starts I
                stepindex = [0] * len(path)
                simtime = self.TIME
                simfuel = [self.FUEL] * len(path)
                endPath = [False]*len(path)
                if (flag == -1):
                    endPath[0] = True
                count = 0
                oldstep.clear()
                hasold.clear()
                self.resetBoard(4)
                resetDebug = False
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    # sys.exit()
                    return False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_q:
                        return True
            
                    if event.key == pg.K_r:
                        draw = False
                        # stepindex = 0 #Regulate step in each path
                        startindex = 0 #regulate each starts I
                        stepindex = [0] * len(path)
                        simtime = self.TIME
                        simfuel = [self.FUEL] * len(path)
                        endPath = [False]*len(path)
                        if (flag == -1):
                            endPath[0] = True
                        count = 0
                        oldstep.clear()
                        hasold.clear()
                        pg.draw.rect(self.window, "#CCCCCC", pg.Rect(210, 210, 780, 580))
                        pg.draw.rect(self.window, "#CCCCCC", pg.Rect(210, 10, self.HUD["eventbox"].size[0] - 20, self.HUD["eventbox"].size[1] - 20))
                        self.drawIngameStat("time", simtime)
                        for i in range(len(path)):
                            self.drawIngameStat(f"S{i}", self.FUEL)
                        self.resetBoard(4)
                    if event.key == pg.K_n:
                        mode[0] = True
                    if event.key == pg.K_a:
                        mode[1] = not mode[1]
            # pop = False
            if (startindex == len(path)): # Pass the last start
                if False in endPath:
                    simtime -= 1
                    startindex = 0
                    mode[0] = False
                
                elif flag == -1:
                    self.drawText("S didnt reached goal", ((self.HUD["eventbox"].left + 24), ((self.HUD["eventbox"].size[1] - 36) // 2)))
                    pg.display.flip()
                else:
                    self.drawText("S reached goal", ((self.HUD["eventbox"].left + 24), (self.HUD["eventbox"].size[1] - 36) // 2))
                    pg.display.flip()

            try:    
                step = path[startindex][stepindex[startindex]]
                content = str(self.GRAPH[step[0]][step[1]])
                if (content[0] == 'F'):
                    simfuel[startindex] = self.FUEL + 1
                if (startindex in oldstep):
                    if (oldstep[startindex] != step and hasold[startindex]):
                        temp = oldstep[startindex]
                        simfuel[startindex] -= 1
                        hasold[startindex] = False
                        self.drawPassedCellLine(temp, step, oldcellColor[startindex])
                self.drawCurrentCursor( step , cellColor)
                self.drawIngameStat("time", simtime)
                self.drawIngameStat(f"S{startindex}", simfuel[startindex])
                self.clock.tick(10)
                if (step == goals[startindex][0]):
                    for newgoal in goals[startindex]:
                        if str(self.GRAPH[newgoal[0]][newgoal[1]])[0] != "G":
                            # self.GRAPH[newgoal[0]][newgoal[1]] =  # Added Goal
                            self.drawBoardCell(f"GX{count}", newgoal, (0,0,0), self.getColor("G"))
                            count += 1
                pg.display.flip()
                pg.time.delay(100)
                if (mode[0] or mode[1]):
                    oldstep[startindex] = step
                    hasold[startindex] = True
                    stepindex[startindex] += 1
                    if stepindex[startindex] == len(path[startindex]):
                        endPath[startindex] = True
                    startindex += 1 #Turn for next start
            except:
                if startindex < len(path):
                    startindex+=1
                continue
            # draw = True
        # self.GRAPH = copy.deepcopy(copyGraph)
        return True

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
                    return
            self.window.fill("#CCCCCC")
            level = self.showMenu()
            if (level > 0 and level < 4):
                    self.window.fill("#CCCCCC") 
                    pg.display.flip()
                    for algorithm in self.algorithm[level]:
                        self.window.blit(self.HUDFrame,(0,0))
                        self.drawToggleHelp()
                        self.resetBoard(level)
                        self.drawInfo(algorithm[1], level)
                        path = algorithm[0]((self.ROW, self.COL, self.TIME, self.FUEL, self.GRAPH, self.START, self.GOAL))
                        run = self.drawSolutionPath(path, level)
                        if (run == False):
                            return
                        pg.time.delay(300)
                    level = 0
            if (level == 4):
                    self.window.fill("#CCCCCC")
                    self.window.blit(self.HUDFrame,(0,0))
                    self.drawToggleHelp()
                    self.resetBoard(level)
                    self.drawInfo(self.algorithm[4][0][1], level)
                    pg.display.flip()
                    paths, goals, flag = self.algorithm[4][0][0]((self.ROW, self.COL, self.TIME, self.FUEL, self.GRAPH, self.START, self.GOAL), self.STARTS, self.GOALS)
                    run = self.drawSolutionForLv4(paths, goals, flag)
                    if (run == False):
                            return
                    level = 0
            pg.display.flip()
            self.clock.tick(60)


def main():
    filepath = input("Problem file path (0 to exit program): ")
    
    while (filepath != "0"):
        print("Start initializing problem...")
        pg.init()
        pg.font.init()
        ROW, COL, TIME, FUEL, GRAPH, STARTS, GOALS = read_file(filepath)
        START = STARTS[0]
        GOAL = GOALS[0]
        PROBLEM = (ROW, COL, TIME, FUEL, GRAPH, START, GOAL, STARTS, GOALS)
        sim = Simulator(winW, winH, PROBLEM)
        print("Run simulation")
        print("If you want another input, please turn off the Simulation window")
        sim.run()
        filepath = input("Problem file path (0 to exit program): ")

main()