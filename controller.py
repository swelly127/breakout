# controller.py
# Jessica Shu js2634
# December 2 2012

# Extensions: Score, Power Ups, and Increasing Ball Speed as game goes on
# Increasing ball speed causes some glitches when update cannot keep up
# Ball may go through certain bricks at high speed

"""Controller module for Breakout
This module contains a class and global constants for the game Breakout.
Unlike the other files in this assignment, you are 100% free to change
anything in this file. You can change any of the constants in this file
(so long as they are still named constants), and add or remove classes."""
import colormodel
import random
from graphics import *

# CONSTANTS

# Width of the game display (all coordinates are in pixels)
GAME_WIDTH  = 400
# Height of the game display
GAME_HEIGHT = 620

# Width of the paddle
PADDLE_WIDTH = 58
# Height of the paddle
PADDLE_HEIGHT = 11
# Distance of the (bottom of the) paddle up from the bottom
PADDLE_OFFSET = 30

# Horizontal separation between bricks
BRICK_SEP_H = 5
# Vertical separation between bricks
BRICK_SEP_V = 4
# Height of a brick
BRICK_HEIGHT = 8
# Offset of the top brick row from the top
BRICK_Y_OFFSET = 70

# Number of bricks per row
BRICKS_IN_ROW = 5
# Number of rows of bricks, in range 1..10.
BRICK_ROWS = 10
# Width of a brick
BRICK_WIDTH = GAME_WIDTH / BRICKS_IN_ROW - BRICK_SEP_H

# Diameter of the ball in pixels
BALL_DIAMETER = 18

# Number of attempts in a game
NUMBER_TURNS = 3

# Basic game states
# Game has not started yet
STATE_INACTIVE = 0
# Game is active, but waiting for next ball
STATE_PAUSED   = 1
# Ball is in play and being animated
STATE_ACTIVE   = 2
# Game is over, deactivate all actions
STATE_COMPLETE = 3

# Brick Colors
BRICK_COLORS = [colormodel.RED, colormodel.RED, colormodel.ORANGE, colormodel.ORANGE,
                colormodel.YELLOW, colormodel.YELLOW, colormodel.GREEN,
                colormodel.GREEN, colormodel.CYAN, colormodel.CYAN]


