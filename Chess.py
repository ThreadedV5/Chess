import pygame, sys, random
from pygame.locals import *
import copy

# abstract class for all chess pieces
class piece(object):
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.hasMoved = False

        # A list of moves, abstracting dependency on prior elements
        # (Consider subset forward of a rook, moving forward 6 is only possible
        #  If you can move forward 5)
        self.lineOfSight = []

        # A list of lineOfSights
        self.lineOfSightList = []
        
        # Line Of Sights, truncated vision (Also handles castling)
        self.truncatedLineOfSights = [] 

        # The final list of moves, 
        # filtered for illegal moves which blunder the king,
        self.trueMoves = []
        self.updateFreeMoves()
        
    def getCoords(self):
        return([self.x,self.y])
    
    def getColor(self):
        return(self.color)
    # Checks if coords lie on board, appends to self.lineOfSight
    def validateFreeMoveIsOnBoard(self, coords):
        if coords[0] >= 0 and coords[0] <= 7 and coords[1] >= 0 and coords[1] <= 7:
            self.lineOfSight.append(coords)
            return True
        else:
            return False
    
    # pop free moves and add it to lineOfSight
    def appendSubsetMoves(self):
        if len(self.lineOfSight) != 0:
            self.lineOfSightList.append(self.lineOfSight)
            self.lineOfSight = []
    
    # Filters lineOfSightList
    # Truncates lineOfSights to the first piece seen
    # Updates truncatedLineOfSights
    def truncateLineOfSights(self, board):
        self.truncatedLineOfSights = []
        for lineOfSight in self.lineOfSightList:
            for j in range(len(lineOfSight)):
                rank = lineOfSight[j][1]
                file = lineOfSight[j][0]
                if board[rank][file] is not None:
                    if self.color == board[rank][file].color:
                        # Same colour piece, end lineOfSight
                        break
                    else:
                        # Different colour piece, take and end lineOfSight
                        self.truncatedLineOfSights.append(lineOfSight[j])
                        break
                else:
                    self.truncatedLineOfSights.append(lineOfSight[j])

    #limits truncatedLineOfSights to only legal moves
    def updateTrueMoves(self, gameBoard, board):
        self.trueMoves = []
        for i in self.truncatedLineOfSights:
            if gameBoard.checkLegal(board, self.getCoords(), i):
                self.trueMoves.append(i)

    
    #checks if a piece has a king in sight
    def validateCheckKing(self, coords):
        if coords in self.truncatedLineOfSights:
            return True
        else:
            return False
        
        

class pawn(piece):
    def __init__(self, x, y, color):
        self.enPassantAble = False
        super().__init__(x, y, color)
    
    def updateFreeMoves(self):
        self.lineOfSightList = []
        self.lineOfSight = []
        if self.color == 'W':
            self.validateFreeMoveIsOnBoard([self.x,self.y+1])
            if not self.hasMoved:
                self.validateFreeMoveIsOnBoard([self.x,self.y+2])
        else:
            self.validateFreeMoveIsOnBoard([self.x,self.y-1])
            if not self.hasMoved:
                self.validateFreeMoveIsOnBoard([self.x,self.y-2])
        self.appendSubsetMoves()
    def truncateLineOfSights(self,board):
        self.truncatedLineOfSights = []
        for i in self.lineOfSightList:
            for j in range(len(i)):
                if board[i[j][1]][i[j][0]] is not None:
                    break
                else:
                    self.truncatedLineOfSights.append(i[j])
        #allow taking diagonally
        if self.getColor() == "W":
            step = 1
        else:
            step = -1
        if self.y + step >= 0 and self.y + step <= 7:
            if self.x + 1 >= 0 and self.x + 1 <= 7:
                if board[self.y + step][self.x + 1] is not None:
                    if board[self.y + step][self.x + 1].getColor() != self.getColor():
                        self.truncatedLineOfSights.append([self.x+1,self.y+step])
            if self.x - 1 >= 0 and self.x - 1 <= 7:
                if board[self.y + step][self.x - 1] is not None:
                    if board[self.y + step][self.x - 1].getColor() != self.getColor():
                        self.truncatedLineOfSights.append([self.x - 1,self.y + step])
        #allow en passant
        if (self.getColor() == "W" and self.y == 4) or (self.getColor() == "B" and self.y == 3):
            if self.x + 1 >= 0 and self.x + 1 <= 7:
                if board[self.y][self.x + 1] is not None:
                    if board[self.y][self.x + 1].getChr() == "P":
                        if board[self.y][self.x + 1].enPassantAble == True:
                            self.truncatedLineOfSights.append([self.x+1,self.y+step])
            if self.x - 1 >= 0 and self.x - 1 <= 7:
                if board[self.y][self.x - 1] is not None:
                    if board[self.y][self.x - 1].getChr() == "P":
                        if board[self.y][self.x - 1].enPassantAble == True:
                            self.truncatedLineOfSights.append([self.x-1,self.y+step])
        
            

    def disableEnPassant(self):
        self.enPassantAble = False
    def enableEnPassant(self):
        self.enPassantAble = True
    def getChr(self):
        return('P')

