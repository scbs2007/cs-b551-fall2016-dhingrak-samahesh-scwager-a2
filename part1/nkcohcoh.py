#https://www.cs.swarthmore.edu/~meeden/cs63/f05/minimax.html (pseudocode from here)
#http://codereview.stackexchange.com/a/24775 (ideas for victory check)

import sys
import numpy as np

losing_seq = []
  
def printable_board(board):
  return "\n".join([ " ".join(row) for row in board])
  
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
  
# Check whether game has ended and whether there is a tie, a win, or a lose
def game_status(board, n, k):
  for seq in losing_seq:
    vals = [ board[x,y] for [x,y] in seq ]
    if all(v == 'b' for v in vals): return True, 1
    if all(v == 'w' for v in vals): return True, -1
  if all('.' not in row for row in board): return True, 0
  return False, 0
    
# Add a piece to the board at the given position, and return a new board (doesn't change original)
def add_piece(board, row, col, color):
    return board[0:row] + [board[row][0:col] + [color,] + board[row][col+1:]] + board[row+1:]  
  
def successor(board, color):
  empty = zip(*np.where(board == '.'))
  return [ add_piece(board, row, col) for (row, col) in empty ]

#need to implement this
def branching_factor_function(time):
  return 20

def alphaBetaSearch(board, n, k, time):
  depth_limit = branching_factor_function(time)
  val, newboard = alphaBetaMinimax(board, n, k, -sys.maxint, sys.maxint, depth_limit, 0)
  return newboard

def alphaBetaMinimax(board, n, k, alpha, beta, depth_limit, depth):
  #check for leaf nodes
  end, status = game_status(board, n, k)
  if end is True: return status, board
  if depth >= depth_limit: return status, board
  #find whose turn it is
  color = 'b' if len(board[board == 'w']) > len(board[board == 'b']) else 'w'
  #get successors
  successors = successor(board, color)
  #if MAX's turn
  if color == 'w':
    for s in successors:
      result, newboard = alphaBetaMinimax(s, n, k, alpha, beta, depth_limit, depth+1)
      if result > alpha:
        alpha = result
      if alpha >= beta:
        return alpha, s
    return alpha, s
  #if MIN's turn
  if color == 'b':
    for s in successors:
      result, newboard = alphaBetaMinimax(s, n, k, alpha, beta, depth_limit, depth+1)
      if result < beta:
        beta = result
      if beta <= alpha:
        return beta, s
    return beta, s

if "__main__" == __name__:
  n, k, board, time = int(sys.argv[1]), int(sys.argv[2]), str(sys.argv[3]),  int(sys.argv[4])
  losing_seq = sequences(n,k)
  board = np.reshape(list(board), (n, n))
  print ( "current board:")
  print (printable_board(board))
  end, status = game_status(board, n, k)
  result = ": white won." if status == 1 else ": black won." if status == -1 else " with a draw."
  if end is True: 
    print ( "Game has ended" + result )
    quit()
  print ( alphaBetaSearch(board, n, k, time) )
  
  
  
  