  # -*- coding: latin-1 -*-
import random
import sys
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import addCoords
from AIPlayerUtils import *


##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    #   cpy           - whether the player is a copy (when playing itself)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer, self).__init__(inputPlayerId, "Effie")
        #the coordinates of the agent's food and tunnel will be stored in these
        #variables (see getMove() below)
        self.myFood = None
        self.myTunnel = None
        self.stateUtil = self.initializeStateUtil() # {state: utility} # TODO check file structure and initialize
        self.discountFactor = 0.95 # Constant
        self.learningRate = 1.0 # will exponentially decline
        self.explorationRate = 1.0 # will exponentially decline
        self.lastState = None

    ##
    #getPlacement
    #
    # The agent uses a hardcoded arrangement for phase 1 to provide maximum
    # protection to the queen.  Enemy food is placed randomly.
    #
    def getPlacement(self, currentState):
        self.myFood = None
        self.myTunnel = None
        if currentState.phase == SETUP_PHASE_1:
            return [(0,0), (5, 1),
                    (0,3), (1,2), (2,1), (3,0), \
                    (0,2), (1,1), (2,0), \
                    (0,1), (1,0) ];
        elif currentState.phase == SETUP_PHASE_2:
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return None  #should never happen

    ##
    #getMove
    #
    # This agent simply gathers food as fast as it can with its worker.  It
    # never attacks and never builds more ants.  The queen is never moved.
    #
    ##
    def getMove(self, currentState):
        # save this state in case the game ends
        self.lastState = currentState
        # update stateUtil for self.lastState by applying TD learning equation
        # make a move
        moveType = random.random() # [0, 1]

        if moveType > self.explorationRate:
            return self.makeExploitationMove(currentState)
        else:
            moves = listAllLegalMoves(currentState)
            selectedMove = moves[random.randint(0,len(moves) - 1)];

            #don't do a build move if there are already 3+ ants
            numAnts = len(currentState.inventories[currentState.whoseTurn].ants)
            while (selectedMove.moveType == BUILD and numAnts >= 3):
                selectedMove = moves[random.randint(0,len(moves) - 1)];

            return selectedMove

    ##
    #getAttack
    #
    # This agent never attacks
    #
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        return enemyLocations[0]  #don't care

    ##
    #registerWin
    #
    # save the stateUtil mapping to a file and updates the learning and exploration rates
    #
    def registerWin(self, hasWon):
        reward = hasWon
        # update stateUtil for self.lastState by applying TD learning equation
        # update learning rate
        # update exploration rate
        self.saveUtils()

    ######################### NEW TD LEARNING METHODS ##########################
    ## TODO complete
    # initializeStateUtil
    # Description: Sets the stateUtil dict as the contents of
    # delplanc18_plaisted20_state_util.txt or empty.
    #
    def initializeStateUtil(self):
        return {}

    ##
    # consolidateState
    # Description: Map a GameState to a consolidated state based on food values.
    #
    # Parameters:
    #   state: GameState to consolidate.
    #
    def consolidateState(self, state):
        pass

    ##
    # saveUtils
    # Description: writes the current stateUtil dictionary to a file.
    # File Name delplanc18_plaisted20_state_util.txt
    #
    def saveUtils(self):
        pass

    ##
    # loadUtils
    # Description: reads the values from file name delplanc18_plaisted20_state_util.txt
    #
    def loadUtils(self):
        pass

    ##
    # makeExploitationMove
    # Description: pick the move that leads to the highest utility state. Ignore
    # all moves without corresponding utility values. Break ties randomly and choose
    # random move if no states have utilities
    #
    def makeExploitationMove(self, state):
        pass
