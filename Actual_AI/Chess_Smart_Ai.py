import random

peice_Score = {'K' : 0, 'Q': 9, 'R': 5, 'B': 3, 'N': 3, 'p': 1} #score for peice
CHECKMATE = 100 #score for checkmate

STALEMATE = 1 #score when satelmate

#we will make it so that black is trying to make board score
#(yes, the whole board has single score. )
#as negative as possible and white is tryin to make board score as positive as possibel

def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) -1)]

def find_best_moves(gs, validmoves):
    maxscore = 0
    turnmultiplier = 1 if gs.white_to_move else -1

    if gs.checkmate:
        score = CHECKMATE

    elif gs.stalemate:
        score = 0
    bestmove = None
    for playermove in validmoves:
        gs.make_Move(playermove)
        oppmoves = gs.get_Valid_moves()
        oppMaxScore = -CHECKMATE
        for oppmove in oppmoves:
            gs.make_Move(oppmove)
            if gs.checkmate:
                score = -CHECKMATE
            elif gs.stalemate:
                score = STALEMATE
            else:
                score = -Board_score(gs.board) * turnmultiplier

            if( score <= maxscore):
                maxscore = score
                bestmove = playermove
            gs.undo_Move()
        gs.undo_Move()



    return bestmove





def Board_score( board):
    score = 0
    for r in board:
        for c in r:
            if(c != '--'):
                if(c[0] == 'w'):
                    score += peice_Score[c[1]]
                elif(c[0] == 'b'):
                    score -= peice_Score[c[1]]

    return score



            