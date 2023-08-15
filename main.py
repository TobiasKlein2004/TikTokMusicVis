import pygame
import random

pygame.init()

# Constant Variables
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700
FPS = 30
PLAYER_SIZE = 20
PLAYER_SPEED = 10

# colors
BACKGROUND_COLOR = (0,0,0)
PLAYER_COLOR = (255,0,0)
WALL_COLOR = (0,0,255)


pygame.display.set_caption("Musik Game")
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_WIDTH))


class Player():
    def __init__(self, size, pos, direction, speed):
        self.size = size
        self.x, self.y = pos
        self.direction = direction
        self.speed = speed
    
    def draw(self):
        match self.direction:
            case 0:
                self.y -= 1*self.speed
            case 45:
                self.x += 1*self.speed
                self.y -= 1*self.speed
            case 90:
                self.x += 1*self.speed
            case 135:
                self.x += 1*self.speed
                self.y += 1*self.speed
            case 180:
                self.y += 1*self.speed
            case 225:
                self.y += 1*self.speed
                self.x -= 1*self.speed
            case 270:
                self.x -= 1*self.speed
            case 315:
                self.x -= 1*self.speed
                self.y -= 1*self.speed

        pygame.draw.rect(screen, PLAYER_COLOR, pygame.Rect(self.x, self.y, self.size, self.size))
    
    def changeDirection(self, direction, wallDir):
        acceptedDirections = [0, 45, 90, 135, 180, 225, 270, 315]
        standingOpposits = [(45, 315), (135, 225), (90, 270)]
        layingOpposits = [(45, 135), (315, 225), (0, 180)]

        if direction not in acceptedDirections:
            print("(Error) Unaccepted direction value: " + str(direction))
            raise Exception
        
        print("Current Dir.: " + str(direction))

        tempDir = 0
        if wallDir == 0:    #aka standing
            print("STANDING - - - - - - - - - - -")
            for pair in standingOpposits:
                if pair[0] == direction:
                    tempDir = pair[1]
                elif pair[1] == direction:
                    tempDir = pair[0]
        elif wallDir == 1:    #aka laying
            print("LAYING - - - - - - - - - - -")
            for pair in layingOpposits:
                if pair[0] == direction:
                    tempDir = pair[1]
                elif pair[1] == direction:
                    tempDir = pair[0]
        
        self.direction = tempDir
    
    def formatDirection(self, direction):
        if self.direction + direction < 0:
            return -1*(self.direction + direction)
        elif self.direction + direction > 360:
            print(self.direction + direction - 360)
            return (self.direction + direction) - 360
        elif self.direction + direction == 360:
            return 0
        else: 
            return self.direction + direction
    
    def checkCollision(self, walls):
        neighbors = [(self.x - 1, self.y), (self.x, self.y - 1), (self.x + 1, self.y), (self.x, self.y + 1)]
        for neighbor in neighbors:
            for wall in walls:
                info = wall.info()
                if neighbor in info[3]:    #aka neighbor in the area/pixels of wall
                    self.changeDirection(self.direction, info[2])

class Wall():
    def __init__(self, size, pos, direction):
        self.sizeX, self.sizeY = size
        self.x, self.y = pos
        self.direction = direction
    
    def draw(self):
        pygame.draw.rect(screen, WALL_COLOR, pygame.Rect(self.x, self.y, self.sizeX, self.sizeY))
    
    def getPixels(self):
        res = []
        for i in range(self.sizeY):
            for j in range(self.sizeX):
                res.append((j + self.x, i + self.y))
        return res

    def info(self):
        return [(self.x, self.y), (self.sizeX, self.sizeY), self.direction, self.getPixels()]


def drawWalls(walls):
    for wall in walls:
        wall.draw()

player = Player(PLAYER_SIZE, (200, 500), 315, PLAYER_SPEED)

# wall = wall((width, height), (xPos, yPos), orientation) <- 0 standing, 1 laying
wall1 = Wall((100, 700), (0, 0), 0)
wall2 = Wall((100, 700), (600, 0), 0)
wall3 = Wall((700, 100), (0, 0), 1)
wall4 = Wall((700, 100), (0, 600), 1)
Walls = [wall1, wall2, wall3, wall4]

running = True

while running == True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # redraw
    screen.fill(BACKGROUND_COLOR)
    player.draw()
    drawWalls(Walls)

    # game Logic
    player.checkCollision(Walls)

    # refresh
    pygame.display.update()

    # set fps
    pygame.time.Clock().tick(FPS)

pygame.quit()

