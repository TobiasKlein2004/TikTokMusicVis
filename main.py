import pygame
import random
import math
import librosa
import time
import os
#import librosa.display
#import matplotlib.pyplot as plt

# Constant Variables
DEBUG = True
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700
FPS = 60
PLAYER_SIZE = 20
X_SPEED = 3
PLAYER_SPEED = 1            #higher means faster (PLAYER_STEPS % PLAYER_SPEED shoud be 0)
PLAYER_STEPS = 200             #lower means faster
PLAYER_START_DIRECTION = 30
PLAYER_START_POSITION = (0, 0)
PATH_PROJECTION_LENGHT = 700
ANGLE_NOISE = 5

WORLD_OFFSET = (0, 0)
WALL_SIZE = (40, 10)

# colors
BACKGROUND_COLOR = (0,0,25)
PLAYER_COLOR = (255,0,0)
WALL_COLOR = (0,0,255)

# Audio Stuff
ONSETS = []
AUDIO_FILE_PATH = input("- - - Audio path: audio/")
if AUDIO_FILE_PATH == "":
    AUDIO_FILE_PATH = "1.wav"
MOVEMENT_DATA = input("- - - Use precomputed WorldData (Yes or Enter for No): ")
usingBeatmap = True
BEATMAP = ""
if MOVEMENT_DATA == "":
    BEATMAP = input("- - - Beatmap Path (Enter for none): ")
if MOVEMENT_DATA != "":
    usingBeatmap = False
DURATION = librosa.get_duration(path='audio/'+AUDIO_FILE_PATH)



if BEATMAP == "":
    print("- - - Compute Beatmap ...")
    waveform, samplerate = librosa.load('audio/' + AUDIO_FILE_PATH)
    onset_frames = librosa.onset.onset_detect(y=waveform, sr=samplerate, wait=1, pre_avg=1, post_avg=1, pre_max=1, post_max=1)
    onset_times = librosa.frames_to_time(onset_frames)
    ONSETS = onset_times
    # Write Onsets to Beatmap
    file_name_no_extension, _ = os.path.splitext(AUDIO_FILE_PATH)
    output_name = 'beatmaps/' + file_name_no_extension + '.beatmap.txt'
    with open(output_name, 'wt') as f:
        f.write('\n'.join(['%.4f' % onset_time for onset_time in onset_times]))
else:
    print("- - - Using Beatmap: " + BEATMAP)
    with open('beatmaps/' + BEATMAP) as file:
        for line in file:
            ONSETS.append(float(line))
    print(ONSETS)




pygame.init()

pygame.display.set_caption("Musik Game")
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_WIDTH))


# Debug - - - - - - - - - - - - - - - - - -
def debugDraw(target, pos):
    # draw grid
    gridgapsize = PLAYER_SIZE
    linecolor = (100, 100, 100)
    for i in range(WINDOW_WIDTH):
        if i % gridgapsize == 0:
            pygame.draw.line(screen, linecolor, (i, 0), (i, WINDOW_HEIGHT))
    for i in range(WINDOW_HEIGHT):
        if i % gridgapsize == 0:
            pygame.draw.line(screen, linecolor, (0, i), (WINDOW_WIDTH, i))
    pygame.draw.circle(screen, (255, 165, 0), toPygameCoordinates(target), PLAYER_SIZE / 4)
    pygame.draw.line(screen, (255, 255, 255), pos, toPygameCoordinates(target))
# Debug End - - - - - - - - - - - - - - - -




def toPygameCoordinates(coords):
    return (coords[0] + WINDOW_WIDTH / 2, coords[1] + WINDOW_HEIGHT / 2)

