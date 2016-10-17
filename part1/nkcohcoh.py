
#https://www.cs.swarthmore.edu/~meeden/cs63/f05/minimax.html (pseudocode from here)
#http://codereview.stackexchange.com/a/24775 (ideas for victory check)

#things to try for alpha-beta:
#transposition table
#use of IDS to order branch exploration

'''
For each programming problem, please include a detailed comments section at the top of your code 
that describes: 

Timing Note!! : the program accepts all time inputs within a given number of seconds, meaning 
truncated to the given number of seconds. if given time = 3, the program accepts 3.5, 3.7, etc...
If the ceiling of 3 is desired, the input should be 2.

(1) a description of how you formulated the search problem, including precisely defining 
the state space, the successor function, the edge weights, and any heuristics you designed; 
State space: all possible game states reachable from the input board 
successor function: depending on whose turn it is, black or white stone added to current board at all open positions
edge weights: constant
heuristics: 
terminal states: win: inf. loss: -inf. draw: 0.
nonterminal states: for every possible sequence location:
  for white: if a sequence has no black stones:
                count +1 for the possibility of losing there. count the number of white stones, add +3**|w|
  for black: do the same
  subtract white from black for white for an overall score

(2) a brief description of how your search algorithm works;
Iterative deepening for alpha-beta pruning, with one final layer of beam search where the worst successor is removed.
This beam search may not check the whole final layer unless time permits.

(3) a discussion of any problems you faced, any assumptions, simplifications, and/or design 
decisions you made;
The fact that quitting recursive threads after a timeout occurs made it difficult to design alpha-beta.
For this reason, we (a) counted the total number of moves at depth d (e.g., if there are 8 open spots and
the depth is 2, there are 8*7 moves (b) computed the time for IDS to run at depth d and counted the 
number of visited states (c) checked whether the remaining time was long enough for a full IDS at depth d+1.
For example, here, we would need 6*computing_time_for_d to be able to compute for d+1. (d) ran a beam search
at d+1 if the full search was not possible.

(4) answers to any questions asked below in the assignment.
No additional questions
'''

import sys
import numpy as np
import copy
import time
import signal

losing_seq = []
heuristic = ""

def printable_board(board):
  return "\n".join([ " ".join(row) for row in board])

def printable_board_flat(board):
  return "".join([ "".join(row) for row in board])

  
def sequences(n, k):
  positions_groups = []
  seq = (
    [[[(x, y+z) for y in range(k)] for z in range(n-k+1) ] for x in range(n)] + # horizontals
    [[[(x+z, y) for x in range(k)] for z in range(n-k+1) ] for y in range(n)] + # verticals
    [[[(d+x, d+z) for d in range(k)] for x in range(n-k+1) ] for z in range(n-k+1)] + #diag TL BR
    [[[(n-1-d-x, d+z) for d in range(k)] for x in range(n-k+1) ] for z in range(n-k+1)] # diagonal BL TR
  )
  for s in seq:
   for d in s:
    positions_groups.append(d)
  return np.array(positions_groups)

def game_heuristic(board, n, k, seq):
    w = b = 0 #scores for white and black
    empty_spot = zip(*np.where(board == '.'))
    white_pos = zip(*np.where(board == 'w'))
    blck_pos =  zip(*np.where(board == 'b'))
    for seq in losing_seq:
      vals = [ board[x,y] for [x,y] in seq ]
      if vals.count('b') == 0: #where w can lose
        w += 1 + sum( 3**i for i in range(vals.count('w')) )
      if vals.count('w') == 0: #where b can lose
        b += 1 + sum( 3**i for i in range(vals.count('b')) )
    return b - w


# Check whether game has ended and whether there is a tie, a win, or a lose
def game_status(board, n, k):
  for seq in losing_seq:
    vals = [ board[x,y] for [x,y] in seq ]
    if all(v == 'b' for v in vals): return True, sys.maxsize
    if all(v == 'w' for v in vals): return True, -sys.maxsize
  if all('.' not in row for row in board): return True, 0
  return False, game_heuristic(board, n, k, seq)

# Add a piece to the board at the given position, and return a new board (doesn't change original)
def add_piece(board, row, col, color):
    newboard = copy.deepcopy(board)
    newboard[row,col] = color
    return newboard
  
def successor(board, color):
  empty = zip(*np.where(board == '.'))
  return [ add_piece(board, row, col, color) for (row, col) in empty ]
    
def alphaBetaSearchIDS(board, n, k, timeout_duration):
  '''returns fringe of moves at max depth that can be computed within time limit'''
  # hash table to store move order
  order = {}
  depth = 1
  state_count = (board == '.').sum() #how many states are explored at each depth
  start = time.clock()
  while depth <= state_count:
    curr_start = time.clock()
    score, new_board, node_count = alphaBetaMinimax(board, n, k, -sys.maxsize, sys.maxsize, depth, 0, order, 0)
    if game_status(new_board, n, k)[0] == True:
      return new_board #if game ended
    time_used_at_depth = time.clock() - curr_start
    time_elapsed = time.clock() - start
    time_left = timeout_duration - time_elapsed
    if time_left / time_used_at_depth < state_count - depth: #there are this many times more states to explore at depth+1
      if heuristic == "b": return new_board
      if heuristic == "a":
        nodes_at_fringe = np.floor( 0.7* time_left / time_used_at_depth * node_count - node_count )
        if nodes_at_fringe > 0:
          score, new_board, node_count = alphaBetaMinimaxForwardPrune(board, n, k, -sys.maxsize, sys.maxsize, depth+1, 0, order, 0, nodes_at_fringe)
          print ("time", time.clock() - start)
        return new_board
    depth += 1
  return new_board
  
