# Simple tetris program! v0.2
# D. Crandall, Sept 2016

from AnimatedTetris import *
from SimpleTetris import *
from kbinput import *
from multiprocessing.dummy import Pool as ThreadPool 
from operator import itemgetter
#from functools import partial
import time, sys, copy, itertools

class HumanPlayer:
    def get_moves(self, tetris):
        print "Type a sequence of moves using: \n  b for move left \n  m for move right \n  n for rotation\nThen press enter. E.g.: bbbnn\n"
        moves = raw_input()
        return moves

    def control_game(self, tetris):
        while 1:
            c = get_char_keyboard()
            commands =  { "b": tetris.left, "n": tetris.rotate, "m": tetris.right, " ": tetris.down }
            commands[c]()

#####
# This is the part you'll want to modify!
# Replace our super simple algorithm with something better
#
class ComputerPlayer:
    # This function should generate a series of commands to move the piece into the "optimal"
    # position. The commands are a string of letters, where b and m represent left and right, respectively,
    # and n rotates. tetris is an object that lets you inspect the board, e.g.:
    #   - tetris.col, tetris.row have the current column and row of the upper-left corner of the 
    #     falling piece
    #   - tetris.get_piece() is the current piece, tetris.get_next_piece() is the next piece after that
    #   - tetris.left(), tetris.right(), tetris.down(), and tetris.rotate() can be called to actually
    #     issue game commands
    #   - tetris.get_board() returns the current state of the board, as a list of strings.
    #
    def get_moves(self, tetris):
        # super simple current algorithm: just randomly move left, right, and rotate a few times
        return random.choice("mnb") * random.randint(1, 10)
       
    # This is the version that's used by the animted version. This is really similar to get_moves,
    # except that it runs as a separate thread and you should access various methods and data in
    # the "tetris" object to control the movement. In particular:
    #   - tetris.col, tetris.row have the current column and row of the upper-left corner of the 
    #     falling piece
    #   - tetris.get_piece() is the current piece, tetris.get_next_piece() is the next piece after that
    #   - tetris.left(), tetris.right(), tetris.down(), and tetris.rotate() can be called to actually
    #     issue game commands
    #   - tetris.get_board() returns the current state of the board, as a list of strings.
    #
    def control_game(self, tetris):
        # O, J, I, T, Z - Key is found by " ".join(piece orientation)
        allPossiblePieces = \
        {'xx xx': [['xx','xx']], \
        \
        ' x  x xx': [[' x', ' x', 'xx'], ['x  ', 'xxx'], ['xx', 'x ', 'x '], ['xxx', '  x']], \
        'x   xxx': [[' x', ' x', 'xx'], ['x  ', 'xxx'], ['xx', 'x ', 'x '], ['xxx', '  x']], \
        'xx x  x ': [[' x', ' x', 'xx'], ['x  ', 'xxx'], ['xx', 'x ', 'x '], ['xxx', '  x']], \
        'xxx   x': [[' x', ' x', 'xx'], ['x  ', 'xxx'], ['xx', 'x ', 'x '], ['xxx', '  x']], \
        \
        'x x x x': [['x', 'x', 'x', 'x'], ['xxxx']], \
        'xxxx': [['x', 'x', 'x', 'x'], ['xxxx']], \
        \
        'xxx  x ': [['xxx', ' x '], [' x', 'xx', ' x'], [' x ', 'xxx'], ['x ', 'xx', 'x ']], \
        ' x xx  x': [['xxx', ' x '], [' x', 'xx', ' x'], [' x ', 'xxx'], ['x ', 'xx', 'x ']], \
        ' x  xxx': [['xxx', ' x '], [' x', 'xx', ' x'], [' x ', 'xxx'], ['x ', 'xx', 'x ']], \
        'x  xx x ': [['xxx', ' x '], [' x', 'xx', ' x'], [' x ', 'xxx'], ['x ', 'xx', 'x ']], \
        \
        'xx   xx': [['xx ', ' xx'], [' x', 'xx', 'x ']], \
        ' x xx x ': [['xx ', ' xx'], [' x', 'xx', 'x ']]}
        
        while 1:
            time.sleep(0.1)
            
            board = tetris.get_board()
            piece = tetris.get_piece()[0]
            pieceAsString = " ".join(piece)
            #print "Piece::: \n"
            #print piece
            #print "Next Piece::: \n"
            #print tetris.get_next_piece()
            allRotations = allPossiblePieces[pieceAsString]
            pool = ThreadPool(len(allRotations))
            #func = partial(self.calculateScore, board)
            
            results = pool.map(self.findBestPositionForPiece, zip(allRotations, [board] * len(allRotations)))
            maxResult = max(results, key=itemgetter(0))
            
            toPlaceAtColumnIndex = maxResult[1]
            maxHeuristicPieceIndex = results.index(maxResult)
            print "Result: "
            print results
            print"------"
            print maxHeuristicPieceIndex
            print"------"
            print "All Rotations: "
            print allRotations[maxHeuristicPieceIndex]
            print "piece"
            print piece
            if(piece !=  allRotations[maxHeuristicPieceIndex]):
                #print"Rotate"
                piece = tetris.get_piece()[0]
                tetris.rotate()
                
            sys.exit(0)
            if(toPlaceAtColumnIndex < tetris.col):
                tetris.left()
            elif(toPlaceAtColumnIndex > tetris.col):
                tetris.right()
            else:
                tetris.down()
            pool.close()
            pool.join()

    def findBestPositionForPiece(self, argument):
        piece, board = argument
        #board = board[0:19] + ['xxxxxxxxx ']
        columnHeights = map(lambda x: 20 - x, self.findColumnHeights(board))
        possibleIndexes = []
        for col in range(0, 10):
            index = columnHeights[col]
            rowIndexToPlaceAt = index - len(piece)
            #print piece
            #print (rowIndexToPlaceAt, col)
            val = TetrisGame.check_collision((board, 0), piece, rowIndexToPlaceAt, col)
            if(val == False):
                possibleIndexes.append((rowIndexToPlaceAt, col))
        #print "HERE--"
        #print possibleIndexes
        numberOfThreads = len(possibleIndexes)
        if numberOfThreads == 0:
            return None
        pool = ThreadPool(numberOfThreads)
        results = pool.map(self.calculateHeuristicValue, zip([piece] * numberOfThreads, [board] * numberOfThreads, possibleIndexes))
        #maxHeuristicIndex = results.index(max(results))
        #print "Results: "
        #print(results)
        pool.close()
        pool.join()
        maxHeuristicValue = max(results)
        return (maxHeuristicValue, results.index(maxHeuristicValue))

    def calculateHeuristicValue(self, argument):
        # https://codemyroad.wordpress.com/2013/04/14/tetris-ai-the-near-perfect-player/
        
        a = -0.510066
        b = 0.760666
        c = -0.35663
        d = -0.184483

        #print "ARGUMENT: \n" 
        #print argument[0]
        #print argument[2]
        #print "\n"
        #sys.exit(0)
        piece, board, rowCol = argument
        
        # Place piece on board for calculating heuristic score
        board = TetrisGame.place_piece((board, 0), piece, rowCol[0], rowCol[1])[0]
        #print "ADDED PIECE: "
        #print "\n".join(board)
        # Calculate heuristic
        return a * self.calculateAggregateColumnHeights(board) + \
                    b * self.findNumberOfCompleteLines(board) + \
                    c * self.findNumberOfHoles(board) + \
                    d * self.calculateBumpiness(board)
        

    def findColumnHeights(self, board):
        heights = []
        for col in range(0, len(board[0])):
            flag = 0
            for row in range(0, len(board)):
                if board[row][col] == "x":
                    heights.append(20 - row)
                    flag =1
                    break
            if flag == 0:
                heights.append(0)
        return heights
        #return [max([(19 - row) for row in range(0, len(board)) if board[row][col] == "x"] + [0, ]) for col in range(0, len(board[0]))]

    def calculateAggregateColumnHeights(self, board):
        return sum(self.findColumnHeights(board))

    def findNumberOfCompleteLines(self, board):
        return sum([1 for row in board if all(cellValue == "x" for cellValue in row)])
    
    def findNumberOfHoles(self, board):
        columnHeights = map(lambda x: 20 - x, self.findColumnHeights(board))
        holes = 0
        for i in range(0, len(board[0])):
            if columnHeights[i] != 20:
                for j in range(len(board) - 1, columnHeights[i], -1):
                    if board[j][i] == " ":
                        holes += 1
        return holes
        #return sum([sum([1 for row in range(len(board) - 1, map(lambda x: 19 if x == 0 else 20 - x, findColumnHeights(board))[col], -1) if board[row][col] == " "]) \
        #        for col in range(0, len(board[0]))])

    def calculateBumpiness(self, board):
        columnHeights = self.findColumnHeights(board)
        return sum([abs(columnHeights[index] - columnHeights[index + 1])  for index in range(len(columnHeights) - 1)])
        
    def professors_control_game(self, tetris):
        # another super simple algorithm: just move piece to the least-full column
        while 1:
            time.sleep(0.1)

            board = tetris.get_board()
            column_heights = [ min([ r for r in range(len(board) - 1, 0, -1) if board[r][c] == "x"  ] + [100,] ) for c in range(0, len(board[0]) ) ]
            index = column_heights.index(max(column_heights))

            if(index < tetris.col):
                tetris.left()
            elif(index > tetris.col):
                tetris.right()
            else:
                tetris.down()


###################
#### main program

(player_opt, interface_opt) = sys.argv[1:3]

try:
    if player_opt == "human":
        player = HumanPlayer()
    elif player_opt == "computer":
        player = ComputerPlayer()
    else:
        print "unknown player!"

    if interface_opt == "simple":
        tetris = SimpleTetris()
    elif interface_opt == "animated":
        tetris = AnimatedTetris()
    else:
        print "unknown interface!"

    tetris.start_game(player)

except EndOfGame as s:
    print "\n\n\n", s