# CLASSES
class Breakout(GameController):
    """Instance is the primary controller for Breakout.

    This class extends GameController and implements the various methods
    necessary for running the game.

        Method initialize starts up the game.

        Method update animates the ball and provides the physics.

        The on_touch methods handle mouse (or finger) input.

    The class also has fields that provide state to this controller.
    The fields can all be hidden; you do not need properties. However,
    you should clearly state the field invariants, as the various
    methods will rely on them to determine game state."""
    # FIELDS.

    # Current play state of the game; needed by the on_touch methods
    # Invariant: One of STATE_INACTIVE, STATE_PAUSED, STATE_ACTIVE, STATE_COMPLETE
    _state  = STATE_INACTIVE

    # List of currently active "bricks" in the game.
    #Invariant: A list of  objects that are instances of GRectangle (or a
    #subclass) If list is  empty, then state is STATE_INACTIVE (game over)
    _bricks = []

    # The player paddle
    # Invariant: An object that is an instance of GRectangle (or a subclass)
    # Also can be None; if None, then state is STATE_INACTIVE (game over)
    _paddle = None

    # The ball to bounce about the game board
    # Invariant: An object that is an instance of GEllipse (or a subclass)
    # Also can be None; if None, then state is STATE_INACTIVE (game over) or
    # STATE_PAUSED (waiting for next ball)
    _ball = None

    # ADD MORE FIELDS (AND THEIR INVARIANTS) AS NECESSARY

    # Message displayed on welcome screen.
    # Invariant: Must be GLabel object with text displaying message
    # telling user to click to start game
    # Is None when game starts. Then stays a GLabel object that is hidden form view
    _message=None

    # Position of X before touch motion
    # Invariant: Must be float of integer
    _initPadX=0

    # Position of X before touch motion
    # Invariant: Must be float of integer
    _initTouchX=0

    # Number of turns player has left
    # Invariant: Must be an integer that is either 0 1 2 or 3
    _turnsLeft = NUMBER_TURNS

    # Power ups in play
    # Invariant: Must be a PowerUp object (a subclass of GImage)
    # None when no powerUps are in play
    _powerUps = None

    # bounceSound
    # Invariant: must be a sound object
    # Does not change throughout the game
    _bounce=Sound('bounce.wav')

    # power up sound
    # Invariant: must be a sound object
    # Does not change throughout the game
    _power = Sound('bonus.wav')

    # power up message
    # Invariant: must be a GLabel object
    # Also can be None when no powerUps are in play
    _powerMes = None

    # lives left message
    # Invariant: must be a GLabel object
    # Also can be None before game is initialized
    _lives = None

    # score label for viewer
    # Invariant: must be a GLabel object
    # Also can be None when game has not been initialized
    _scoreLabel = None

    # score
    # Invariant: positive integer representing the score
    _score = 0

    # the image associated with the winning message
    # Invariant: GImage object containing the winning message
    # None when state is not STATE_COMPLETE
    _completeImage = None

    # the object the ball bumps into
    # Invariant: Must be a brick
    _bump = None

    def initialize(self):
        """Initialize the game state.

        Initialize any state fields as necessary to statisfy invariants.
        When done, set the state to STATE_INACTIVE, and display a message
        saying that the user should press to play a game."""
        self._power.set_volume(0.5)
        self._score = 0
        self.view.add(GRectangle(size=(GAME_WIDTH,GAME_HEIGHT),x=0,y=0,
                                 fillcolor=colormodel.BLACK))
        self._message=GLabel(text='Click to Start',linecolor=colormodel.WHITE,
                        width=400,height=620,font_size=20,font_name='ComicSans.ttf',
                        bold=True,halign='center',valign='middle')
        self.view.add(self._message)
        Breakout._state=STATE_INACTIVE

    def update(self, dt):
        """Animate a single frame in the game.

        This is the method that does most of the work.  It moves the ball, and
        looks for any collisions.  If there is a collision, it changes the
        velocity of the ball and removes any bricks if necessary.

        This method may need to change the state of the game.  If the ball
        goes off the screen, change the state to either STATE_PAUSED (if the
        player still has some tries left) or STATE_COMPLETE (the player has
        lost the game).  If the last brick is removed, it needs to change
        to STATE_COMPLETE (game over; the player has won).

        Precondition: dt is the time since last update (a float).  This
        parameter can be safely ignored."""
        if self._state==STATE_ACTIVE:
            if self._lives!=None:
                self.view.remove(self._lives)
            self._lives=GLabel(top = GAME_HEIGHT,size=(90,100),
                               linecolor=colormodel.WHITE,
                               x=0,halign='center',valign='top',font_size=20,
                               text='Lives: '+ str(self._turnsLeft))
            self.view.add(self._lives)
            if self._scoreLabel!=None:
                self.view.remove(self._scoreLabel)
            self._scoreLabel=GLabel(top = GAME_HEIGHT,size=(90,100),x=GAME_WIDTH-90,
                                    halign='right',valign='top',font_size=20,
                                    text='Score: '+ str(self._score),
                                    linecolor=colormodel.RED)
            self.view.add(self._scoreLabel)
            self._bump = self._ball._getCollidingObject()
            if self._bump!=None:
                self.updateBrick()
            elif self._hitsPaddle():
                self.activatePower()
            try:
                self._powerUps.y += self._powerUps.vy
            except:
                pass
            try:
                self.updateBall()
            except:
                pass

    def updateBrick(self):
        """ Helper function for update. Updates bricks and checks for wins

        This function will remove bricks that have touched the ball. Also
        checks if game is finished and randomly assigns powerups"""
        self.view.remove(self._bump)
        Breakout._bricks.remove(self._bump)
        self._score += self._bump.y-300
        if random.random()<0.25 and self._powerUps==None:
            self._powerUps = PowerUp(self._bump.x,self._bump.y)
            self.view.add(self._powerUps)
        if Breakout._bricks == []:
            self._state=STATE_COMPLETE
            self._message = GLabel(text='not bad ;)',
                                  linecolor = colormodel.WHITE,
                                  width=400,height=620,font_size=20,
                                  font_name='ComicSans.ttf',
                                  bold=True,halign='center',valign='middle')
            self.view.add(self._message)
            self._completeImage=GImage(source='winner.png',width=100,height=210,
                                 pos=(50,170))
            self.view.add(self._completeImage)

    def updateBall(self):
        """Helper function for Update. Updates ball position and checks for losses

        This function updates the position of the ball, and checks to see if game
        has been lost"""
        self._ball.x += self._ball._vx
        self._ball.y += self._ball._vy
        if self._ball.x<0.1 and self._ball._vx<0.0:
            self._ball._vx = -1 * self._ball._vx
        elif self._ball.x+self._ball.width>GAME_WIDTH-0.1:
            self._ball._vx = -1 * self._ball._vx
        if self._ball.y+self._ball.height>GAME_HEIGHT-0.1:
            self._ball._vy = -1 * self._ball._vy
        elif self._ball.y<5.0:
            self._paddle.size = (PADDLE_WIDTH,PADDLE_HEIGHT)
            self.view.remove(self._ball)
            self._turnsLeft -= 1
            if self._turnsLeft == 0:
                self._state=STATE_COMPLETE
                self._message = GLabel(text='much dissappoint :(',
                            linecolor=colormodel.WHITE, width=400,height=620,
                            font_size=20,font_name='Arial.ttf',
                            bold=True,halign='center',valign='middle')
                self.view.add(self._message)
                self._completeImage=GImage(source='loser.png',width=100,
                                     height=210,pos=(50,170))
                self.view.add(self._completeImage)
            else:
                if self._powerUps!=None:
                    self.view.remove(self._powerUps)
                    self._powerUps = None
                    self.view.remove(self._powerMes)
                    self._powerMes = None
                self._state=STATE_PAUSED
                self._ball=None

    def activatePower(self):
        """This is a helper function for update that activates Power Ups.

        When user 'catches' a power up star, this helper function is called
        Adds 50 to user's score. Randomly chooses and implements one of
        four different power ups Creates a GLabel message telling user she or
        he has activated the power up. Power ups include a longer paddle, slower
        ball, less bricks, and larger ball"""
        self._score += 50
        self._power.play()
        j=random.choice([1,2,3,4])
        if j == 1:
            self.displayPower('ball speed decreased!!!')
            self._ball.vx=self._ball.vx * 0.75
            self._ball.vy=self._ball.vy * 0.75
        elif j == 2:
            self.displayPower('paddle size increased!!!')
            Breakout._paddle.width += PADDLE_WIDTH/4.0
        elif j ==3:
            self.displayPower('random brick kill!!!')
            for c in Breakout._bricks:
                if random.random()<.20:
                    self.view.remove(c)
                    self._bricks.remove(c)
        elif j==4:
            self.displayPower('ball size increased!!!')
            self._ball.width += BALL_DIAMETER/5.0
            self._ball.height += BALL_DIAMETER/5.0

    def displayPower(self,msg):
        '''Created a GLabel Object informing user that a PowerUp is active

        Precondition: msg must be a string'''
        if self._powerMes!=None:
            self.view.remove(self._powerMes)
        self._powerMes = GLabel(size=(GAME_WIDTH,BRICK_Y_OFFSET),
                                linecolor=colormodel.WHITE,
                                top=GAME_HEIGHT,left=0,
                                text=msg,halign='center',
                                valign='top',font_size=20)
        self.view.add(self._powerMes)

    def on_touch_down(self,view,touch):
        """Respond to the mouse (or finger) being pressed (but not released)

        If state is STATE_ACTIVE or STATE_PAUSED, then this method should
        check if the user clicked inside the paddle and begin movement of the
        paddle.  Otherwise, if it is one of the other states, it moves to the
        next state as appropriate.

        Precondition: view is just the view attribute (unused because we have
        access to the view attribute).  touch is a MotionEvent (see
        documentation) with the touch information."""
        if self._state==STATE_INACTIVE:
            print "INACTIVE"
            self.view.remove(self._message)
            Breakout._state=STATE_PAUSED
            self.set_bricks()
            Breakout._paddle=GRectangle(fillcolor=colormodel.BLUE,
                            size=(PADDLE_WIDTH,PADDLE_HEIGHT),x=0,y=PADDLE_OFFSET)
            self.view.add(Breakout._paddle)
            self._scoreLabel=GLabel(top = GAME_HEIGHT,size=(90,100),x=GAME_WIDTH-90,
                                    halign='right', valign='top',font_size=20,
                                    text='Score: '+ str(self._score),
                                    linecolor=colormodel.RED)
            self.view.add(self._scoreLabel)
        elif self._state==STATE_PAUSED:
            self.view.remove(self._message)
            Breakout._initPadX=Breakout._paddle.x
            Breakout._initTouchX=touch.x
            self.delay(self._serve,0)
            if self._ball!=None:
                self._state=STATE_ACTIVE
        elif self._state==STATE_ACTIVE:
            print "ACTIVE"
            Breakout._initPadX=Breakout._paddle.x
            Breakout._initTouchX=touch.x
        elif self._state==STATE_COMPLETE:
            print "COMPLETE"
            self.view.remove(self._completeImage)
            self.view.remove(self._message)
            self.view.remove(self._lives)
            for p in self._bricks:
                try:
                    self.view.remove(p)
                except:
                    pass
            self._turnsLeft=NUMBER_TURNS
            self._state=STATE_INACTIVE
            self._score=0
            self.view.add(GRectangle(size=(GAME_WIDTH,GAME_HEIGHT),x=0,y=0,
                                    fillcolor=colormodel.BLACK))
            self._message=GLabel(text='Click to Play Again',linecolor=colormodel.WHITE,
                        width=400,height=620,font_size=20,font_name='ComicSans.ttf',
                        bold=True,halign='center',valign='middle')
            self.view.add(self._message)
            Breakout._paddle=GRectangle(fillcolor=colormodel.BLUE,
                            size=(PADDLE_WIDTH,PADDLE_HEIGHT),x=0,y=PADDLE_OFFSET)
            self.view.add(Breakout._paddle)
            self._ball=Ball()
            self.view.add(self._ball)
            self.set_bricks()
            Breakout._state=STATE_PAUSED
            self._state=STATE_PAUSED

    def _serve(self):
        """Serves the Ball

        Adds it to view, and changes state to limbo"""
        if self._ball==None:
            self._ball=Ball()
            self.view.add(self._ball)
        self._state=STATE_ACTIVE

    def on_touch_move(self,view,touch):
        """Respond to the mouse (or finger) being moved.

        If state is STATE_ACTIVE or STATE_PAUSED, then this method should move
        the paddle. The distance moved should be the distance between the
        previous touch event and the current touch event. For all other
        states, this method is ignored.

        Precondition: view is just the view attribute (unused because we have
        access to the view attribute).  touch is a MotionEvent (see
        documentation) with the touch information."""
        if self._state==STATE_ACTIVE or self._state==STATE_PAUSED:
            Breakout._paddle.x=min(max(0,touch.x+self._initPadX-self._initTouchX),
                                   GAME_WIDTH-PADDLE_WIDTH)

    def on_touch_up(self,view,touch):
        """Respond to the mouse (or finger) being released.

        If state is STATE_ACTIVE, then this method should stop moving the
        paddle. For all other states, it is ignored.

        Precondition: view is just the view attribute (unused because we have
        access to the view attribute).  touch is a MotionEvent (see
        documentation) with the touch information."""
        if self._state==STATE_ACTIVE:
            Breakout._paddle.x=Breakout._paddle.x
        else:
            pass

    def set_bricks(self):
        """Sets up bricks for game play

        Makes a list of bricks and adds it to the field _bricks
        Adds each brick to the game view."""
        for c in range(BRICKS_IN_ROW):
            for q in range(BRICK_ROWS):
                self._bricks.append(GRectangle(y=GAME_HEIGHT-
                    (BRICK_Y_OFFSET+(BRICK_SEP_V+BRICK_HEIGHT)*(q+1)),
                    x=BRICK_SEP_H/2.0+c*(float(BRICK_WIDTH)+float(BRICK_SEP_H)),
                    linecolor=BRICK_COLORS[q%10], fillcolor=BRICK_COLORS[q%10],
                    height=BRICK_HEIGHT, width=BRICK_WIDTH))
        for p in self._bricks:
            self.view.add(p)

    def _hitsPaddle(self):
        """Checks to see if the user successfully catches the power up

        Checks if paddle collides with both lower corners of power up image.
        Returns Boolean value
        Removes power up image from view and sets power up field to None"""
        if self._powerUps!=None:
            if (self._paddle.collide_point(self._powerUps.x
                or self._powerUps+20,self._powerUps.y)):
                self.view.remove(self._powerUps)
                self._powerUps = None
                return True
            elif self._powerUps.y<1.0:
                self.view.remove(self._powerUps)
                self._powerUps = None
                return False


