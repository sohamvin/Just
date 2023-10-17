
import pygame as py

import Engine

from Actual_AI import Chess_Smart_Ai as ChAI



py.init()

WIDTH = HEIGHT = 512
DIMENTIONS = 8
SQ_SIZE = HEIGHT//DIMENTIONS
MAX_FPS = 15
IMAGES = {}
MOVING_IMAGES = {}


def loadImages():
    peices = ['wp','wR', 'wN', 'wB', 'wK', 'wQ',"bp",'bR','bN','bB','bK','bQ']


    for peice in peices:
        IMAGES[peice] = py.transform.scale(py.image.load('images/'+peice+'.png'),(SQ_SIZE,SQ_SIZE))
        MOVING_IMAGES[peice] = py.transform.scale(py.image.load('movingimages/' + peice + '.png'), (SQ_SIZE, SQ_SIZE))


def main():
    py.init()
    screen = py.display.set_mode((WIDTH,HEIGHT))
    clock = py.time.Clock()
    gs = Engine.GameState()

    validMoves = gs.get_Valid_moves()

    #flags
    moveMade = False #flag variable for when a move is made
    animate = False
    game_over = False
    stalemate = False

    player_one = True#if human playing white, the True. else False
    player_Two = False#same for black


    print(gs.board)
    loadImages()
    running = True
    square_selected= ()
    player_clicks = [] #keeps track of player clicks {tuples :: [initial_pos,final_pos] :: [(3,4),(3,5)]

    while running:
        is_huma_turn = (gs.white_to_move and player_one) or (not gs.white_to_move and player_Two)
        for e in py.event.get():
            if e.type == py.QUIT:
                running = False

            elif e.type == py.MOUSEBUTTONDOWN:
                if not game_over and is_huma_turn:
                    loc = py.mouse.get_pos() #x,y pos on screen
                    col = loc[0]//SQ_SIZE
                    row = loc[1]//SQ_SIZE

                    if square_selected == (row,col): #if user double clicked on that square
                        square_selected = () #readjust value to null
                        player_clicks = [] #readjust value to null

                    else:
                        square_selected = (row,col)
                        player_clicks.append(square_selected) #append for 1st ad second click.

                    if len(player_clicks) ==2 : #so after the 2nd click, so 3rd click will be the pos we want to move to
                        move = Engine.Move(player_clicks[0],player_clicks[1],gs.board)
                        print(move.get_chess_notation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.make_Move(validMoves[i])
                                moveMade = True
                                animate = True
                                square_selected = () #reset user clickes
                                player_clicks = []
                        if not moveMade:
                            player_clicks = [square_selected]

                # else:
                #     gs = Engine.GameState()
                #     validMoves = gs.get_Valid_moves()
                #     square_selected = ()
                #     player_clicks = []
                #     moveMade = False
                #     animate = False


            elif e.type == py.KEYDOWN:
                if e.key == py.K_z: #press z to undo
                    gs.undo_Move()
                    animate = False
                    moveMade = True# since undoing a move (which had to be a valid move , as otherwise we arent redering it) is a valid move
                    if(game_over):
                        game_over = False

                if e.key == py.K_r: #r key to reset
                    gs =Engine.GameState()
                    validMoves = gs.get_Valid_moves()
                    square_selected = ()
                    player_clicks = []
                    moveMade = False
                    animate = False


        #AI Move Finder Logic. not inside clicks cuz ais turns doesnt need clicks
        if not game_over and not is_huma_turn:
            AImove = ChAI.find_best_moves(gs, validMoves)

            if AImove is None:
                AImove = ChAI.find_random_move(validMoves)
            gs.make_Move(AImove)
            moveMade = True
            animate = True


        if moveMade: #if a valid move is made
            if animate:
                animate_move(gs.moveLog[-1], screen, gs.board, clock)  # animate last move in movelog
            validMoves = gs.get_Valid_moves() #since the gamestate changes/ the loc of peices changed, we need a new set of lavid moves for this new state of the board

            if(not gs.inCheck() and len(validMoves) == 0):
                stalemate = True
            elif(gs.inCheck() and len(validMoves) == 0):
                game_over = True
            else:
                peices = []
                for r in gs.board:
                    for c in r:
                        if[c != '--']:
                            peices.append(c)
                if(len(peices) == 2):
                    stalemate = True
            gs.set_stalemate_checkmate()

            moveMade = False #set the flag back to false as it is used to track if valid move made.

        drawGameState(screen,gs, validMoves, square_selected)

        if gs.checkmate:
            if(gs.white_to_move):
                Draw_text(screen, "Black Wins By CHECKMATE")
            else:
                Draw_text(screen, "White Wins By CHECKMATE")

        if gs.stalemate:
            Draw_text(screen, "Salemate")

        clock.tick(MAX_FPS)
        py.display.flip()





"""
Highlight square seleceted.
"""

def highlight_Square(screen, game_state, validmoves, squ_selected, move = None):
    if squ_selected != ():
        r, c = squ_selected
        if game_state.board[r][c][0] == ('w' if game_state.white_to_move else 'b'):
            s = py.Surface((SQ_SIZE, SQ_SIZE))
            s1 = py.Surface((SQ_SIZE, SQ_SIZE))

            #highlight selected square
            s.set_alpha(100) # 0 is transparent, 255 is opaque
            s1.set_alpha(50)
            s.fill(py.Color('blue'))
            #s1.fill(py.Color('red'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            # screen.blit(s1, (move.startcol*SQ_SIZE, move.startrow*SQ_SIZE))
            # screen.blit(s1, (move.endcol*SQ_SIZE, move.endrow*SQ_SIZE))

            #highlight moves from square
            s.fill(py.Color('yellow'))
            for move in validmoves:
                if move.startrow == r and move.startcol == c:
                    screen.blit(s, (move.endcol*SQ_SIZE, move.endrow*SQ_SIZE))





def drawGameState(screen, gs, validMoves, SQ_selected):
    drawBoard(screen) #draws squares on board
    #last_move = gs.last_move_played
    highlight_Square(screen, gs, validMoves, SQ_selected)
    drawPeices(screen,gs.board)


"""draw """
def drawBoard(screen):
    global colors
    colors = [py.Color("white"),py.Color('gray')]
    for row in range(DIMENTIONS):
        for col in range(DIMENTIONS):
            color = colors[((row+col)%2)]
            py.draw.rect(screen,color,py.Rect(col*SQ_SIZE,row*SQ_SIZE,SQ_SIZE,SQ_SIZE))
    pass

"""draw peices on the board using current gamestates board variable"""
def drawPeices(screen,board):
    for row in range(DIMENTIONS):
        for col in range(DIMENTIONS):
            peice = board[row][col]
            if peice != "--":
                screen.blit(IMAGES[peice],py.Rect(col*SQ_SIZE,row*SQ_SIZE,SQ_SIZE,SQ_SIZE))



def animate_move(move, screen, board, clock):
    global colors
    co_ord = []
    dR = move.endrow - move.startrow
    dC = move.endcol - move.startcol
    frames_per_square = 10 #how many frames of animation per square. so if more, peice moves slower.
    framecount = ((abs(dR)) + (abs(dC)))*frames_per_square #eg, if knight moves, (2+1)*frames_per_square so we want to animate the move in
    # ato total of 30 frames

    for frame in range(framecount+1):
        r,c =(move.startrow + dR*frame/framecount, move.startcol + dC*frame/framecount) #r, c is current squares in the animation. depending on
        #what frame the peice is
        drawBoard(screen) #draw board 1st
        drawPeices(screen,board) #then draw peices
        color = colors[(move.endcol + move.endrow)%2]
        endsqr =py.Rect(move.endcol*SQ_SIZE, move.endrow*SQ_SIZE, SQ_SIZE, SQ_SIZE) #draw rectangle
        py.draw.rect(screen, color, endsqr)

        if(move.peice_captured != '--'):
            screen.blit(IMAGES[move.peice_captured], endsqr) #if we are captiuring a peice, blit all the images again

        screen.blit(IMAGES[move.peice_moved], py.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        py.display.flip()
        clock.tick(200) # makes animation smooth and faster


def Draw_text(screen, s):
    font = py.font.SysFont("Helvitca", 32, True, False)
    font_obj = font.render(s, 0, py.Color('Black'))
    text_loc = py.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - font_obj.get_width()/2, HEIGHT/2 - font_obj.get_height()/2)
    screen.blit(font_obj, text_loc)
    pass


if __name__ == "__main__":
    main()
