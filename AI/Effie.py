  # -*- coding: latin-1 -*-
import random
import sys
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *
import os

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
        self.myHill = None
        self.file = './delplanc18_plaisted20_state_util.txt'
        self.stateUtil = self.initializeStateUtil() # {state: utility} 
        self.discountFactor = 0.95 # Constant
        self.learningRate = 1.0 # will exponentially decline
        self.explorationRate = 1.0 # will exponentially decline
        self.tickingClock = 0 # will increase after every game
        self.reward = 0 # no rewards yet
        self.discount = 0.95 #static variable
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
        # one time variables
        if (self.myTunnel == None):
            self.myTunnel = getConstrList(currentState, currentState.whoseTurn, (TUNNEL,))[0]
        if (self.myHill == None):
            self.myHill = getConstrList(currentState, currentState.whoseTurn, (ANTHILL,))[0]
        if (self.myFood == None):
            self.myFood = getCurrPlayerFood(self, currentState)
        
        self.explorationRate = 1-self.tickingClock**2/1000000
        self.learningRate = 1-self.tickingClock**2/1000
       
        self.reward += -0.001 # this will give a small penalty for every move made to encourage it to win faster
        consolidatedCurrent = self.consolidateState(currentState)
        if self.lastState is None:
            consolidatedLast = ""
        else:
            consolidatedLast = self.consolidateState(self.lastState)
        
        if consolidatedLast in self.stateUtil:
            lastStateUtil = self.stateUtil[consolidatedLast]
        else:
            lastStateUtil = 0
        if consolidatedCurrent in self.stateUtil:
            currentUtil = self.stateUtil[consolidatedCurrent]
        else:
            currentUtil = 0
        self.stateUtil[consolidatedLast] = lastStateUtil + self.learningRate*(self.reward+self.discount*currentUtil-lastStateUtil)


        # save this state in case the game ends
        self.lastState = currentState
        # make a move
        moveType = random.random() # [0, 1]
        move = None
        if moveType > self.explorationRate: 
            move = self.makeExploitationMove(currentState)
        if move is None:
            moves = listAllLegalMoves(currentState)
            selectedMove = moves[random.randint(0,len(moves) - 1)]

            #don't do a build move if there are already 3+ ants
            numAnts = len(currentState.inventories[currentState.whoseTurn].ants)
            while (selectedMove.moveType == BUILD and numAnts >= 3):
                selectedMove = moves[random.randint(0,len(moves) - 1)]

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
        if hasWon:
            reward = 1
        else: 
            reward = -1
        # update stateUtil for self.lastState by applying TD learning equation
            # get consolidated state
        s = self.consolidateState(self.lastState)
        if s in self.stateUtil:
            old = self.stateUtil[s]
            newUtil = old + self.learningRate * self.reward
            self.stateUtil[s] = newUtil
        else:
            self.stateUtil[s] = self.learningRate * self.reward
        self.tickingClock += 1 # increment tickingClock
        self.reward = 0 # reset reward
        self.saveUtils()

    ######################### NEW TD LEARNING METHODS ##########################
    ##
    # initializeStateUtil
    # Description: Sets the stateUtil dict as the contents of
    # delplanc18_plaisted20_state_util.txt or empty.
    #
    def initializeStateUtil(self):
        if os.path.exists(self.file):
            return self.loadUtils()
        else:
            return {}

    ##
    # consolidateState
    # Description: Map a GameState to a consolidated state based on food values.
    #
    # Parameters:
    #   state: GameState to consolidate.
    # Return: a string representing a consolidated state
    #
    def consolidateState(self, state):
        # helper variables
        # print("This is our state: ", state)
        queen = getAntList(state, state.whoseTurn, (QUEEN,))[0]
        workers = getAntList(state, state.whoseTurn, (WORKER,))

        simpleState = ''

        # number of workers
        simpleState += 'Effie has ' + str(len(workers)) + ' worker(s).'
        # amount of food
        simpleState += ' Effie has ' + str(state.inventories[state.whoseTurn].foodCount)
        simpleState += ' item(s) of food in inventory.'
        # average dist of carrying ants/non=carrying ants
        numCarry = 0
        sumCarry = 0
        numForage = 0
        sumForage = 0
        for worker in workers:
            if worker.carrying:
                numCarry += 1
                sumCarry += (min(approxDist(worker.coords, self.myHill.coords),
                               approxDist(worker.coords, self.myTunnel.coords)))
            else:
                numForage += 1
                sumForage += (min(approxDist(worker.coords, self.myFood[0].coords),
                               approxDist(worker.coords, self.myFood[1].coords)))
        if numCarry > 0:
            carryVal = sumCarry / float(numCarry)
        else:
            carryVal = 0
        if numForage > 0:
            forageVal = sumForage / float(numForage)
        else:
            forageVal = 0
        simpleState += ' The average distance of a carrying worker from its target is ' + str(carryVal)
        simpleState += ' steps. The average distance of a non-carrying worker from its target is ' + str(forageVal)
        simpleState += ' steps.'

        # queen is on anthill
        if queen.coords == self.myHill.coords:
            simpleState += ' The queen is on the anthill.'
        else:
            simpleState += ' The queen is not on the anthill.'
        # queen is on tunnel
        if queen.coords is self.myTunnel.coords:
            simpleState += ' The queen is on the tunnel.'
        else:
            simpleState += ' The queen is not on the tunnel.'

        return simpleState.strip()

    ##
    # saveUtils
    # Description: writes the current stateUtil dictionary to a file.
    # File Name delplanc18_plaisted20_state_util.txt
    #
    def saveUtils(self):
        with open(self.file, "w") as file:
              for key, value in self.stateUtil.items():
                file.write("" + str(key) + "|" + str(value))
                file.write("\n")

    ##
    # loadUtils
    # Description: reads the values from file name delplanc18_plaisted20_state_util.txt
    #
    def loadUtils(self):
        data = {}
        with open(self.file) as file:
          for line in file:
            line = line.strip()
            (key,val) = line.split("|")
            data[key] = float(val)

        return data

    # makeExploitationMove
    # Description: pick the move that leads to the highest utility state. Ignore
    # all moves without corresponding utility values. Break ties randomly and choose
    # random move if no states have utilities
    #
    def makeExploitationMove(self, state):
        legalMoves = listAllLegalMoves(state)
        #stateArray = []
        utilities = {}
        for move in legalMoves:
            state = getNextState(state,move)
            consolidatedState = self.consolidateState(state)
            #stateArray.append(consolidatedState)
            if consolidatedState in self.stateUtil:
                utilities[move] = self.stateUtil[consolidatedState]

        # establishes the highest utilites that were found and the best state
        highestUtility = -100000
        bestMove = None

        # checks the list of utilites for comparisons
        for key in utilities.keys():
            if utilities[key] > highestUtility: #if new utility is higher, it replaces the current highest
                highestUtility = utilities[key]
                bestMove = key
            elif utilities[key] == highestUtility: #if the utilites are tied, there is a random tiebreaker
                score1 = random.random()
                score2 = random.random()
                if score1 > score2:
                    bestMove = key
        return bestMove
            
        


    ## FROM AIPLAYERUTILS for testing
    # Return: a list of the food objects on my side of the board
    def getCurrPlayerFood(self, currentState):
        food = getConstrList(currentState, 2, (FOOD,))
        myFood = []
        if (currentState.inventories[0].player == currentState.whoseTurn):
            myFood.append(food[2])
            myFood.append(food[3])
        else:
            myFood.append(food[0])
            myFood.append(food[1])
        return myFood

