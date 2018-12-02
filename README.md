# CS421_HW6

Our Plan for HW 6

TD equation: Utility_Updated(s) = Utility_Old(s) + learning_rate (Reward(s) + discount_factor * Utility_Current_State(s') - Utility_Old(s))

Instance Variables:
- stateUtil dictionary: when I see a new state --> consolidateState --> If in stateUtil, update. Otherwise, calculate util and add.
- discount factor: start at 0.95 (constant)
- exponential learning rate: exponential function --> want to play around 200 games before exploitation.
    1 - (x^2) / 1000 (look at inverse exponential, steep at first, then limit at 0) 1 - 1/2 * x^2
- epsilon exploration_rate = 1 - (x^2) / 1000000
- updateNum = 10 (not using currently -> for TD Lambda)
- lastState -- the last state seen

Methods:

- consolidateState(state): will map all possible states into a smaller group of states
     
- saveUtils: writes the current stateUtil dictionary to a file. File Name delplanc18_plaisted20_state_util.txt
  - called by registerWin (should overwrite old values?)
- loadUtlis: load the values from the file specified above
  - Constructor should check if file is present. If so, initialize stateUtil with these values.
- registerWin:
  - set reward for game: +1 for win, -1 for loss
  - update StateUtil by applying TD learning on self.lastState
  -update learning rate
  - update exploration_rate
- makeMove:
  - grab last updateNum states and update their utility using TD equation
  - save current state as lastState
  - update stateUtil by applying TD learning
    - see equation at top of description. Use R(s) = -0.0001
  - making the move:
    - get random number [0, 1]
    - if num > learning_rate:
        exploit --> 
          - get all possible moves. 
          - call getNextState for all legal moves.
          - call consolidateState for each state resulting.
          - Is this state in our stateUtil? If so, get utility. Otherwise, ignore.
          - Pick state with highest utility.
                - Break ties randomly.
                - If no states with utility, choose random move/End turn.
    - otherwise:
        random move,
        make random move. 