class rook(piece):
    def updateFreeMoves(self):
        self.lineOfSightList = []
        self.lineOfSight = []
        count = 1
        while self.validateFreeMoveIsOnBoard([self.x, self.y + count]): count += 1
        self.appendSubsetMoves()
        count = 1
        while self.validateFreeMoveIsOnBoard([self.x, self.y - count]): count += 1
        self.appendSubsetMoves()
        count = 1
        while self.validateFreeMoveIsOnBoard([self.x + count, self.y]): count += 1
        self.appendSubsetMoves()
        count = 1
        while self.validateFreeMoveIsOnBoard([self.x - count, self.y]): count += 1
        self.appendSubsetMoves()
        
    def getChr(self):
        return('R')

class knight(piece):
    def updateFreeMoves(self):
        self.lineOfSightList = []
        self.lineOfSight = []
        self.validateFreeMoveIsOnBoard([self.x+1,self.y+2])
        self.appendSubsetMoves()
        self.validateFreeMoveIsOnBoard([self.x-1,self.y+2])
        self.appendSubsetMoves()
        self.validateFreeMoveIsOnBoard([self.x+1,self.y-2])
        self.appendSubsetMoves()
        self.validateFreeMoveIsOnBoard([self.x-1,self.y-2])
        self.appendSubsetMoves()
        self.validateFreeMoveIsOnBoard([self.x+2,self.y+1])
        self.appendSubsetMoves()
        self.validateFreeMoveIsOnBoard([self.x+2,self.y-1])
        self.appendSubsetMoves()
        self.validateFreeMoveIsOnBoard([self.x-2,self.y+1])
        self.appendSubsetMoves()
        self.validateFreeMoveIsOnBoard([self.x-2,self.y-1])
        self.appendSubsetMoves()
    def getChr(self):
        return('N')

class bishop(piece):
    def updateFreeMoves(self):
        self.lineOfSightList = []
        self.lineOfSight = []
        count = 1
        while self.validateFreeMoveIsOnBoard([self.x + count, self.y + count]) == 1: count += 1
        self.appendSubsetMoves()
        count = 1
        while self.validateFreeMoveIsOnBoard([self.x + count, self.y - count]) == 1: count += 1
        self.appendSubsetMoves()
        count = 1
        while self.validateFreeMoveIsOnBoard([self.x - count, self.y + count]) == 1: count += 1
        self.appendSubsetMoves()
        count = 1
        while self.validateFreeMoveIsOnBoard([self.x - count, self.y - count]) == 1: count += 1
        self.appendSubsetMoves()
    def getChr(self):
        return('B')

class queen(piece):
    def updateFreeMoves(self):
        self.lineOfSightList = []
        self.lineOfSight = []
        count = 1
        while self.validateFreeMoveIsOnBoard([self.x + count, self.y + count]) == 1: count += 1
        self.appendSubsetMoves()
        count = 1
        while self.validateFreeMoveIsOnBoard([self.x + count, self.y - count]) == 1: count += 1
        self.appendSubsetMoves()
        count = 1
        while self.validateFreeMoveIsOnBoard([self.x - count, self.y + count]) == 1: count += 1
        self.appendSubsetMoves()
        count = 1
        while self.validateFreeMoveIsOnBoard([self.x - count, self.y - count]) == 1: count += 1
        self.appendSubsetMoves()
        count = 1
        while self.validateFreeMoveIsOnBoard([self.x, self.y + count]): count += 1
        self.appendSubsetMoves()
        count = 1
        while self.validateFreeMoveIsOnBoard([self.x, self.y - count]): count += 1
        self.appendSubsetMoves()
        count = 1
        while self.validateFreeMoveIsOnBoard([self.x + count, self.y]): count += 1
        self.appendSubsetMoves()
        count = 1
        while self.validateFreeMoveIsOnBoard([self.x - count, self.y]): count += 1
        self.appendSubsetMoves()
    def getChr(self):
        return('Q')