################################################################################
##############################TEST CASES########################################
################################################################################
testAgent = AIPlayer(PLAYER_ONE)

################################################################################
# consolidateState
######################################################################
testState = GameState.getBasicState()
food1 = Building((5, 0), FOOD, NEUTRAL)
food2 = Building((4, 0), FOOD, NEUTRAL)
food3 = Building((4, 9), FOOD, NEUTRAL)
food4 = Building((5, 9), FOOD, NEUTRAL)
hill = Building((0, 0), ANTHILL, PLAYER_ONE)
tunnel = Building((5,1), TUNNEL, PLAYER_ONE)
testState.inventories[NEUTRAL].constrs += [food1, food2]
testState.inventories[NEUTRAL].constrs += [food3, food4]
p1Worker = Ant((5, 4), WORKER, PLAYER_ONE)
queen = Ant((0, 0), QUEEN, PLAYER_ONE)
testState.inventories[0].ants.append(p1Worker)
testState.inventories[0].ants.append(queen)
testState.inventories[0].foodCount = 10
testState.whoseTurn = PLAYER_ONE
testAgent.myFood = testAgent.getCurrPlayerFood(testState)
testAgent.myTunnel = getConstrList(testState, testState.whoseTurn, (TUNNEL,))[0]
testAgent.myHill = getConstrList(testState, testState.whoseTurn, (ANTHILL,))[0]

