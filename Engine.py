from move import *
from castle_right import *


class GameState:
    def __init__(self):
        self.board = [
            ['bR','bN','bB','bQ','bK','bB','bN','bR'],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ['--','--','--','--','--','--','--','--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
        ]
        self.white_to_move = True
        self.moveLog= []
        self.move_Functions = {'p': self.getPawnMoves, "R": self.getRookMoves, "N": self.getKnightMoves, "B": self.getBishopMoves, "Q": self.getQueenMoves, "K": self.getKingMoves}

        self.white_king_loc = (7,4) #initial white king loc
        self.black_king_loc = (0,4)

        self.incheck = False
        self.checkmate = False

        self.stalemate = False

        self.pins = []
        self.checks = []

        self.enPassantPossible = ()# co-ordinates of square where enpassant capture is possible.

        self.current_castleing_rights = Castle_rights(True,True,True,True)
        self.castle_rights_log = [Castle_rights(self.current_castleing_rights.white_king_side,
                                                self.current_castleing_rights.white_queen_side,
                                                self.current_castleing_rights.black_king_side,
                                                self.current_castleing_rights.black_queen_side)]


    def set_stalemate_checkmate(self):
        valid_moves = self.get_Valid_moves()
        self.white_to_move= not self.white_to_move
        opp_moves = self.get_Valid_moves()
        if(len(opp_moves) == 0 and len(valid_moves) == 0):
            self.stalemate = True
        elif(len(opp_moves) != 0 and len(valid_moves) == 0):
            self.checkmate = True
        self.white_to_move = not self.white_to_move


    """
    Takes move as parameter and executes(not for catsleiing, enpassent, pawn promotion)
    """
    def make_Move(self, move):
        self.board[move.startrow][move.startcol] = "--" #cuz now no peice in starting location.
        self.board[move.endrow][move.endcol] = move.peice_moved
        self.moveLog.append(move) #log the move if you want to undo it later, of keep track of moves

        #move will be obj of class move
        self.white_to_move = not self.white_to_move  # switching player from whatever it was

        #update kings loc
        if move.peice_moved =="wK":
            self.white_king_loc = (move.endrow,move.endcol)
        elif move.peice_moved == "bK":
            self.black_king_loc = (move.endrow,move.endcol)



        if move.isPawnPromotion:
            self.board[move.endrow][move.endcol] = move.peice_moved[0] + "Q" #so new peice , if pawn being promoted, becomes, queen. color of peice + Q.

        #enpassant move
        if move.isEnpassantMove:
            move.peice_captured = self.board[move.startrow][move.endcol]
            self.board[move.startrow][move.endcol] = '--'#capturing the pawn which is to our side and to ourbehind, before and after enpassanting


        #updaste enpassantpossiblemove variable
        if move.peice_moved[1] == 'p' and abs(move.startrow - move.endrow) == 2:
            self.enPassantPossible = ((move.startrow + move.endrow)//2, move.startcol)
        else:
            self.enPassantPossible = ()


        if move.iscastleMove:
            if move.endcol - move.startcol == 2: #kingside castle
                self.board[move.endrow][move.endcol-1] = self.board[move.endrow][move.endcol+1] #switch rook from corner to one on other side of king
                self.board[move.endrow][move.endcol + 1] = '--' #tremove rook from that pos
            else: #queen side casteling
                self.board[move.endrow][move.endcol + 1] = self.board[move.endrow][move.endcol -2]
                self.board[move.endrow][move.endcol - 2] = '--'

        # update the castleing rights
        self.update_castle_rights(move)
        self.castle_rights_log.append(Castle_rights(self.current_castleing_rights.white_king_side,self.current_castleing_rights.white_queen_side, self.current_castleing_rights.black_king_side, self.current_castleing_rights.black_queen_side))

        self.last_move_played = move


    def undo_Move(self):
        if len(self.moveLog)!= 0: #make sure atleast 1move is done
            move = self.moveLog.pop() #store removed, last stored move in variable move.
            self.board[move.startrow][move.startcol] = move.peice_moved #put the moved peice back to original pos.
            self.board[move.endrow][move.endcol] = move.peice_captured  # put captured peice back to original place.

            #update kings loc. even if king not moved by undo, its loc before and after undo is move.start...
            if move.peice_moved == "wK":
                self.white_king_loc = (move.startrow, move.startcol)
            elif move.peice_moved == "bK":
                self.black_king_loc = (move.startrow, move.startcol)

            self.white_to_move = not self.white_to_move #Switch the turns back


            #undo enpassant capture
            if move.isEnpassantMove:
                self.board[move.endrow][move.endcol] = '--' #make landing square blank
                self.board[move.startrow][move.endcol] = move.peice_captured
                self.enPassantPossible = (move.endrow, move.endcol)

            #undo two square moving of opposite pawn
            if move.peice_moved[1] == 'p' and (abs(move.startrow - move.endrow) == 2):
                self.enPassantPossible = () # cuz undoing of the move itself is

            # update castelling rights
            self.castle_rights_log.pop()
            castlerights = self.castle_rights_log[-1]
            self.current_castleing_rights = castlerights

            # undo castle move
            if move.iscastleMove:
                if move.endcol - move.startcol == 2: #king side
                    self.board[move.endrow][move.endcol+1] = self.board[move.endrow][move.endcol-1]
                    self.board[move.endrow][move.endcol - 1] = '--'
                else: #queen side
                    if self.white_to_move:
                        self.board[7][0] = 'wR'
                        self.board[7][3] = '--'
                    else:
                        self.board[0][0] = 'bR'
                        self.board[0][3] = '--'

        if(self.checkmate == True):
            self.checkmate = False
        if(self.stalemate == True):
            self.stalemate = False





    def update_castle_rights(self, move):
        if move.peice_moved == 'wK':
            self.current_castleing_rights.white_king_side = False
            self.current_castleing_rights.white_queen_side = False
        elif move.peice_moved == 'bK':
            self.current_castleing_rights.black_king_side = False
            self.current_castleing_rights.black_queen_side = False
        elif move.peice_moved == 'wR':
            if move.startrow == 7:
                if move.startcol == 0: #left white rook
                    self.current_castleing_rights.white_queen_side = False
                elif move.startcol == 7: #right white rook
                    self.current_castleing_rights.white_king_side = False
        elif move.peice_moved == 'bR':
            if move.startrow == 0:
                if move.startcol == 0:
                    self.current_castleing_rights.black_queen_side = False
                elif move.startcol == 7:
                    self.current_castleing_rights.black_king_side = False





    """
    ALL possible valid moves considering checks, discovered checks, etc.
    """
    def get_Valid_moves(self):

        temporaray_enpassant_possible = self.enPassantPossible

        # generate all possible moves
        moves = []

        self.incheck, self.pins, self.checks = self.check_for_pins_and_checks()

        if self.white_to_move:
            kingrow = self.white_king_loc[0]
            kingcol = self.white_king_loc[1]
        else:
            kingrow = self.black_king_loc[0]
            kingcol = self.black_king_loc[1]

        if self.incheck:
            if len(self.checks) == 1: #only 1 check. then block check or mobve king.
                moves = self.All_possible_moves()
                check = self.checks[0] #check info.
                check_row = check[0]
                check_col = check[1]
                peice_checking = self.board[check_row][check_col]

                valid_squares = [] #stores valid squares where peices other than king can move to to stop the check.
                #if knioght, kill knight or move king.

                if peice_checking[1] == "N":
                    valid_squares = [(check_row, check_col)]

                else:
                    for i in range(1,8):
                        valid_square = (kingrow + check[2]*i, kingcol + check[3]*i) # check[2] and check[3] are directions in which enemy peice attacks
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break

                for i in range(len(moves)-1, -1, -1): # traverse the array backwards.
                    if moves[i].peice_moved[1] != 'K': #this perticular move in all possible moves at this isntance, doesnt move the king. it isnt a king move. so we have to move another peice in the path of check or kill the knight if it was a knight check.
                        if not(moves[i].endrow , moves[i].endcol) in valid_squares: #so if this move doesnt black the check then ==>
                            moves.remove(moves[i])



            else: #double check or triple check, cuz more than 1 checks. in this case, must move the king.
                self.getKingMoves(kingrow, kingcol, moves)



        else: #not in check, so all moves are fine.
            temporaryCastleRights = Castle_rights(self.current_castleing_rights.white_king_side,
                                                  self.current_castleing_rights.white_queen_side,
                                                  self.current_castleing_rights.black_king_side,
                                                  self.current_castleing_rights.black_queen_side)
            moves = self.All_possible_moves()

            if self.white_to_move:
                self.getCastleMoves(self.white_king_loc[0], self.white_king_loc[1], moves,'w')

            else:
                self.getCastleMoves(self.black_king_loc[0], self.black_king_loc[1], moves, 'b')

            self.current_castleing_rights = temporaryCastleRights


        self.enPassantPossible = temporaray_enpassant_possible # moves stores all possible moves for that turn
        # when computting that, we actually play that move temporarily. so the value of self.enPassantPossible may change.
        # so we need to set it temporarily to some variable so that we can retrive it later.

        peices = []
        for r in self.board:
            for c in r:
                if(c != '--'):
                    peices.append('a')

        if(len(peices) == 2):
            moves = []




        return moves



    def inCheck(self): #to see if you are in check
        if self.white_to_move: #white king to move/white peice to move
            return self.square_under_attack(self.white_king_loc[0],self.white_king_loc[1])
        else:
            return self.square_under_attack(self.black_king_loc[0],self.black_king_loc[1])


    def square_under_attack(self,r,c):
        #check if square r,c is under attack
        self.white_to_move = not self.white_to_move #change move to see opponents moves.
        oppMoves = self.All_possible_moves() #store all possible moves of opponent here.
        self.white_to_move = not self.white_to_move  # switch turn back
        for move in oppMoves:
            if move.endrow == r and move.endcol == c:
                return True #cuz square is under attack.
        return False #else return false.

    """
    All moves without considering checks. cuz if check on that square or discovered check due to that move, 
    that move shouldnt be allowed. but in All_possible_moves, we are allowing such moves.
    """
    def All_possible_moves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0] # cuz string of length 2. so [0] and [1]. so turn will be char of '-' or 'w' or 'b'. so that will tell if peice there or not and if there, of what color. black or white.
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move): #check if white peice and white to move or black peice and black to move.
                    peice = self.board[row][col][1]
                    self.move_Functions[peice](row,col,moves)
        return moves


    def getPawnMoves(self,r,c,moves):
        peice_pinned = False
        pin_direction = ()

        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c :
                peice_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i]) # since we have already accounted for this pin, remove it.
                break



        if self.white_to_move:
            if self.board[r-1][c] == "--": #if white to move and square in front of it is empty
                if not peice_pinned or pin_direction == (-1,0):
                    moves.append(Move((r, c), (r - 1, c), self.board))
                    if r == 6 and self.board[r - 2][c] == "--":  # white can move twice only if on 6th row from top. and if thyat squar is empty
                        moves.append(Move((r, c), (r - 2, c), self.board))


            #captures
            if c-1 >=0: #not letting it get out of board moving to left of board, capture to left
                if self.board[r-1][c-1][0] == "b": #if peice from 1 accross diagonal is enemy peice, in this case, black peice.
                    if not peice_pinned or pin_direction == (-1, -1):
                        moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r-1,c-1) == self.enPassantPossible:
                    if not peice_pinned or pin_direction == (-1,-1):
                        moves.append(Move((r,c), (r-1, c-1), self.board, isEnpassantMove = True))


            if c+1 <= 7: #if move letting it get out of board. moving to right of board, capture to right
                if self.board[r-1][c+1][0] == 'b':
                    if not peice_pinned or pin_direction == (-1, 1):
                        moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r-1,c+1) == self.enPassantPossible:
                    if not peice_pinned or pin_direction == (-1,1):
                        moves.append(Move((r,c), (r-1, c+1), self.board, isEnpassantMove = True))




        if not self.white_to_move:
            if self.board[r + 1][c] == "--":  # if black to move and square in front of it is empty
                if not peice_pinned or pin_direction == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r + 2][c] == "--":  # black can move twice only if on 1st row from top. and if thyat squar is empty
                        moves.append(Move((r, c), (r + 2, c), self.board))



            #captures
            if c - 1 >= 0:  # not letting it get out of board moving to left of board
                if self.board[r + 1][c - 1][0] == "w": # if peice from 1 accross diagonal is enemy peice, in this case, white peice.
                    if not peice_pinned or pin_direction == (1, -1):
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r+1,c-1) == self.enPassantPossible:
                    if not peice_pinned or pin_direction == (1,-1):
                        moves.append(Move((r,c), (r+1, c-1), self.board, isEnpassantMove = True))


            if c + 1 <= 7:  # if move letting it get out of board. moving to right of board
                if self.board[r + 1][c + 1][0] == 'w':
                    if not peice_pinned or pin_direction == (1, 1):
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r+1,c+1) == self.enPassantPossible:
                    if not peice_pinned or pin_direction == (1,1):
                        moves.append(Move((r,c), (r+1, c+1), self.board, isEnpassantMove = True))

    def getRookMoves(self,r,c,moves):
        peice_pinned = False
        pin_direction = ()

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                peice_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q': #cant remove queen from pins on rook moves, only on bishop moves
                    self.pins.remove(self.pins[i])  # since we have already accounted for this pin, remove it.
                break

        direction = ((-1,0),(0,-1),(1,0),(0,1))
        enemy_color = "b" if self.white_to_move else "w"
        for d in direction:
            for i in range(1,8):
                endrow = r+d[0]*i
                endcol = c+d[1]*i
                if 0 <= endrow <8 and 0<= endcol < 8:
                    if not peice_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        endpeice = self.board[endrow][endcol]  # the peice to which we can move to
                        if endpeice == "--":  # is empty
                            moves.append(Move((r, c), (endrow, endcol), self.board))
                        elif endpeice[0] == enemy_color:  # is enemy peice
                            moves.append(Move((r, c), (endrow, endcol), self.board))
                            break  # break loop in that case
                        else:
                            break  # cuz invalid
                else:
                    break

    def getKingMoves(self,r,c,moves):

        rowMoves = (-1,-1,-1,0,0,1,1,1)
        colMoves = (-1,0,1,-1,1,-1,0,1)
        allycolor = 'w' if self.white_to_move else 'b'

        for i in range(8):
            endrow = r + rowMoves[i]
            endcol = c + colMoves[i]
            if 0 <= endrow < 8 and 0 <= endcol < 8:
                endpeice = self.board[endrow][endcol]  # the peice to which we can move to so it can be 'b'/ 'w'/ '-'

                if endpeice[0] != allycolor:
                    print(allycolor)
                    #place king on end square to see if he is in check aty that location

                    if allycolor == 'w':
                        self.white_king_loc = (endrow, endcol)
                    else:
                        self.black_king_loc = (endrow, endcol)

                    inChecks, pins, checks = self.check_for_pins_and_checks() # this gives us if in check at endro, endcol; list of pins at endrow, endcol; and checks at endrow, endcol

                    if not inChecks:
                        moves.append(Move((r,c),(endrow,endcol), self.board)) #since not in check, moving king to that perticular endrow, endcol is a valid move

                    #place king on original location since we moved him to endrow, endcol to check if he has checks or such there
                    if allycolor == 'w':
                        self.white_king_loc = (r,c)
                    else:
                        self.black_king_loc = (r,c)




    def getQueenMoves(self,r,c,moves):
        self.getRookMoves(r,c,moves)
        self.getBishopMoves(r,c,moves)

    def getKnightMoves(self,r,c,moves):

        peice_pinned = False

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                peice_pinned = True
                self.pins.remove(self.pins[i])  # since we have already accounted for this pin, remove it.
                break


        direction = ((2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2))
        enemy_color = "b" if self.white_to_move else "w"
        for d in direction:
            endrow = r + d[0]
            endcol = c + d[1]
            if 0 <= endrow < 8 and 0 <= endcol < 8:
                if not peice_pinned:
                    endpeice = self.board[endrow][endcol]  # the peice to which we can move to
                    if endpeice == "--":  # is empty
                        moves.append(Move((r, c), (endrow, endcol), self.board))
                    elif endpeice[0] == enemy_color:  # is enemy peice
                        moves.append(Move((r, c), (endrow, endcol), self.board))






        pass

    def getBishopMoves(self,r,c,moves):

        peice_pinned = False
        pin_direction = ()

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                peice_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])  # since we have already accounted for this pin, remove it.
                break

        direction = ((-1, 1), (1, -1), (1, 1), (-1, -1))
        enemy_color = "b" if self.white_to_move else "w"
        for d in direction:
            for i in range(1, 8):
                endrow = r + d[0] * i
                endcol = c + d[1] * i
                if 0 <= endrow < 8 and 0 <= endcol < 8:

                    if not peice_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        endpeice = self.board[endrow][endcol]  # the peice to which we can move to
                        if endpeice == "--":  # is empty
                            moves.append(Move((r, c), (endrow, endcol), self.board))
                        elif endpeice[0] == enemy_color:  # is enemy peice
                            moves.append(Move((r, c), (endrow, endcol), self.board))
                            break  # break loop in that case
                        else:
                            break  # cuz invalid
                else:
                    break

    def check_for_pins_and_checks(self): #note that if your peice is pinned by an enemy peice, the enemy peice must be a anything other than a knight
        pins = [] #square where allyied peice is pinned and direction of pin.
        checks = [] #squares from which the the enemy peice checks.
        in_check = False

        if self.white_to_move:
            ally_color = 'w'
            enemy_color = 'b'
            start_row = self.white_king_loc[0]
            start_col = self.white_king_loc[1]
        else:
            ally_color = 'b'
            enemy_color = 'w'
            start_row = self.black_king_loc[0]
            start_col = self.black_king_loc[1]

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1),(-1, 1), (-1, -1), (1, 1), (1, -1)) #all possible directions

        for j in range(len(directions)):
            possible_pins = () #create empty tuple
            d = directions[j]

            for i in range(1,8):
                endrow = start_row +d[0]*i
                endcol = start_col + d[1]*i

                if (0<= endrow < 8) and (0<= endcol <8):
                    endpeice = self.board[endrow][endcol]
                    if endpeice[0] == ally_color and endpeice[1] != "K": #this has potential of pin
                        if possible_pins == (): #so it is empty, so only 1 peice so far in that direction.
                            possible_pins = (endrow,endcol,d[0],d[1])
                            #we dont know if this peice is pinned, we wont know that until we see what further ahead. like if we are going in a diagonal direction. our queen is lyinhg in same diagonal as king, but further ahead, there muight or might not be an enemy bishop.
                            #but for now, we will consider it pinned
                        else:
                            #since tuple is not empty, there are two allied peices in that direction. like a pawn and a bishop and a king are on same diagonal and further ahead, there might be an enemy bishop or not be. but whjatever the case, we arnt pinned. both the pawn and the bishop can move.
                            break
                    elif endpeice[0] == enemy_color: #this has potential of check
                        #if the next peice is enemy color, there are several possibilities.
                        type = endpeice[1]
                        #1) orthogonally away from king and enemy peice is rook
                        #2) diagonally away from king and enemy peice is bishop
                        #3) 1 square diagonally away from king and enemy peice is pawn.
                        #4) any direction and enemy peice is queen.
                        #5) any direction , 1 squr away, and enemy peice is king

                        if (0 <= j <= 3 and type == "R") or (4 <= j <= 7 and type == "B") or \
                                (i == 1 and type == 'p' and ((enemy_color == 'w' and 6 <= j <= 7) or (
                                        enemy_color == 'b' and 4 <= j <= 5))) or \
                                (type == "Q") or (i == 1 and type == "K"):
                            if possible_pins == () : #nothing is blocking, so check
                                in_check = True
                                checks.append((endrow,endcol, d[0], d[1]))
                                #since only 1 check is possible from that direction ==>
                                break
                            else: # peice is blocking this check.
                                pins.append(possible_pins) # so our possibility was true. cuz further in that direction, someone is checking if peice moves.
                                break

                        else:
                            #since none of the 5 conditions satisfied, no check/ pin
                            break
                else:
                    #out of board.
                    break

        #checks and pins for knight.
        knightmoves = ((2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2))
        for m in knightmoves:
            endrow = start_row + m[0]
            endcol = start_col + m[1]

            if (0<= endrow < 8) and (0<= endcol <8):
                endpeice = self.board[endrow][endcol]

                if endpeice[0] == enemy_color and endpeice[1] == "N":
                    in_check = True
                    checks.append((endrow,endcol, m[0], m[1]))


        return in_check, pins, checks



    def getCastleMoves(self, r, c, moves, allycolor):
        if self.square_under_attack(r,c):
            return #as we cant castle if in check

        if (self.white_to_move and self.current_castleing_rights.white_king_side) or( not self.white_to_move and self.current_castleing_rights.black_king_side):
            self.get_King_side_castle_moves(r,c,moves, allycolor)
        if (self.white_to_move and self.current_castleing_rights.white_queen_side) or (
                not self.white_to_move and self.current_castleing_rights.black_queen_side):
            self.get_Queen_side_castle_moves(r, c, moves, allycolor)

    def get_King_side_castle_moves(self, r,c,moves,allycolor):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.square_under_attack(r,c+1) and not self.square_under_attack(r, c+2):
                moves.append(Move((r,c), (r,c+2), self.board, isCastleMove = True))



    def get_Queen_side_castle_moves(self,r,c,moves,allycolor):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.square_under_attack(r,c-1) and not self.square_under_attack(r, c-2):
                moves.append(Move((r,c), (r,c-2), self.board, isCastleMove = True))