class king(piece):
    def updateFreeMoves(self):
        self.lineOfSightList = []
        self.lineOfSight = []
        self.validateFreeMoveIsOnBoard([self.x,self.y-1])
        self.appendSubsetMoves()
        self.validateFreeMoveIsOnBoard([self.x+1,self.y-1])
        self.appendSubsetMoves()
        self.validateFreeMoveIsOnBoard([self.x+1,self.y])
        self.appendSubsetMoves()
        self.validateFreeMoveIsOnBoard([self.x+1,self.y+1])
        self.appendSubsetMoves()
        self.validateFreeMoveIsOnBoard([self.x,self.y+1])
        self.appendSubsetMoves()
        self.validateFreeMoveIsOnBoard([self.x-1,self.y+1])
        self.appendSubsetMoves()
        self.validateFreeMoveIsOnBoard([self.x-1,self.y])
        self.appendSubsetMoves()
        self.validateFreeMoveIsOnBoard([self.x-1,self.y-1])
        self.appendSubsetMoves()
    def truncateLineOfSights(self,board):
        super().truncateLineOfSights(board)
        # enable castling
        if self.hasMoved == False:
            if board[self.y][0] is not None:
                if board[self.y][0].hasMoved == False:
                    if board[self.y][1] is None and board[self.y][2] is None:
                        self.truncatedLineOfSights.append([1,self.y])
            if board[self.y][7] is not None:
                if board[self.y][7].hasMoved == False:
                    if board[self.y][4] is None and board[self.y][5] is None and board[self.y][6] is None:
                        self.truncatedLineOfSights.append([5,self.y])
                        
    def getChr(self):
        return('K')

