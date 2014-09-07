# Jessica Shu
# Enjoy :)

"""Controller module for bubble game"""

import colormodel
import random
from graphics import *

# CONSTANTS

# Width of the game display (all coordinates are in pixels)
GAME_WIDTH  = 400
# Height of the game display
GAME_HEIGHT = 620

# Radius of Each Bubble
BUBBLE_RADIUS = 10
# Columns of Bubbles
BUBBLE_COLS = 20
# Rows of Bubbles
BUBBLE_ROWS = 20

# Basic game states
# Game has not started yet
STATE_INACTIVE = 0
# Game is active, but waiting for ball to shoot
STATE_PAUSED   = 1
# Ball is in play and being animated
STATE_ACTIVE   = 2
# Game is over, deactivate all actions
STATE_COMPLETE = 3

# Bubble colors
BUBBLE_COLORS = [colormodel.RED,colormodel.BLUE,colormodel.GREEN,colormodel.BLACK,colormodel.WHITE,colormodel.ORANGE]
#Levels vary number of bubble colors used
NUM_COLORS = 1

class BubbleGame(GameController):
    """Instance is the primary controller for Breakout.

    This class extends GameController and implements the various methods
    necessary for running the game.

        Method initialize starts up the game.

        Method update animates the ball and provides the physics.

        The on_touch methods handle mouse (or finger) input"""
    _state = STATE_INACTIVE
    _shooter = None
    _mainBall = None
    _startMes = None

    def initialize(self):
        """Initialize the game state.

        Initialize any state fields as necessary to statisfy invariants.
        When done, set the state to STATE_INACTIVE, and display a message
        saying that the user should press to play a game."""
        self._message=GLabel(text='Click to Start',width=400,height=620,font_size=20,font_name='ComicSans.ttf',bold=True,halign='center',valign='middle')
        self.view.add(self._message)
        BubbleGame._state = STATE_INACTIVE

    def touchDown(self):
        if self._state==STATE_INACTIVE:
            self.setBalls

    def setBalls(self):
        colors = BUBBLE_COLORS[:NUM_COLORS]
        for c in BUBBLE_COLS:
            for q in BUBBLE_ROWS:
                if q%2==1:
                    ball=GEllipse(size=(20,20),fill_color=random.choice(colors),
                                  center=(10+20*c,20*q),line_color=colormodel.BLACK)
                    self.view.add(ball)
                elif c!=BUBBLE_COLS-1:
                    ball=GEllipse(size=(20,20),fill_color=random.choice(colors),
                                  center=(20+20*c,20*q),line_color=colormodel.BLACK)
                    self.view.add(ball)
                q=q+1
            c=c+1

