
#https://www.cs.swarthmore.edu/~meeden/cs63/f05/minimax.html (pseudocode from here)
#http://codereview.stackexchange.com/a/24775 (ideas for victory check)

#things to try for alpha-beta:
#transposition table
#use of IDS to order branch exploration

'''
timeout function inspired by @ http://stackoverflow.com/questions/492519/timeout-on-a-function-call
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
    w = b = 0 #scores so far
    empty_spot = zip(*np.where(board == '.'))
    white_pos = zip(*np.where(board == 'w'))
    blck_pos =  zip(*np.where(board == 'b'))
    for seq in losing_seq:
      vals = [ board[x,y] for [x,y] in seq ]
      if vals.count('b') == 0:
        w += 1 + sum( 3**i for i in range(vals.count('w')) )
      if vals.count('w') == 0:
        b += 1 + sum( 3**i for i in range(vals.count('b')) )
    if heuristic == "a": 
      return w - b
    if heuristic == "b": 
      return 0
    else: 
      print("wrong heuristic")
      quit()

# Check whether game has ended and whether there is a tie, a win, or a lose
def game_status(board, n, k):
  #print (board)
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
  # hash table to store move order
  order = {}
  depth = 1
  state_count = (board == '.').sum() #how many states are explored at each depth
  start = time.clock()
  while depth <= state_count:
    print (depth)
    score, new_board = alphaBetaMinimax(board, n, k, -sys.maxsize, sys.maxsize, depth, 0, order)
    print("new_board", new_board)
    if game_status(new_board, n, k)[0] == True: return new_board #if game ended
    time_used = time.clock() - start
    time_left = timeout_duration - time_used
    print (time_left, time_used, time_left/time_used, state_count - depth, "depth", depth)
    if time_left / time_used < state_count - depth: #there are this many times more states to explore at depth+1
      print ("exit", time_left, time_used, time_left/time_used, state_count - depth, "depth", depth)
      return new_board #no time to add additional depth
    depth += 1
  return new_board

def alphaBetaMinimax(board, n, k, alpha, beta, depth_limit, depth, order):
  #check whether leaf node has been reached
  end, status = game_status(board, n, k)
  if end is True: return status, board
  if depth >= depth_limit: return status, board
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
      result, newboard = alphaBetaMinimax(s, n, k, alpha, beta, depth_limit, depth+1, order)
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
    return alpha, best_move
  #if MIN's turn
  if color == 'b':
    for s in successors:
      result, newboard = alphaBetaMinimax(s, n, k, alpha, beta, depth_limit, depth+1, order)
      scores.append(result)
      if best_move.shape[0] == 0: best_move = s
      if result < beta:
        beta = result
        best_move = s
      if alpha >= beta:
        break
    # store moves in increasing value order
    if str(board) not in order: order[str(board)] = order[str(board)] = sorted(range(len(scores)), key=lambda k: scores[k])
    return beta, best_move
    
if "__main__" == __name__:
  n, k, board, time_lim, h = int(sys.argv[1]), int(sys.argv[2]), str(sys.argv[3]),  int(sys.argv[4]), str(sys.argv[5])
  # find all possible sequence positions in board
  losing_seq = sequences(n,k)
  heuristic = h
  board = np.reshape(list(board), (n, n))
  print ( "current board:")
  print (printable_board(board))
  end, status = game_status(board, n, k)
  result = ": white won." if status == sys.maxsize else ": black won." if status == -sys.maxsize else " with a draw."
  if end is True: 
    print ( "Game has ended" + result )
    quit()
  # let the algorithm pick a move!
  #print ( alphaBetaSearchIDS(board, n, k, time) )  
  print (printable_board_flat( alphaBetaSearchIDS(board, n, k, time_lim) ))  