s1 = testAgent.consolidateState(testState)
goalState1 = """
 Effie has 1 worker(s). Effie has 10 item(s) of food in inventory. The average distance of a carrying worker from its target is 0 steps. The average distance of a non-carrying worker from its target is 5.0 steps. The queen is on the anthill. The queen is not on the tunnel.
"""
if not s1.strip() == goalState1.strip():
    print('Effie failed consolidateState test 1. Expected:\n', goalState1, '\nRecieved:\n', s1, '\n')

queen.coords = (9,9)
p1Worker2 = Ant((8, 9), WORKER, PLAYER_ONE)
p1Worker3 = Ant((0, 1), WORKER, PLAYER_ONE)
p1Worker3.carrying = True

testState.inventories[0].ants.append(p1Worker2)
testState.inventories[0].ants.append(p1Worker3)

s2 = testAgent.consolidateState(testState)
goalState2 = """
 Effie has 3 worker(s). Effie has 10 item(s) of food in inventory. The average distance of a carrying worker from its target is 1.0 steps. The average distance of a non-carrying worker from its target is 4.0 steps. The queen is on the anthill. The queen is not on the tunnel.
"""
if not s2.strip() == goalState2.strip():
    print('Effie failed consolidateState test 2. Expected:\n', goalState2, '\nRecieved:\n', s2, '\n')

################################################################################
# saveUtils
######################################################################
testAgent.stateUtil = {'I am a consolidated state.' : 0.0,
    'I am also a consolidated state' : 1.0,
    'I am the best of the consolidated states.': 2.0}
testAgent.file = 'test.txt'
testAgent.saveUtils()

with open(testAgent.file, "r") as f:
    data = f.read()

goalContent = """
I am a consolidated state.|0.0
I am also a consolidated state|1.0
I am the best of the consolidated states.|2.0
"""

if not data.strip() == goalContent.strip():
    print('Effie failed saveUtils test 1. Expected:\n', goalContent, '\nRecieved:\n', data, '\n')


################################################################################
# loadUtils
######################################################################
old = testAgent.stateUtil
new = testAgent.loadUtils()

if not old == new:
    print('Effie failed loadUtils test 1. Expected:\n', old, '\nRecieved:\n', new, '\n')

################################################################################
# initializeStateUtil
################################################################################
testAgent.stateUtil = None
testAgent.stateUtil = testAgent.initializeStateUtil()
if not old == testAgent.stateUtil:
    print('Effie failed initializeStateUtil test 1. Expected:\n', old, '\nRecieved:\n', testAgent.stateUtil, '\n')

os.remove(testAgent.file)
testAgent.stateUtil = testAgent.initializeStateUtil()
if not testAgent.stateUtil == {}:
    print('Effie failed initializeStateUtil test 2. Expected:\nNone \nRecieved:\n', testAgent.stateUtil, '\n')
################################################################################
# makeExploitationMove
######################################################################