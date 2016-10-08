
import sys
import numpy as np

# Return a string with the board rendered in a human-friendly format                                                                                      
def printable_board(board, n):
  return " ".join([ "\n" + elem if i % n == 0 else elem for i, elem in enumerate(board) ]) 
  
# Return all possible losing sequences (row, column, diagonal up, diagonal down)
def sequence(n, k, color):
  return [ (color +'.'*j) * (k-1) + color for j in [0, n-1, n-2, n] ]
  
# Check whether there is a tie, a win, or a lose
def game_outcome(board, n, k):
  if any(s in board for s in sequence(n,k,'w')):
    return -1
  if any(s in board for s in sequence(n,k,'b')):
    return 1
  return 0
  
# Do we need something like this?
def game_ended(board):
  if '.' not in board:
    return True

if "__main__" == __name__:
  n, k, board, time = int(sys.argv[1]), int(sys.argv[2]), str(sys.argv[3]),  int(sys.argv[4])
  #n, k, board, time = [f(v) for (f, v) in zip((int, int, str, int, lambda v: v == 'True'), line.split())]
  print ( printable_board(board,n) )
  print ( "current outcome", game_outcome(board, n, k) )
  
  
  
  