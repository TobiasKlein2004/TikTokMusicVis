import pygame
import random
import math
import librosa
import time
import playsound
import os
#import librosa.display
#import matplotlib.pyplot as plt

# Constant Variables
DEBUG = True
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700
FPS = 60
PLAYER_SIZE = 20
PLAYER_SPEED = 5            #higher means faster (PLAYER_STEPS % PLAYER_SPEED shoud be 0)
PLAYER_STEPS = 200             #lower means faster
PLAYER_START_DIRECTION = 30
PLAYER_START_POSITION = (0, 0)
PATH_PROJECTION_LENGHT = 700
ANGLE_NOISE = 5

# colors
BACKGROUND_COLOR = (0,0,0)
PLAYER_COLOR = (255,0,0)
WALL_COLOR = (0,0,255)

# Audio Stuff
ONSETS = []
AUDIO_FILE_PATH = input("- - - Audio path: audio/")
if AUDIO_FILE_PATH == "":
    AUDIO_FILE_PATH = "1.wav"
BEATMAP = input("- - - Beatmap Path (Enter for none): ")

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


def playOnsets(onsets):
    last = 0
    for onset in onsets:
        time.sleep(float(onset - last))
        last = float(onset)
        print("bam")





pygame.init()

pygame.display.set_caption("Musik Game")
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_WIDTH))


# Debug - - - - - - - - - - - - - - - - - -
def debugDraw(target, pos):
    # draw grid
    gridgapsize = PLAYER_SIZE
    linecolor = (50, 50, 50)
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
    
    def draw(self, walls):
        #print("X Target: " + str(self.targetX) + "  |  Y Target: " + str(self.targetY))
        #print("X Distance: " + str(self.dX) + "  |  Y Distance: " + str(self.dY))
        if (round(self.x), round(self.y)) != (self.targetX, self.targetY):
            self.x += self.StepSize[0] * PLAYER_SPEED
            self.y += self.StepSize[1] * PLAYER_SPEED

        pgx, pgy = toPygameCoordinates((self.x, self.y)) #PyGameX and PyGameY (convert center based coords to topleft based coords)

        self.collisionCheck(walls, round(pgx), round(pgy))

        playerPixels = []
        for i in range(round(pgy) - round(self.size / 2), round(pgy) + round(self.size / 2)):
            for j in range(round(pgx) - round(self.size / 2), round(pgx) + round(self.size / 2)):
                playerPixels.append((j,i))

        # Actual drawing
        if DEBUG:
            debugDraw((self.targetX, self.targetY), (pgx, pgy))
        self.drawPlayerBox(playerPixels)
        for wall in walls:
            wall.draw()
        #pygame.draw.line(screen, (255, 255, 255), (pgx, pgy), (pgx + self.targetX, pgy + self.targetY))
    
    def angleToCoordinats(self, angle):
        radiants = -1*((angle - 180) * (math.pi / 180))   # make 0deg uplooking and going clockwise
        x = math.sin(radiants)
        y = math.cos(radiants)
        return (x, y)

    def updateAngle(self, angle):
        if ANGLE_NOISE != 0:
            self.direction = angle + random.choice(range(-ANGLE_NOISE, ANGLE_NOISE))
        else:
            self.direction = angle
        self.targetX, self.targetY = round(self.angleToCoordinats(self.direction)[0] * PATH_PROJECTION_LENGHT), round(self.angleToCoordinats(self.direction)[1] * PATH_PROJECTION_LENGHT)
        self.dX, self.dY = self.calcDistance((self.x, self.y), (self.targetX, self.targetY))
        self.StepSize = (self.dX / PLAYER_STEPS, self.dY / PLAYER_STEPS)
    
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
                            print("IN: " + str(self.direction) + " - OUT: " + str(outgoingAngle))
                            self.updateAngle(outgoingAngle)
                        case "top":
                            if 0 < self.direction < 90:
                                outgoingAngle = 180 - self.direction
                            elif 270 < self.direction < 360:
                                outgoingAngle = 270 - (self.direction - 270)
                            else:
                                outgoingAngle = 180
                            print("IN: " + str(self.direction) + " - OUT: " + str(outgoingAngle))
                            self.updateAngle(outgoingAngle)
                        case "left":
                            if self.direction < 270:
                                outgoingAngle = 180 - (self.direction - 180)
                            elif self.direction > 270:
                                outgoingAngle = 360 - self.direction
                            else:
                                outgoingAngle = 90
                            print("IN: " + str(self.direction) + " - OUT: " + str(outgoingAngle))
                            self.updateAngle(outgoingAngle)
                        case "right":
                            if self.direction > 90:
                                outgoingAngle = 180 + (180 - self.direction)
                            elif self.direction < 90:
                                outgoingAngle = 360 - self.direction
                            else:
                                outgoingAngle = 270
                            print("IN: " + str(self.direction) + " - OUT: " + str(outgoingAngle))
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
    




# Sound - - - - - - - - - - - - - - - - - - - - - - - -
pygame.mixer.music.load('audio/' + AUDIO_FILE_PATH)
def playMusic():
    pygame.mixer.music.play(1)
    # time_since_start (every frame += time.deltaTime)
    # current_onset (int that represents the position of the current onset)
    # if time_since_start >= ONSETS[current_onset]:
    #       current_onset += 1
    #       set wall color to random color
# Sound End - - - - - - - - - - - - - - - - - - - - - - 

# Game Objects - - - - - - - - - - - - - - - - - - - - -
player = Player(PLAYER_SIZE, PLAYER_START_POSITION, PLAYER_START_DIRECTION, PLAYER_SPEED)

# wall = wall((width, height), (xPos, yPos), orientation) <- 0 standing, 1 laying
wall1 = Wall((50, 700), (0, 0), 0)
wall2 = Wall((50, 700), (650, 0), 0)
wall3 = Wall((700, 50), (0, 0), 1)
wall4 = Wall((700, 50), (0, 650), 1)
Walls = [wall1, wall2, wall3, wall4]
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
    
    # redraw
    screen.fill(BACKGROUND_COLOR)

    # game Logic
    keys=pygame.key.get_pressed()
    if keys[pygame.K_w]:
        gamestart = True
        time_since_start = 0
        playMusic()

    if gamestart:
        player.draw(Walls)
        time_since_start_seconds = float(time_since_start / 1000)
        print(time_since_start_seconds)
        if current_onset <= len(ONSETS) - 1:
            if time_since_start_seconds >= ONSETS[current_onset]:
                print(" - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
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

pygame.quit()

