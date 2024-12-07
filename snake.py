"""Wormy (a Nibbles clone) - By Al Sweigart al@inventwithpython.com
http://inventwithpython.com/pygame - Released under a "Simplified BSD" license
"""
# CHANGE: Docstrings, like the one above, were added throughout.

import random, pygame, sys
from pygame.locals import *

FPS = 15
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
CELLSIZE = 20
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
# CHANGE: New color.
ORANGE    = (255, 128,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0 # syntactic sugar: index of the worm's head

def main():
    """Set some basic variables and alternate between running and game over."""
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Wormy')

    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()


def runGame():
    """Set the enviroment up and run the main game loop."""
    # Set a random start point.
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    wormCoords = [{'x': startx,     'y': starty},
                  {'x': startx - 1, 'y': starty},
                  {'x': startx - 2, 'y': starty}]
    direction = RIGHT

    # CHANGE: Added obstacles.
    rocks = list()
    # Start the apple in a random place.
    # CHANGE: Each getRandomLocation call edited, paramaters changed.
    apple = dict()
    apple = getRandomLocation(wormCoords[HEAD], apple, rocks)
    # CHANGE: Add a score starting at 0
    score = 0

    while True: # main game loop
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if (event.key == K_LEFT or event.key == K_a) and direction != RIGHT:
                    direction = LEFT
                elif (event.key == K_RIGHT or event.key == K_d) and direction != LEFT:
                    direction = RIGHT
                elif (event.key == K_UP or event.key == K_w) and direction != DOWN:
                    direction = UP
                elif (event.key == K_DOWN or event.key == K_s) and direction != UP:
                    direction = DOWN
                elif event.key == K_ESCAPE:
                    terminate()

        # check if the worm has hit itself or the edge
        if wormCoords[HEAD]['x'] == -1 or wormCoords[HEAD]['x'] == CELLWIDTH or wormCoords[HEAD]['y'] == -1 or wormCoords[HEAD]['y'] == CELLHEIGHT:
            return # game over
        for wormBody in wormCoords[1:]:
            if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
                return # game over
        # CHANGE: Check for rock collision.
        for rock in rocks:
            if wormCoords[HEAD]['x'] == rock['x'] and wormCoords[HEAD]['y'] == rock['y']:
                return # game over

        sound_played = False
        # check if worm has eaten an apple
        if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
            # CHANGE: added sound to play after apple is eaten
            if not sound_played: 
                bite_sound = pygame.mixer.Sound('bite.mp3')
                bite_sound.play() 
                sound_played = True
            apple = getRandomLocation(wormCoords[HEAD], apple, rocks) # set a new apple somewhere
            # CHANGE: add one to the score
            score += 1
            # CHANGE: Number of rocks based on score for difficulty curve.
            if (score // 4) > (len(rocks)): # Add one for every four points.
                rocks.append(getRandomLocation(wormCoords[HEAD], apple, rocks))
        else:
            del wormCoords[-1] # remove worm's tail segment

        # move the worm by adding a segment in the direction it is moving
        if direction == UP:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - 1}
        elif direction == DOWN:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + 1}
        elif direction == LEFT:
            newHead = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
        elif direction == RIGHT:
            newHead = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}
        wormCoords.insert(0, newHead)
        DISPLAYSURF.fill(BGCOLOR)

        # CHANGE: increase speed as the score increases
        FPS = min(15 + score // 3, 30)

        drawGrid()
        drawWorm(wormCoords)
        drawApple(apple)
        # CHANGE: Draw the new rocks.
        drawRocks(rocks)
        # CHANGE: Using the new score variable instead.
        drawScore(score)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def drawPressKeyMsg():
    """Display the "Press a key to play" message, doesn't handle the input."""
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    """Check for escape key and QUIT events, otherwise return the key."""
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def showStartScreen():
    """Display two rotating "Wormy" signs until a key is pressed."""
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('Wormy!', True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render('Wormy!', True, GREEN)

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3 # rotate by 3 degrees each frame
        degrees2 += 7 # rotate by 7 degrees each frame


def terminate():
    """Closes the game when called."""
    pygame.quit()
    sys.exit()

# CHANGE: Function now checks if new object is too close to worm
# or is occupied by another object.
def getRandomLocation(wormHead, apple, rocks):
    """Return a dictionary with coordinates if they are far enough away from
    the worm and not on top of another object (excluding the worm's body).
    """
    distance_from_worm = 5
    x = random.randint(0, CELLWIDTH - 1)
    y = random.randint(0, CELLHEIGHT - 1)
    while True:
        while x > (wormHead['x'] - distance_from_worm) and x < (wormHead['x'] + distance_from_worm):
            x = random.randint(0, CELLWIDTH - 1)
        while y > (wormHead['y'] - distance_from_worm) and y < (wormHead['y'] + distance_from_worm):
            y = random.randint(0, CELLHEIGHT - 1)
        if {'x': x, 'y': y} == apple or {'x': x, 'y': y} in rocks:
            x = random.randint(0, CELLWIDTH - 1)
            y = random.randint(0, CELLHEIGHT - 1)
            continue
        else:
            return {'x': x, 'y': y}

def showGameOverScreen():
    """Display "Game Over", then a sound and wait for key press."""
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, 10)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 10 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress() # clear out any key presses in the event queue
    # CHANGE: added sound to play when the Game Over screen appears
    ending_sound = pygame.mixer.Sound('boom.wav')
    ending_sound.play()
    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return

def drawScore(score):
    """Display player's current score while game is running."""
    scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def drawWorm(wormCoords):
    """Draw the entire worm's body."""
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, GREEN, wormInnerSegmentRect)


def drawApple(coord):
    """Draw the apple."""
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, appleRect)

#CHANGE: New function to draw the rocks.
def drawRocks(rocks):
    """Draw the rocks."""
    for rock in rocks:
        x = rock['x'] * CELLSIZE
        y = rock['y'] * CELLSIZE
        rockRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, ORANGE, rockRect)

def drawGrid():
    """Draw the grid that everything displays in."""
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


if __name__ == '__main__':
    main()