class Player():
    def __init__(self, size, pos, direction, speed):
        self.size = size
        self.x, self.y = pos
        self.direction = direction
        self.speed = speed
        self.targetX, self.targetY = round(self.angleToCoordinats(self.direction)[0] * PATH_PROJECTION_LENGHT), round(self.angleToCoordinats(self.direction)[1] * PATH_PROJECTION_LENGHT)
        self.dX, self.dY = self.calcDistance((self.x, self.y), (self.targetX, self.targetY))
        self.StepSize = (self.dX / PLAYER_STEPS, self.dY / PLAYER_STEPS)
    
    def calcDistance(self, start, target):
        return (target[0] - start[0], target[1] - start[1])

    def drawPlayerBox(self, pixels):
        for pixel in pixels:
            pygame.draw.rect(screen, (random.choice(range(0, 255)), random.choice(range(0, 255)), random.choice(range(0, 255))), pygame.Rect(pixel[0], pixel[1], 1, 1))

    def getStepSize(self):
        return self.StepSize
    
    def getPosition(self):
        return (self.x, self.y)
    
    def draw(self, walls, trackers):
        #print("X Target: " + str(self.targetX) + "  |  Y Target: " + str(self.targetY))
        #print("X Distance: " + str(self.dX) + "  |  Y Distance: " + str(self.dY))
        if (round(self.x), round(self.y)) != (self.targetX, self.targetY):
            self.x += self.StepSize[0] * PLAYER_SPEED
            self.y += self.StepSize[1] * PLAYER_SPEED

        pgx, pgy = toPygameCoordinates((self.x, self.y)) #PyGameX and PyGameY (convert center based coords to topleft based coords)
        #pgx, pgy = toPygameCoordinates((0, 0)) #PyGameX and PyGameY (convert center based coords to topleft based coords)

        global WORLD_OFFSET
        #WORLD_OFFSET = (self.x*-1, self.y*-1)
        WORLD_OFFSET = (0, 0)

        self.collisionCheck(walls, round(pgx), round(pgy))

        playerPixels = []
        for i in range(round(toPygameCoordinates((self.x, self.y))[1]) - round(self.size / 2), round(toPygameCoordinates((self.x, self.y))[1]) + round(self.size / 2)):
            for j in range(round(toPygameCoordinates((self.x, self.y))[0]) - round(self.size / 2), round(toPygameCoordinates((self.x, self.y))[0]) + round(self.size / 2)):
                playerPixels.append((j,i))

        # Actual drawing
        if DEBUG:
            debugDraw((self.targetX, self.targetY), (pgx, pgy))
        self.drawPlayerBox(playerPixels)
        for wall in walls:
            wall.draw()
        for line in trackers:
            line.draw()
        #pygame.draw.line(screen, (255, 255, 255), (pgx, pgy), (pgx + self.targetX, pgy + self.targetY))
    
    def angleToCoordinats(self, angle):
        radiants = -1*((angle - 180) * (math.pi / 180))   # make 0deg uplooking and going clockwise
        x = math.sin(radiants)
        y = math.cos(radiants)
        return (x, y)

    def updateAngle(self, angle):
        if ANGLE_NOISE != 0:
            d = angle + random.choice(range(-ANGLE_NOISE, ANGLE_NOISE))
            if d > 359:
                d = d % 360
            self.direction = d
        else:
            if angle > 359:
                angle = angle % 360
            self.direction = angle
        self.targetX, self.targetY = round(self.angleToCoordinats(self.direction)[0] * PATH_PROJECTION_LENGHT), round(self.angleToCoordinats(self.direction)[1] * PATH_PROJECTION_LENGHT)
        self.dX, self.dY = self.calcDistance((self.x, self.y), (self.targetX, self.targetY))
        self.StepSize = (self.dX / PLAYER_STEPS, self.dY / PLAYER_STEPS)

    # Physics: Collision
    def collisionCheck(self, walls, x, y):
        colOffset = self.size // 2 + 5
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
                    #print("Collision: " + col)
                    match col:
                        case "bottom":
                            if self.direction < 180:
                                outgoingAngle = 90 - (self.direction - 90)
                            elif self.direction > 180:
                                outgoingAngle = 360 - (self.direction - 180)
                            else:
                                outgoingAngle = 0
                            #print("IN: " + str(self.direction) + " - OUT: " + str(outgoingAngle))
                            if MOVEMENT_DATA == "":
                                self.updateAngle(outgoingAngle)
                        case "top":
                            if 0 < self.direction < 90:
                                outgoingAngle = 180 - self.direction
                            elif 270 < self.direction < 360:
                                outgoingAngle = 270 - (self.direction - 270)
                            else:
                                outgoingAngle = 180
                            #print("IN: " + str(self.direction) + " - OUT: " + str(outgoingAngle))
                            if MOVEMENT_DATA == "":
                                self.updateAngle(outgoingAngle)
                        case "left":
                            if self.direction < 270:
                                outgoingAngle = 180 - (self.direction - 180)
                            elif self.direction > 270:
                                outgoingAngle = 360 - self.direction
                            else:
                                outgoingAngle = 90
                            #print("IN: " + str(self.direction) + " - OUT: " + str(outgoingAngle))
                            if MOVEMENT_DATA == "":
                                self.updateAngle(outgoingAngle)
                        case "right":
                            if self.direction > 90:
                                outgoingAngle = 180 + (180 - self.direction)
                            elif self.direction < 90:
                                outgoingAngle = 360 - self.direction
                            else:
                                outgoingAngle = 270
                            #print("IN: " + str(self.direction) + " - OUT: " + str(outgoingAngle))
                            if MOVEMENT_DATA == "":
                                self.updateAngle(outgoingAngle)