class gameBoard:
    def __init__(self):
        self.board =[
         [rook(0,0,'W'), knight(1,0,'W'), bishop(2,0,'W'), king(3,0,'W'), queen(4,0,'W'), bishop(5,0,'W'), knight(6,0,'W'), rook(7,0,'W')], 
         [pawn(x,1,'W') for x in range(8)], 
         [None, None, None, None, None, None, None, None], 
         [None, None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None, None],
         [None, None, None, None, None, None, None, None],
         [pawn(x,6,'B') for x in range(8)],
         [rook(0,7,'B'), knight(1,7,'B'), bishop(2,7,'B'), king(3,7,'B'), queen(4,7,'B'), bishop(5,7,'B'), knight(6,7,'B'), rook(7,7,'B')]
         ]
        self.turn = "W"
        self.truncateLineOfSights(self.board)
        self.updateTrueMoves(self.board)
        self.gameOver = False
        

    #find all available moves for all pieces
    def truncateLineOfSights(self, board):
        for i in board:
            for j in i:
                if j is not None:
                    j.truncateLineOfSights(board)
    def updateTrueMoves(self, board):
        for i in board:
            for j in i:
                if j is not None:
                    j.updateTrueMoves(self, board)

    #returns the coords of the color of a king   
    def findKing(self, board, color):
        for i in board:
            for j in i:
                if j is not None:
                    if j.getChr() == 'K':
                        if j.getColor() == color:
                            return j.getCoords()

    #returns either True or False given a board
    def evalWhiteInCheck(self, board):
        kingCoords = self.findKing(board,'W')
        for i in board:
            for j in i:
                if j is not None:
                    if j.getColor() == 'B':
                        if j.validateCheckKing(kingCoords):
                            return True
        return False
    
    def evalBlackInCheck(self, board):
        kingCoords = self.findKing(board,'B')
        for i in board:
            for j in i:
                if j is not None:
                    if j.getColor() == 'W':
                        if j.validateCheckKing(kingCoords):
                            return True
        return False

    def clearEnPassant(self, board):
        for i in board:
            for j in i:
                if j is not None:
                    if j.getChr() == 'P':
                        j.disableEnPassant()

    def verifyWhiteCheckmate(self, board):
        count = 0
        for i in board:
            for j in i:
                if j is not None:
                    if j.getColor() == 'B':
                        count += len(j.trueMoves)
        if count == 0:
            return True
        else:
            return False

    def verifyBlackCheckmate(self, board):
        count = 0
        for i in board:
            for j in i:
                if j is not None:
                    if j.getColor() == 'W':
                        count += len(j.trueMoves)
        if count == 0:
            return True
        else:
            return False
        
    # Takes two co-ordinates
    # Returns true if a move was made
    def requestMove(self, oldCoords, newCoords):
        if self.board[oldCoords[1]][oldCoords[0]] is None:
            print("You have not selectedPiece a piece")
            return False
        if self.board[oldCoords[1]][oldCoords[0]].getColor() != self.turn:
            print("You have selectedPiece the wrong color piece")
            return False
        if newCoords not in self.board[oldCoords[1]][oldCoords[0]].truncatedLineOfSights:
            print("Your piece cannot move there")
            return False
        if newCoords not in self.board[oldCoords[1]][oldCoords[0]].trueMoves:
            print("Your king is unprotected")
            return False
        #simulate the next move
        self.board = self.simulateBoard(self.board, oldCoords, newCoords, False)
        if self.turn == 'W': self.turn = 'B'
        else: self.turn = 'W'
        self.updateTrueMoves(self.board)
        if self.turn == 'W':
            if self.verifyBlackCheckmate(self.board):
                self.gameOver = True
                print("Checkmate, white wins!")
        else:
            if self.verifyWhiteCheckmate(self.board):
                self.gameOver = True
                print("Checkmate, black wins!")
        return True

    #returns True if legal, False if illegal
    def checkLegal(self, board, oldCoords, newCoords):
        tempBoard = copy.deepcopy(board)
        tempBoard = self.simulateBoard(tempBoard, oldCoords, newCoords, True)
        if self.turn == "W":
            if self.evalWhiteInCheck(tempBoard):
                return False
        else:
            if self.evalBlackInCheck(tempBoard):
                return False
        return True
    
    def simulateBoard(self, board, oldCoords, newCoords, quickSim):
        #handle en passant
        if board[oldCoords[1]][oldCoords[0]].getChr() == 'P':
            if oldCoords[0] != newCoords[0]:
                if board[newCoords[1]][newCoords[0]] is None:
                    board[oldCoords[1]][newCoords[0]] = None

        #handle castling
        if board[oldCoords[1]][oldCoords[0]].getChr() == 'K':
            if abs(oldCoords[0]-newCoords[0]) == 2:
                if newCoords[0] == 1:
                    board[oldCoords[1]][2] = board[oldCoords[1]][0]
                    board[oldCoords[1]][0] = None
                    board[oldCoords[1]][2].x = 2
                    board[oldCoords[1]][2].hasMoved = True
                    board[oldCoords[1]][2].updateFreeMoves()
                else:
                    board[oldCoords[1]][4] = board[oldCoords[1]][7]
                    board[oldCoords[1]][7] = None
                    board[oldCoords[1]][4].x = 4
                    board[oldCoords[1]][4].hasMoved = True
                    board[oldCoords[1]][4].updateFreeMoves()

        #handle normal moves
        board[newCoords[1]][newCoords[0]] = board[oldCoords[1]][oldCoords[0]]
        board[oldCoords[1]][oldCoords[0]] = None
        board[newCoords[1]][newCoords[0]].x = newCoords[0]
        board[newCoords[1]][newCoords[0]].y = newCoords[1]
        board[newCoords[1]][newCoords[0]].hasMoved = True
        board[newCoords[1]][newCoords[0]].updateFreeMoves()

        #enable promotion
        if board[newCoords[1]][newCoords[0]].getChr() == 'P':
            if newCoords[1] == 0 or newCoords[1] == 7:
                chosenPiece  = ""
                if quickSim:
                    chosenPiece = "Q"
                while chosenPiece not in ["Q","R","B","K"]:
                    chosenPiece  = input("Choose a piece: Q/R/B/K").upper()
                if chosenPiece == "Q":
                    board[newCoords[1]][newCoords[0]] = queen(newCoords[0], newCoords[1], board[newCoords[1]][newCoords[0]].getColor())
                    board[newCoords[1]][newCoords[0]].hasMoved = True
                if chosenPiece == "R":
                    board[newCoords[1]][newCoords[0]] = rook(newCoords[0], newCoords[1], board[newCoords[1]][newCoords[0]].getColor())
                    board[newCoords[1]][newCoords[0]].hasMoved = True
                if chosenPiece == "K":
                    board[newCoords[1]][newCoords[0]] = knight(newCoords[0], newCoords[1], board[newCoords[1]][newCoords[0]].getColor())
                    board[newCoords[1]][newCoords[0]].hasMoved = True
                if chosenPiece == "B":
                    board[newCoords[1]][newCoords[0]] = bishop(newCoords[0], newCoords[1], board[newCoords[1]][newCoords[0]].getColor())
                    board[newCoords[1]][newCoords[0]].hasMoved = True

        #enable en passant
        self.clearEnPassant(board)
        if board[newCoords[1]][newCoords[0]].getChr() == 'P':
            if abs(newCoords[1]-oldCoords[1]) == 2:
                board[newCoords[1]][newCoords[0]].enableEnPassant()
                
        self.truncateLineOfSights(board)
        return board
        
        
        