def alphaBetaMinimaxForwardPrune(board, n, k, alpha, beta, depth_limit, depth, order, node_count, max_nodes):
  #check whether leaf node has been reached
  end, status = game_status(board, n, k)
  if end is True: return status, board, node_count
  if depth >= depth_limit: 
    node_count += 1 # number of nodes that can be expanded one level further
    return status, board, node_count
  if node_count >= max_nodes: 
    return status, board, node_count
  #find whose turn it is
  color = 'b' if len(board[board == 'w']) > len(board[board == 'b']) else 'w'
  # get successors
  successors = successor(board, color)
  # keep only ordered successors if this depth has already been explored:
  if str(board) in order: 
    successors = [ successors[i] for i in order[ str(board) ] ]
    if len(successors) > 1: del successors[-1]
  best_move = np.array([])
  scores = []
  #if MAX's turn
  if color == 'w':     
    for s in successors:
      result, newboard, node_count = alphaBetaMinimax(s, n, k, alpha, beta, depth_limit, depth+1, order, node_count)
      # keep track of scores for each successor
      scores.append(result)
      if best_move.shape[0] == 0: best_move = s
      if result > alpha:
        alpha = result
        # keep track of best move for current player
        best_move = s 
      if alpha >= beta:
        break
    # store moves in decreasing value order
    if str(board) not in order: order[str(board)] = sorted(range(len(scores)), key=lambda k: scores[k], reverse = True)
    return alpha, best_move, node_count
  #if MIN's turn
  if color == 'b':
    for s in successors:
      result, newboard, node_count = alphaBetaMinimax(s, n, k, alpha, beta, depth_limit, depth+1, order, node_count)
      scores.append(result)
      if best_move.shape[0] == 0: best_move = s
      if result < beta:
        beta = result
        best_move = s
      if alpha >= beta:
        break
    # store moves in increasing value order
    if str(board) not in order: order[str(board)] = order[str(board)] = sorted(range(len(scores)), key=lambda k: scores[k])
    return beta, best_move, node_count


def alphaBetaMinimax(board, n, k, alpha, beta, depth_limit, depth, order, node_count):
  node_count += 1
  #check whether leaf node has been reached
  end, status = game_status(board, n, k)
  if end is True: return status, board, node_count
  if depth >= depth_limit: 
    return status, board, node_count
  #find whose turn it is
  color = 'b' if len(board[board == 'w']) > len(board[board == 'b']) else 'w'
  # get successors
  successors = successor(board, color)
  temp = len(successors)
  # keep only ordered successors if this depth has already been explored:
  if str(board) in order: 
    successors = [ successors[i] for i in order[ str(board) ] ]
  best_move = np.array([])
  scores = []
  #if MAX's turn
  if color == 'w':     
    for s in successors:
      result, newboard, node_count = alphaBetaMinimax(s, n, k, alpha, beta, depth_limit, depth+1, order, node_count)
      # keep track of scores for each successor
      scores.append(result)
      if best_move.shape[0] == 0: best_move = s
      if result > alpha:
        alpha = result
        # keep track of best move for current player
        best_move = s 
      if alpha >= beta:
        break
    # store moves in decreasing value order
    if str(board) not in order: order[str(board)] = sorted(range(len(scores)), key=lambda k: scores[k], reverse = True)
    return alpha, best_move, node_count
  #if MIN's turn
  if color == 'b':
    for s in successors:
      result, newboard, node_count = alphaBetaMinimax(s, n, k, alpha, beta, depth_limit, depth+1, order, node_count)
      scores.append(result)
      if best_move.shape[0] == 0: best_move = s
      if result < beta:
        beta = result
        best_move = s
      if alpha >= beta:
        break
    # store moves in increasing value order
    if str(board) not in order: order[str(board)] = order[str(board)] = sorted(range(len(scores)), key=lambda k: scores[k])
    return beta, best_move, node_count
    
# if "__main__" == __name__:
#   n, k, board, time_lim, h = int(sys.argv[1]), int(sys.argv[2]), str(sys.argv[3]),  int(sys.argv[4]), str(sys.argv[5])
#   # find all possible sequence positions in board
#   losing_seq = sequences(n,k)
#   heuristic = h
#   board = np.reshape(list(board), (n, n))
#   print ( "current board:")
#   print (printable_board(board))
#   end, status = game_status(board, n, k)
#   result = ": white won." if status == sys.maxsize else ": black won." if status == -sys.maxsize else " with a draw."
#   if end is True: 
#     print ( "Game has ended" + result )
#     quit()
#   # let the algorithm pick a move!
#   #print ( printable_board( alphaBetaSearchIDS(board, n, k, time_lim) ))  
#   print (printable_board_flat( alphaBetaSearchIDS(board, n, k, time_lim) ))  
  
if "__main__" == __name__:
  n, k, board, time_lim, h = int(sys.argv[1]), int(sys.argv[2]), str(sys.argv[3]),  int(sys.argv[4]), str(sys.argv[5])
  # find all possible sequence positions in board
  losing_seq = sequences(n,k)
  heuristic = h
  board = np.reshape(list(board), (n, n))
  print ( "current board:")
  print (printable_board(board))
  print("starting heuristic", heuristic, "gets white")
  while True:
    end, status = game_status(board, n, k)
    result = ": white won." if status == sys.maxsize else ": black won." if status == -sys.maxsize else " with a draw."
    if end is True: 
      print ( "Game has ended" + result )
      quit()
    board = alphaBetaSearchIDS(board, n, k, time_lim)
    print (printable_board( board )) 
    if heuristic == "a": heuristic = "b"
    else: heuristic = "a"
  # let the algorithm pick a move!
  #print ( printable_board( alphaBetaSearchIDS(board, n, k, time_lim) ))  
  #print (printable_board_flat( alphaBetaSearchIDS(board, n, k, time_lim) ))  
