'''
Determines best move and handles AI moves
'''
import random

DEPTH = 4
pieceScore = {'K': 0, 'Q': 9, 'R': 5, 'B': 3.3, 'N': 3.2, 'P': 1}
knightScores = [[-50,-40,-30,-30,-30,-30,-40,-50],
                [-40,-20,  0,  0,  0,  0,-20,-40],
                [-30,  0, 10, 15, 15, 10,  0,-30],
                [-30,  5, 15, 25, 25, 15,  5,-30],
                [-30,  0, 15, 25, 25, 15,  0,-30],
                [-30,  5, 5, 15, 15, 5,  5,-30],
                [-40,-20,  0,  5,  5,  0,-20,-40],
                [-50,-40,-30,-30,-30,-30,-40,-50]]

bishopScores = [[-20,-10,-10,-10,-10,-10,-10,-20],
                [-10,  0,  0,  0,  0,  0,  0,-10],
                [-10,  0,  5, 10, 10,  5,  0,-10],
                [-10,  5,  5, 10, 10,  5,  5,-10],
                [-10,  0, 15, 10, 10, 15,  0,-10],
                [-10, 10, 10, 5, 5, 10, 10,-10],
                [-10,  5,  0,  0,  0,  0,  5,-10],
                [-20,-10,-30,-10,-10,-30,-10,-20]]

rookScores = [  [0,  0,  0,  0,  0,  0,  0,  0],
                [5, 10, 10, 10, 10, 10, 10,  5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  5,  5,  5,  0, -5]]

queenScores = [ [-20,-10,-10, -5, -5,-10,-10,-20],
                [-10,  0,  0,  0,  0,  0,  0,-10],
                [-10,  0,  5,  5,  5,  5,  0,-10],
                [-5,  0,  5,  5,  5,  5,  0, -5],
                [0,  0,  5,  5,  5,  5,  0, -5],
                [-10,  5,  5,  5,  5,  5,  0,-10],
                [-10,  0,  5,  0,  0,  0,  0,-10],
                [-20,-10,-10, -5, -5,-10,-10,-20]]

pawnScores = [  [0, 0, 0, 0, 0, 0, 0, 0],
                [50, 50, 50, 50, 50, 50, 50, 50],
                [10, 10, 20, 35, 35, 20, 10, 10],
                [5,  5, 10, 35, 35, 10,  5,  5],
                [0,  -5,  0, 20, 20, 5,  -5,  0],
                [5, -5,-5,  0,  0,-10, -5,  5],
                [5, 10, 0,-25,-25, 0, 10,  5],
                [0,  0,  0,  0,  0,  0,  0,  0]]

piecePositionScores = {"wN": knightScores,
                         "bN": knightScores[::-1],
                         "wB": bishopScores,
                         "bB": bishopScores[::-1],
                         "wQ": queenScores,
                         "bQ": queenScores[::-1],
                         "wR": rookScores,
                         "bR": rookScores[::-1],
                         "wP": pawnScores,
                         "bP": pawnScores[::-1]}
CHECKMATE = 1000
STALEMATE = 0

def findRandomMove(validMoves):
    return random.choice(validMoves)
'''
Helper method to make first recursive call
'''
def findBestMove (gs, validMoves, returnQueue):
    global nextMove, counter
    nextMove = None
    counter = 0
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    print(counter)
    returnQueue.put(nextMove)

def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove, counter
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE
        else: 
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE
    counter += 1
    if depth == 0:
        return searchAllCaptures(gs, alpha, beta, turnMultiplier)        
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
                print(move, score)
        gs.undoMove()
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore


def searchAllCaptures (gs, alpha, beta, turnMultiplier):
    global nextMove
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE
        else: 
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE
    if nextMove is None:
        score = turnMultiplier * scoreBoard(gs, 0)
    else:
        score = turnMultiplier * scoreBoard(gs, nextMove.moveScore)
    if score >= beta:
        return beta
    alpha = max(alpha, score)
    captureMoves = gs.getValidMoves(captures = True)
    for move in captureMoves:
        gs.makeMove(move)
        score = -searchAllCaptures(gs, -beta, -alpha, -turnMultiplier)
        gs.undoMove()
        if score >= beta:
            return beta
        alpha = max(alpha, score)
    return alpha


'''
A positive score is good for white, a negative score is good for black
'''
def scoreBoard(gs, moveScore):
    material = 0
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE
        else: 
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]

            if square != '--':
                piecePositionScore = 0
                if square[1] != "K":
                #score it positionally
                    piecePositionScore = piecePositionScores[square][row][col]
                if square[0] == 'w':
                    score += pieceScore[square[1]] + .01*piecePositionScore
                if square[0] == 'b':
                    score -= pieceScore[square[1]] + .01*piecePositionScore
                material += pieceScore[square[1]]
            if row >= 1 and row <= 6:
                if square == 'wP' and gs.board[row-1][col] == 'wP':
                    score -= .2
                elif square == 'bP' and gs.board[row+1][col] == 'bP':
                    score += .2 
    endGameWeight = 0.1 * (80 - material)
    if gs.whiteToMove:
        score += 0.01*(endGameWeight*endGameScore(gs))
        score += (.01*moveScore)
    else:
        score -= 0.01*(endGameWeight*endGameScore(gs))
        score -= (.01*moveScore)
    return score

'''
Encourages bot to force king into corner and push it's own king closer to opponents
''' 
def endGameScore (gs):
    score = 0
    if gs.whiteToMove:
        opponentKingRow = gs.blackKingLocation[0]
        opponentKingCol = gs.blackKingLocation[1]
        allyKingRow = gs.whiteKingLocation[0]
        allyKingCol = gs.whiteKingLocation[1]
    else:
        opponentKingRow = gs.whiteKingLocation[0]
        opponentKingCol = gs.whiteKingLocation[1]
        allyKingRow = gs.blackKingLocation[0]
        allyKingCol = gs.blackKingLocation[1]
    opponentKingDstToCenterCol = max(3-opponentKingCol, opponentKingCol-4)
    opponentKingDstToCenterRow = max(3-opponentKingRow, opponentKingRow-4)
    opponentKingDstFromCenter = opponentKingDstToCenterCol + opponentKingDstToCenterRow
    score += (2 * opponentKingDstFromCenter)
    dstBtwnKingsCol = abs(allyKingCol - opponentKingCol)
    dstBtwnKingsRow = abs(allyKingRow - opponentKingRow)
    dstBtwnKings = dstBtwnKingsCol + dstBtwnKingsRow
    score -= (dstBtwnKings)
    return score