pygame.init()

# Colours
BACKGROUND = (100, 100, 100)
BLACK = (0,0,0)
WHITE = (0,0,0)
GREEN = (0,255,0)
 
# Game Setup
FPS = 60
fpsClock = pygame.time.Clock()
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600

BOARD_X = 0
BOARD_Y = 0
BOARD_WIDTH = 600
BOARD_HEIGHT = BOARD_WIDTH
SQUARE_WIDTH = BOARD_WIDTH / 8
SQUARE_HEIGHT = BOARD_HEIGHT / 8

Board_png = pygame.image.load('Images/Board.png')
Board_png = pygame.transform.scale(Board_png,(BOARD_WIDTH,BOARD_HEIGHT))

def loadPiece(path):
    image = pygame.image.load(path)
    return pygame.transform.scale(image, (SQUARE_WIDTH, SQUARE_HEIGHT))

whitePieces = {'P': loadPiece('Images/wp.png'),
          'R': loadPiece('Images/wr.png'),
          'N': loadPiece('Images/wn.png'),
          'B': loadPiece('Images/wb.png'),
          'Q': loadPiece('Images/wq.png'),
          'K': loadPiece('Images/wk.png')}

blackPieces = {'P': loadPiece('Images/bp.png'),
          'R': loadPiece('Images/br.png'),
          'N': loadPiece('Images/bn.png'),
          'B': loadPiece('Images/bb.png'),
          'Q': loadPiece('Images/bq.png'),
          'K': loadPiece('Images/bk.png')}

# End of Game Setup

WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Chess ')

# The main function that controls the game
def main () :
  looping = True

  myBoard = gameBoard()
  # square that a player selects
  selectedPiece = None
  
  # The main game loop
  while looping :
    # Get inputs
    for event in pygame.event.get() :
      if event.type == QUIT :
        pygame.quit()
        sys.exit()
      if not myBoard.gameOver:
          # Game only updates on MOUSEBUTTONDOWN
          if event.type == MOUSEBUTTONDOWN:
              if event.button == 1:
                  # Verify square location
                  mouse_X, mouse_Y = pygame.mouse.get_pos()
                  square_X = int((mouse_X - BOARD_X) // SQUARE_WIDTH)
                  square_Y = int((mouse_Y - BOARD_Y) // SQUARE_HEIGHT)

                  # Verify valid co-ordinates
                  if square_X >= 0 and square_X <= 7 and square_Y >= 0 and square_Y <= 7:
                      if selectedPiece == None:
                          # Start Square
                          selectedPiece = myBoard.board[square_Y][square_X]
                          selected_X, selected_Y  = square_X, square_Y
                      else:
                          # End square
                          request = myBoard.requestMove([selected_X, selected_Y], [square_X, square_Y])
                          if request is False:
                              selectedPiece = None
                          else:
                              selectedPiece = None
 
    # Render elements of the game
    WINDOW.fill(BACKGROUND)

    #Render the board
    WINDOW.blit(Board_png, (BOARD_X, BOARD_Y))
    #Render the pieces
    for i in range(8):
        for j in range(8):
            if myBoard.board[j][i] is not None:
                if myBoard.board[j][i].getColor() == 'W':
                    WINDOW.blit( whitePieces[myBoard.board[j][i].getChr()] , (BOARD_X + (SQUARE_WIDTH*i), BOARD_Y + (SQUARE_HEIGHT*j)) )
                else:
                    WINDOW.blit( blackPieces[myBoard.board[j][i].getChr()] , (BOARD_X + (SQUARE_WIDTH*i), BOARD_Y + (SQUARE_HEIGHT*j)) )
    #highlight in a green square the selectedPiece
    if selectedPiece is not None:
        rect = pygame.Rect(BOARD_X + (selected_X * SQUARE_WIDTH), BOARD_Y + (selected_Y * SQUARE_HEIGHT), SQUARE_WIDTH, SQUARE_HEIGHT)
        pygame.draw.rect(WINDOW, GREEN, rect, 2)

    pygame.display.update()
    fpsClock.tick(FPS)
 
main()
































    
