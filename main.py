import pygame
import random
import math

pygame.init()

# Constant Variables
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700
FPS = 10
PLAYER_SIZE = 20
PLAYER_SPEED = 2            #higher means faster
PLAYER_STEPS = 200             #lower means faster
PLAYER_START_DIRECTION = 300

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
    
    def drawPlayerBox(self, pixels):
        for pixel in pixels:
            pygame.draw.rect(screen, (random.choice(range(0, 255)), random.choice(range(0, 255)), random.choice(range(0, 255))), pygame.Rect(pixel[0], pixel[1], 1, 1))
    
    def draw(self, walls):
        targetX, targetY = self.angleToCoordinats(self.direction)
        targetX = round(targetX * 700)
        targetY = round(targetY * 700)
        #print("X Target: " + str(targetX) + "  |  Y Target: " + str(targetY))

        targetX_Distance = targetX - self.x
        targetY_Distance = targetY - self.y
        #print("X Distance: " + str(targetX_Distance) + "  |  Y Distance: " + str(targetY_Distance))

        self.x += targetX_Distance / PLAYER_STEPS * PLAYER_SPEED
        self.y += targetY_Distance / PLAYER_STEPS * PLAYER_SPEED

        pgx, pgy = toPygameCoordinates((self.x, self.y)) #PyGameX and PyGameY (convert center based coords to topleft based coords)

        self.collisionCheck(walls, round(pgx), round(pgy))

        playerPixels = []
        for i in range(round(pgy) - round(self.size / 2), round(pgy) + round(self.size / 2)):
            for j in range(round(pgx) - round(self.size / 2), round(pgx) + round(self.size / 2)):
                playerPixels.append((j,i))

        self.drawPlayerBox(playerPixels)
        #pygame.draw.rect(screen, PLAYER_COLOR, pygame.Rect(pgx - (self.size / 2), pgy - (self.size / 2), self.size, self.size))
        pygame.draw.line(screen, (255, 255, 255), (pgx, pgy), (pgx + targetX, pgy + targetY))
    
    def angleToCoordinats(self, angle):
        radiants = -1*((angle - 180) * (math.pi / 180))   # make 0deg uplooking and going clockwise
        x = math.sin(radiants)
        y = math.cos(radiants)
        return (x, y)

    def updateAngle(self, angle):
        self.direction = angle
    
    # Physics: Collision
    def collisionCheck(self, walls, x, y):
        colOffset = self.size // 2
        col1, col2, col3, col4 = (x-colOffset, y), (x+colOffset, y), (x, y-colOffset), (x, y+colOffset)
        colliders = {
                        "left": col1, 
                        "right": col2,
                        "top": col3, 
                        "bottom": col4
                    }
        for wall in walls:
            for col in colliders:
                if colliders[col] in wall.getPixels():
                    print("Collision: " + col)
                    match col:
                        case "bottom":
                            if self.direction < 180:
                                outgoingAngle = 90 - (self.direction - 90)
                            elif self.direction > 180:
                                outgoingAngle = 360 - (self.direction - 180)
                            else:
                                outgoingAngle = 0
                            self.updateAngle(outgoingAngle)
                        case "top":
                            if 0 < self.direction < 90:
                                outgoingAngle = 180 - self.direction
                            elif 270 < self.direction < 360:
                                outgoingAngle = 270 - (self.direction - 270)
                            else:
                                outgoingAngle = 180
                            self.updateAngle(outgoingAngle)
                        case "left":
                            if self.direction < 270:
                                outgoingAngle = 180 - (self.direction - 180)
                                print("IN: " + str(self.direction) + " - OUT: " + str(outgoingAngle))
                            elif self.direction > 270:
                                outgoingAngle = 360 - self.direction
                                print("IN: " + str(self.direction) + " - OUT: " + str(outgoingAngle))
                            else:
                                outgoingAngle = 90
                            self.updateAngle(outgoingAngle)
                        case "right":
                            if self.direction > 90:
                                outgoingAngle = 180 + (180 - self.direction)
                                print("IN: " + str(self.direction) + " - OUT: " + str(outgoingAngle))
                            elif self.direction < 90:
                                outgoingAngle = 360 - self.direction
                                print("IN: " + str(self.direction) + " - OUT: " + str(outgoingAngle))
                            else:
                                outgoingAngle = 270
                            self.updateAngle(outgoingAngle)

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
    
    def getOrientation(self):
        return self.direction

    def info(self):
        return [(self.x, self.y), (self.sizeX, self.sizeY), self.direction, self.getPixels()]


def drawWalls(walls):
    for wall in walls:
        wall.draw()

player = Player(PLAYER_SIZE, (250, -250), PLAYER_START_DIRECTION, PLAYER_SPEED)

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
    player.draw(Walls)
    drawWalls(Walls)

    # game Logic
    #if counter % FPS == 0:
    #    player.updateAngle(random.choice(range(0, 360)))

    # refresh
    pygame.display.update()

    # set fps
    pygame.time.Clock().tick(FPS)

    counter += 1

pygame.quit()