class Ball(GEllipse):
    """Instance is a game ball.

    We extends GEllipse because a ball does not just have a position; it
    also has a velocity.  You should add a constructor to initialize the
    ball, as well as one to move it.

    Note: The ball does not have to be a GEllipse. It could be an instance
    of GImage (why?). This change is allowed, but you must modify the class
    header up above."""

    # Velocity in x direction.  A number (int or float)
    _vx = 0.0
    # Velocity in y direction.  A number (int or float)
    _vy = 0.0

    @property
    def vx(self):
        return self._vx

    @vx.setter
    def vx(self, value):
        self._vx = float(value)

    @property
    def vy(self):
        return self._vy

    @vy.setter
    def vy(self, value):
        self._vy = float(value)

    def __init__(self):
        """Constructor: Takes no arguments. Created a game ball with random color """
        super(Ball,self).__init__(x=0,y=GAME_HEIGHT-(BRICK_Y_OFFSET+
                (BRICK_SEP_V+BRICK_HEIGHT)*(BRICK_ROWS))-35,
                width=BALL_DIAMETER,height=BALL_DIAMETER,
                fillcolor=colormodel.RGB(random.randrange(255),random.randrange(255),
                random.randrange(255)), linecolor=colormodel.BLACK)
        self._vx = random.uniform(1.0,5.0)
        self._vy = -5.0

    def _getCollidingObject(self):
        """Returns object the ball hits

        Checks paddle for collisions with ball. Then goes through list
        of bricks and checks for collisions. Changes velocity of ball as appropriate

        Does not return value if colliding object is paddle"""
        if Breakout._paddle.collide_point(self.x+self.width,self.y):
            Breakout._bounce.play()
            if Breakout._paddle.collide_point(self.x+self.width,self.y+5):
                self._vx = -1 * self._vx
            else:
                self._vy = self._vy * -1
                if self.vy>0:
                    self.vy+=self.vy/10.0
                else:
                    self.vy-=self.vy/10.0
                self._vx += self._vx/10.0
        elif Breakout._paddle.collide_point(self.x,self.y):
            if Breakout._paddle.collide_point(self.x,self.y+5):
                self._vx = -1 * self._vx
            else:
                self._vy = self._vy * -1

        else:
            for b in Breakout._bricks:
                if (b.collide_point(self.x,self.y)
                    or b.collide_point(self.x,self.y+self.height)
                    or b.collide_point(self.x+self.width,self.y+self.height)
                    or b.collide_point(self.x+self.width,self.y)):
                    if (b.collide_point(self.x+5,self.y)
                        or b.collide_point(self.x+5,self.y+self.height)):
                        self._vy = self._vy * -1
                    elif (b.collide_point(self.x,self.y+5)
                          or b.collide_point(self.x+self.width,self.y+5)):
                        self._vx = self._vx * -1
                    return b


class PowerUp(GImage):
    """Instance is a power up.

    We extends GImage because a power up does not just have a position;
    it also has a velocity """

    # Velocity in x direction.  A number (int or float)
    _vx = 0.0
    # Velocity in y direction.  A number (int or float)
    _vy = 0.0

    @property
    def vx(self):
        return self._vx

    @vx.setter
    def vx(self, value):
        self._vx = float(value)

    @property
    def vy(self):
        return self._vy

    @vy.setter
    def vy(self, value):
        self._vy = float(value)

    def __init__(self,x,y):
        """Constructor: input x and y to set start position of power up"""
        super(PowerUp,self).__init__(source='star.png',pos=(x+BRICK_WIDTH/2.0,y),
                                     width=20,height=20)
        self._vx = 0.0
        self._vy = -4.0