# wall = wall((width, height), (xPos, yPos), orientation) <- 0 standing, 1 laying
class Wall():
    def __init__(self, size, pos, direction):
        self.sizeX, self.sizeY = size
        self.x, self.y = toPygameCoordinates(pos)
        self.direction = direction
    
    def draw(self):
        pygame.draw.rect(screen, WALL_COLOR, pygame.Rect(self.x + WORLD_OFFSET[0], self.y + WORLD_OFFSET[1], self.sizeX, self.sizeY))
    
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
Walls = []

class TrackerLine():
    def __init__(self, pos):
        self.x, self.y = pos

    def draw(self):
        x, y = toPygameCoordinates((self.x, self.y))
        pygame.draw.line(screen, (255, 255, 255), (x - 25, y), (x + 25, y))

    def getPos(self):
        return (self.x, self.y)




# Sound - - - - - - - - - - - - - - - - - - - - - - - -
pygame.mixer.music.load('audio/' + AUDIO_FILE_PATH)
def playMusic():
    pygame.mixer.music.play(1)
# Sound End - - - - - - - - - - - - - - - - - - - - - - 

# Onset Positional Tracking - - - - - - - - - - - - - -
def calcOnsetPos(nextOnset, currentTime, player):
    stepSize = player.getStepSize()                    # aka Movement per Frame
    playerPos = player.getPosition()
    timeLeft = (nextOnset*1000) - currentTime
    framesLeft = int(round(timeLeft) / 1000 * FPS)
    # place tracker at playerPos + stepsize*framesLeft
    x = playerPos[0] + stepSize[0]*framesLeft
    y = playerPos[1] + stepSize[1]*framesLeft
    global TrackerLines
    tracker = TrackerLine((x, y))
    TrackerLines.append(tracker)
# Onset Positional Tracking End - - - - - - - - - - - -

