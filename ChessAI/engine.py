"""
Responsible for storing information about current state of game
Determine valid moves at current state and will also keep a move log
"""
class GameState():
    def __init__(self):
        # board is 8x8 2d list, each element has two characters
        # first char = color ('b' or 'w')
        # second char = type of piece (K, Q, B, N, R, P)
        # '--' = empty space
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        '''
        self.board = [
            ["--", "--", "--", "--", "--", "bK", "--", "--"],
            ["--", "--", "--", "--", "--", "bP", "bP", "--"],
            ["--", "wR", "--", "wP", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "bP", "--"],
            ["--", "--", "--", "--", "--", "--", "wP", "--"],
            ["bR", "bP", "--", "--", "--", "--", "--", "wK"],
            ["--", "--", "--", "--", "--", "--", "wP", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"]
        ]
        '''
        self.whiteToMove = True
        self.moveLog = []
        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves, 'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checked = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.opponentPawnAttacks = []
        self.enpassantPossible = ()
        self.enpassantPossibleLog = [self.enpassantPossible]
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]
    
    '''
    Takes a move as a paramter and executes it (won't work for castling, pawn promotion, and en-passant)
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol]  = '--'
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        #update king location
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
        #enpassant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'
        #update isEnpassantMove variable
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()
        self.enpassantPossibleLog.append(self.enpassantPossible)
        #castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: #kingside castle
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1] = '--'
            else: #queenside castle
                self.board[move.endRow][move.endCol+1] =self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = '--'
        #update castling rights
        self.updateCastleRights(move)
        self.opponentPawnAttacks = self.getOpponentPawnAttacks()
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    '''
    Undo the last move made
    '''
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            #update king location
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            #undo en passant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured
            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]
            #undo castle rights
            self.castleRightsLog.pop()
            self.currentCastlingRight = self.castleRightsLog[-1]
            #undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: #kingside
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else: #queenside
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = '--'
            self.checkmate = False
            self.stalemate = False

    def getOpponentPawnAttacks (self):
        self.whiteToMove = not self.whiteToMove
        opponentPawnAttacks = []
        for r in range(1, 7):
            for c in range(8):
                turn = self.board[r][c]
                if (turn == 'wP' and self.whiteToMove) or (turn == 'bP' and not self.whiteToMove):
                    self.getOpponentPawnMoves(r, c, opponentPawnAttacks)
        self.whiteToMove = not self.whiteToMove
        return opponentPawnAttacks

    def setMoveScore (self, move):
        if ((move.endRow, move.endCol) in self.opponentPawnAttacks) and move.pieceMoved[1] != 'P':
            move.setMoveScore(move.moveScore - move.pieceScore[move.pieceMoved[1]])

    def getOpponentPawnMoves(self, r, c, opponentPawnAttacks):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        moveAmount = -1 if self.whiteToMove else 1

        if c-1 >= 0:
            if not piecePinned or pinDirection == (moveAmount, -1):
                opponentPawnAttacks.append((r+moveAmount, c-1))
        if c+1 <= 7:
            if not piecePinned or pinDirection == (moveAmount, 1):
                opponentPawnAttacks.append((r+moveAmount, c+1))

    '''
    Update the castle rights given the move
    '''
    def updateCastleRights(self, move):
        if move.pieceCaptured == 'wR':
            if move.endCol == 0:  
                self.currentCastlingRight.wqs = False
            elif move.endCol == 7:  
                self.currentCastlingRight.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endCol == 0: 
                self.currentCastlingRight.bqs = False
            elif move.endCol == 7:  
                self.currentCastlingRight.bks = False
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False
    
    '''
    All moves considering checks
    '''
    def getValidMoves(self, captures = False):
        captureMoves = []
        moves = []
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        self.checked, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.checked:
            if len(self.checks) == 1:  # only 1 check, block the check or move the king
                moves = self.getAllPossibleMoves()
                # to block the check you must put a piece into one of the squares between the enemy piece and your king
                check = self.checks[0]  # check information
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []  # squares that pieces can move to
                # if knight, must capture the knight or move your king, other pieces can be blocked
                if pieceChecking[1] == "N":
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)  # check[2] and check[3] are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:  # once you get to piece and check
                            break
                # get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1):  # iterate through the list backwards when removing elements
                    if moves[i].pieceMoved[1] != "K":  # move doesn't move king so it must block or capture
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:  # move doesn't block or capture piece
                            moves.remove(moves[i])
                        else:
                            self.setMoveScore(moves[i])
            else:  # double check, king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else:  # not in check - all moves are fine
            moves = self.getAllPossibleMoves()
            for move in moves:
                self.setMoveScore(move)
        self.getCastleMoves(kingRow, kingCol, moves)
        if len(moves) == 0:
            if self.checked:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        if self.inStalemate():
            self.stalemate = True
        self.currentCastlingRight = tempCastleRights
        for move in moves:
            if move.isCapture:
                captureMoves.append(move)
        if captures:
            captureMoves.sort(key=Move.getMoveScore, reverse=True)
            return captureMoves
        else:
            moves.sort(key=Move.getMoveScore, reverse=True)
            return moves
        
    '''
    Checks if only kings are left on the board or 3 move repetition
    '''
    def inStalemate(self):
        if len(self.moveLog) >= 10:
            if ((self.moveLog[-1].moveID, self.moveLog[-2].moveID) == (self.moveLog[-5].moveID, self.moveLog[-6].moveID) 
            and (self.moveLog[-1].moveID, self.moveLog[-2].moveID) == (self.moveLog[-9].moveID, self.moveLog[-10].moveID)):
                return True
        for row in range(8):
            for col in range(8):
                if self.board[row][col] != '--' and self.board[row][col][1] != 'K':
                    return False
        return True 

    '''
    Determines if enemy can attack the square r, c
    '''
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    '''
    All moves without considering checks
    '''
    def getAllPossibleMoves(self):
        moves = []
        for r in range(8):
            for c in range(8):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves
    
    def checkForPinsAndChecks(self):
        pins = []  # squares pinned and the direction its pinned from
        checks = []  # squares where enemy is applying a check
        checked = False
        if self.whiteToMove:
            enemyColor = 'b'
            allyColor = 'w'
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = 'w'
            allyColor = 'b'
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        # check outwards from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            direction = directions[j]
            possiblePin = ()  # reset possible pins
            for i in range(1, 8):
                endRow = startRow + direction[0] * i
                endCol = startCol + direction[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():  # first allied piece could be pinned
                            possiblePin = (endRow, endCol, direction[0], direction[1])
                        else:  # 2nd allied piece - no check or pin from this direction
                            break
                    elif endPiece[0] == enemyColor:
                        enemyType = endPiece[1]
                        if (0 <= j <= 3 and enemyType == 'R') or (4 <= j <= 7 and enemyType == 'B') or (
                                i == 1 and enemyType == 'P' and (
                                (enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or (
                                enemyType == 'Q') or (i == 1 and enemyType == 'K'):
                            if possiblePin == ():  # no piece blocking, so check
                                checked = True
                                checks.append((endRow, endCol, direction[0], direction[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else:  # enemy piece not applying checks
                            break
                else:
                    break  # off board
        # check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        for move in knightMoves:
            endRow = startRow + move[0]
            endCol = startCol + move[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':  # enemy knight attacking a king
                    checked = True
                    checks.append((endRow, endCol, move[0], move[1]))
        return checked, pins, checks

    def isCheckMove (self, move):
        self.makeMove(move)
        checked, pins, checks = self.checkForPinsAndChecks()
        self.undoMove()
        if checked:
            return True
    '''
    Get all the pawn moves for pawn located at (r, c)
    '''
    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            enemyColor = "b"
            kingRow, kingCol = self.whiteKingLocation
        else:
            moveAmount = 1
            startRow = 1
            enemyColor = "w"
            kingRow, kingCol = self.blackKingLocation

        if self.board[r+moveAmount][c] == '--':
            if not piecePinned or pinDirection == (moveAmount, 0):
                moves.append(Move((r, c), (r+moveAmount, c), self.board))
                if r == startRow and self.board[r+2*moveAmount][c] == '--': 
                    moves.append(Move((r, c), (r+2*moveAmount, c), self.board))
        if c-1 >= 0:
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[r+moveAmount][c-1][0] == enemyColor:
                    moves.append(Move((r, c), (r+moveAmount, c-1), self.board))
                if (r+moveAmount, c-1) == self.enpassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol < c:
                            #inside between king and pawn; outside range between border
                            insideRange = range(kingCol + 1, c-1)
                            outsideRange = range(c+1, 8)
                        else:
                            insideRange = range(kingCol - 1, c, -1)
                            outsideRange = range(c-2, -1, -1)
                        for i in insideRange:
                            if self.board[r][i] != '--':
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if square[0] == enemyColor and (square[1] == 'R' or square[1] == 'Q'):
                                attackingPiece = True
                            elif square != '--':
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r, c), (r+moveAmount, c-1), self.board, isEnpassantMove = True))
        if c+1 <= 7:
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[r+moveAmount][c+1][0] == enemyColor:
                    moves.append(Move((r, c), (r+moveAmount, c+1), self.board))
                if (r+moveAmount, c+1) == self.enpassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol < c:
                            #inside between king and pawn; outside range between border
                            insideRange = range(kingCol + 1, c)
                            outsideRange = range(c+2, 8)
                        else:
                            insideRange = range(kingCol - 1, c+1, -1)
                            outsideRange = range(c-1, -1, -1)
                        for i in insideRange:
                            if self.board[r][i] != '--':
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if square[0] == enemyColor and (square[1] == 'R' or square[1] == 'Q'):
                                attackingPiece = True
                            elif square != '--':
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r, c), (r+moveAmount, c+1), self.board, isEnpassantMove = True))

    '''
    Get all the rook moves for the rook located at (r, c)
    '''
    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    '''
    Get all the knight moves for the knight located at (r, c)
    '''
    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((r, c), (endRow, endCol), (self.board)))

    '''
    Get all the bishop moves for the bishop located at (r, c)
    '''
    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    '''
    Get all the queen moves for the queen located at (r, c)
    '''
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    '''
    Get all the king moves for the king located at (r, c)
    '''
    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    if allyColor == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)
    
    '''
    Generate all valid castle moves for the king at r, c and add to list of moves
    '''
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))
        
class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    ranksToRows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove = False, isCastleMove = False):
        self.pieceScore = {'K': 0, 'Q': 9, 'R': 5, 'B': 3.3, 'N': 3.2, 'P': 1}
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 7)
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wP" if self.pieceMoved == "bP" else "bP"
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        self.isCastleMove = isCastleMove
        self.isCapture = self.pieceCaptured != '--' and self.pieceMoved != '--'
        self.score = 0
        self.moveScore = 0
        if self.pieceMoved[1] != 'P':
            self.moveScore += 5
        if self.isCastleMove:
            self.moveScore += 5
            self.score += 4
        if self.isCapture:
            self.moveScore += (self.pieceScore[self.pieceCaptured[1]] - self.pieceScore[self.pieceMoved[1]] + 10)
            self.score += .5
        if self.isPawnPromotion:
            self.moveScore += 9

    '''
    Overriding the equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    def setMoveScore(self, moveScore):
        self.moveScore = moveScore

    def setScore (self, score):
        self.score = score
    
    def getMoveScore (self):
        return self.moveScore

    def __str__(self):
        if self.isCastleMove:
            return 'O-O' if self.endCol == 6 else 'O-O-O'
        endSquare = self.getRankFile(self.endRow, self.endCol)
        #pawn moves
        if self.pieceMoved[1] == 'P':
            if self.isCapture:
                return self.colsToFiles[self.startCol] + 'x' + endSquare
            else:
                return endSquare
        #piece moves
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += 'x'
        return moveString + endSquare
