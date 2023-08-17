import pygame
import random
import math

pygame.init()

# Constant Variables
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700
FPS = 10
PLAYER_SIZE = 20
PLAYER_SPEED = 1             #higher means faster
PLAYER_STEPS = 200             #lower means faster
PLAYER_START_DIRECTION = 30

# colors
BACKGROUND_COLOR = (0,0,0)
PLAYER_COLOR = (255,0,0)
WALL_COLOR = (0,0,255)


pygame.display.set_caption("Musik Game")
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_WIDTH))


def toPygameCoordinates(coords):
    return (coords[0] + WINDOW_WIDTH / 2, coords[1] + WINDOW_HEIGHT / 2)

class Player():
    def __init__(self, size, pos, direction, speed):
        self.size = size
        self.x, self.y = pos
        self.direction = direction
        self.speed = speed
    
    def draw(self):
        targetX, targetY = self.angleToCoordinats(self.direction)
        targetX = round(targetX * 700)
        targetY = round(targetY * 700)
        print("X Target: " + str(targetX) + "  |  Y Target: " + str(targetY))

        targetX_Distance = targetX - self.x
        targetY_Distance = targetY - self.y
        print("X Distance: " + str(targetX_Distance) + "  |  Y Distance: " + str(targetY_Distance))

        self.x += targetX_Distance / PLAYER_STEPS
        self.y += targetY_Distance / PLAYER_STEPS

        pgx, pgy = toPygameCoordinates((self.x, self.y)) #PyGameX and PyGameY (convert center based coords to topleft based coords)

        pygame.draw.rect(screen, PLAYER_COLOR, pygame.Rect(pgx - (self.size / 2), pgy - (self.size / 2), self.size, self.size))
        pygame.draw.line(screen, (255, 255, 255), (pgx, pgy), (pgx + targetX, pgy + targetY))
    
    def angleToCoordinats(self, angle):
        radiants = -1*((angle - 180) * (math.pi / 180))   # make 0deg uplooking and going clockwise
        x = math.sin(radiants)
        y = math.cos(radiants)
        return (x, y)
    
    def distance(a, b):
        if a > b:
            return b-a
        if b > a:
            return b - a

    def updateAngle(self, angle):
        self.direction = angle

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

player = Player(PLAYER_SIZE, (0, 0), PLAYER_START_DIRECTION, PLAYER_SPEED)

# wall = wall((width, height), (xPos, yPos), orientation) <- 0 standing, 1 laying
wall1 = Wall((50, 700), (0, 0), 0)
wall2 = Wall((50, 700), (650, 0), 0)
wall3 = Wall((700, 50), (0, 0), 1)
wall4 = Wall((700, 50), (0, 650), 1)
Walls = [wall1, wall2, wall3, wall4]

running = True

counter = 0
while running == True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # redraw
    screen.fill(BACKGROUND_COLOR)
    player.draw()
    drawWalls(Walls)

    # game Logic

    # refresh
    pygame.display.update()

    # set fps
    pygame.time.Clock().tick(FPS)

    counter += 1

pygame.quit()