def calcWallType(d, wcpx, wcpy):
    res = []
    wsx, wsy = WALL_SIZE
    if d == 0:
        # h(-) top
        wall = Wall((wsx, wsy), (wcpx - wsx//2, wcpy - wsy), 1)
        res.append(wall)
    elif 1 <= d <= 89:
        # h(-) top OR v(|) right
        wall1 = Wall((wsx, wsy), (wcpx - wsx//2, wcpy - wsy), 1)
        wall2 = Wall((wsy, wsx), (wcpx, wcpy - wsx//2), 0)
        res.append(random.choice([wall1, wall2]))
    elif d == 90:
        # v(|) right
        wall = Wall((wsy, wsx), (wcpx, wcpy - wsx//2), 0)
        res.append(wall)
    elif 91 <= d <= 179:
        # h(-) below OR v(|) right
        wall1 = Wall((wsx, wsy), (wcpx - wsx//2, wcpy), 1)
        wall2 = Wall((wsy, wsx), (wcpx, wcpy - wsx//2), 0)
        res.append(random.choice([wall1, wall2]))
    elif d == 180:
        # h(-) below
        wall = Wall((wsx, wsy), (wcpx - wsx//2, wcpy), 1)
        res.append(wall)
    elif 181 <= d <= 269:
        # h(-) below OR v(|) left
        wall1 = Wall((wsx, wsy), (wcpx - wsx//2, wcpy), 1)
        wall2 = Wall((wsy, wsx), (wcpx - wsy, wcpy - wsx//2), 0)
        res.append(random.choice([wall1, wall2]))
    elif d == 270:
        # v(|) left
        wall = Wall((wsy, wsx), (wcpx - wsy, wcpy - wsx//2), 0)
        res.append(wall)
    elif 271 <= d <= 359:
        # h(-) top OR v(|) left
        wall1 = Wall((wsx, wsy), (wcpx - wsx//2, wcpy - wsy), 1)
        wall2 = Wall((wsy, wsx), (wcpx - wsy, wcpy - wsx//2), 0)
        res.append(random.choice([wall1, wall2]))
    
    return res

def loadWorld():
    with open('movement/worldData.txt', 'r') as file:
        lines = file.readlines()
        for line in lines:
            sizeX = int(line[1:line.find(',')])
            sizeY = int(line[line.find(',')+1:line.find(')')])
            line = line[line.find(')')+2:]
            x = float(line[1:line.find(',')])
            y = float(line[line.find(',')+1:line.find(')')])
            line = line[line.find(')')+2:]
            d = int(line)
            global Walls
            Walls.append(Wall((sizeX, sizeY), (x, y), d))
if MOVEMENT_DATA != "":
    loadWorld()

# Game Objects - - - - - - - - - - - - - - - - - - - - -
player = Player(PLAYER_SIZE, PLAYER_START_POSITION, PLAYER_START_DIRECTION, PLAYER_SPEED)


TrackerLines = []
if MOVEMENT_DATA != "":
    # Load Trackerlines
    with open('movement/movementData.txt', 'r') as file:
        lines = file.readlines()
        for line in lines:
            #parse
            x = float(line[1:line.find(',')])
            y = float(line[line.find(',') + 2:line.find(')', 2)])
            TrackerLines.append(TrackerLine((x, y)))
# Game Objects End - - - - - - - - - - - - - - - - - - -


running = True
gamestart = False

time_since_start = 0
current_onset = 0
getTicksLastFrame = 0
while running == True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    if gamestart == True and time_since_start > DURATION*1000:
        running = False
    
    # redraw
    screen.fill(BACKGROUND_COLOR)

    # game Logic
    keys=pygame.key.get_pressed()
    if keys[pygame.K_w]:
        gamestart = True
        time_since_start = 0
        playMusic()

    if gamestart:
        #TODO update Player angle

        player.draw(Walls, TrackerLines)
        time_since_start_seconds = float(time_since_start / 1000)
        if current_onset <= len(ONSETS) - 1:
            print(player.getPosition())
            if time_since_start_seconds >= ONSETS[current_onset]:
                if MOVEMENT_DATA == "":
                    calcOnsetPos(ONSETS[current_onset], time_since_start, player)
                    
                    #spawn block at trackerPos
                    wallColisionPoint = TrackerLines[-1].getPos()
                    print(wallColisionPoint)
                    wcpx, wcpy = wallColisionPoint[0], wallColisionPoint[1]
                    # spawn wall at that point -> check angel of playler to get orientaion of wall
                    Walls.append(calcWallType(player.direction, wcpx, wcpy)[0])

                else:
                    targetPos = TrackerLines[current_onset + 1].getPos()
                    playerPos = player.getPosition()
                    newAngle = math.atan2(targetPos[1]-playerPos[1], targetPos[0]-playerPos[0])*(180/math.pi)+90
                    if newAngle < 0:
                        newAngle = 360 + newAngle
                    player.updateAngle(newAngle)
                WALL_COLOR = (random.choice(range(0, 255)), random.choice(range(0, 255)), random.choice(range(0, 255)))
                current_onset += 1

    # refresh
    pygame.display.update()

    # set fps
    pygame.time.Clock().tick(FPS)
    t = pygame.time.get_ticks()
    # deltaTime in seconds.
    deltaTime = (t - getTicksLastFrame)
    getTicksLastFrame = t
    #time_since_start = pygame.time.get_ticks()
    time_since_start += deltaTime


# Write Turnpositions/WallPositions to file
with open('movement/movementData.txt', 'w') as file:
    for tracker in TrackerLines:
        file.write(str(tracker.getPos()) + '\n')

# Write Wallpositions to file
with open('movement/worldData.txt', 'w') as file:
    for wall in Walls:
        # (width, height), (xPos, yPos), orientation)
        file.write('(' + str(wall.sizeX) + ',' + str(wall.sizeY) + '),(' + str(wall.x) + ',' + str(wall.y) + '),' + str(wall.direction) + '\n')



pygame.quit()

