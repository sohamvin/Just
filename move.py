
class Move():

    #maps keys to values
    #key :: value

    rankToRows = {'1':7, '2':6,'3':5,"4":4,'5':3,'6':2,'7':1,'8':0} #rank = rows. 1st rank is 7th row in our pygame screen.
    filesToCols = {'a':0, 'b': 1, "c":2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7} #similar

    rowsToRanks = {v: k for k, v in rankToRows.items()} #reverses rankToRows dictionary. keys replaced by values and values by keys
    colsToFiles = {v: k for k, v in filesToCols.items()}#same

    def __init__(self, start_sqr, end_sqr, current_board_state, isEnpassantMove = False, isCastleMove = False):
        self.startrow = start_sqr[0]
        self.startcol = start_sqr[1]

        self.endrow= end_sqr[0]
        self.endcol = end_sqr[1]

        self.peice_moved = current_board_state[self.startrow][self.startcol]
        if not isEnpassantMove:
            self.peice_captured = current_board_state[self.endrow][self.endcol]
        else:
            self.peice_captured = current_board_state[self.endrow - 1][self.endcol]


        self.isPawnPromotion = False
        if (self.peice_moved == 'wp' and self.endrow == 0) or (self.peice_moved == 'bp' and self.endrow == 7):
            self.isPawnPromotion = True

        self.isEnpassantMove = isEnpassantMove

        if self.isEnpassantMove:
            self.peice_captured = 'wp' if self.peice_moved == 'bp' else 'bp'

        self.iscastleMove = isCastleMove

        self.moveID = self.startrow * 1000 + self.startcol * 100 + self.endrow * 10 + self.endcol  # gives usinque move id for each move. no 2 moves would have same id


    def get_chess_notation(self):
        return self.get_rank_file(self.startrow,self.startcol) + self.get_rank_file(self.endrow, self.endcol)



    def get_rank_file(self,row,col):
        return self.colsToFiles[col] + self.rowsToRanks[row] # it will return a string. like 'a4', or 'h1'
        pass

    def __eq__(self, other): #overloading == opertaor to compare 2 objs.
        if isinstance(other,Move):
            return self.moveID == other.moveID #return True if the move ids are equal, i.e. same move
        return False
