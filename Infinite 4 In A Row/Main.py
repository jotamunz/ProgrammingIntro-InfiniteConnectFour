import numpy as np
import pygame
import sys
import math
import random
from pygame import gfxdraw

#E: ninguna
#S: una matriz nula de 6x7
#D: crea el tablero inicial
def createBoard():
    board = np.zeros((6,7))
    return board

#Variables Globales
turn = False
board = createBoard()
columns = [0, 1, 2, 3, 4, 5, 6]
rows = [0, 1, 2, 3, 4, 5]
pause = False
Player1 = ""
Player2 = ""
scores = []
center = 0
tall = 0
indexColumn = 0
indexRow = 0
multGames = []
singleGames = []
loading = False

#Colors
purple = (147,112,219)
darkPurple = (72,61,139)
orange = ((255,99,71))
blue = (0,191,255)
black = (0,0,0)
violet = (238,130,238)
green = (152,251,152)
gray = (169,169,169)

#############################################################################
#                 DOCS
#############################################################################

#E: path del archivo y un string
#S: ninguna
#D: sobreescribe un archivo
def saveDoc(path, string):
    fo = open(path, 'w')
    fo.write(string)
    fo.close()

#E: path del archivo
#S: string del archivo
#D: lee un archivo
def readDoc(path):
    fo = open(path, 'r')
    text = fo.read()
    fo.close()
    return text

#E: path del archivo
#S: lista del archivo
#D: lee y evalua un archivo tipo lista
def loadDoc(path):
    text = readDoc(path)
    if text == "":
        return []
    else:
        return eval(text)

#############################################################################
#               FUNCTIONS
#############################################################################

#E: una matriz y un numero entero
#S; un booleano
#D: retorna si la columna esta llena
def columnNotFull(board, column):
    if board[0][column] == 0:
        return True
    else:
        return False

#E: una matriz y un numero entero
#S: un booleano
#D: retorna si la ficha esta a 7 columnas de alguna ficha ya puesta
def correctDistance(board, column):
    if np.any(board) == False:
        return True
    else:
        try:
            for i in range(column-7, column+8):
                if i < 0:
                    continue
                if board[-1][i] != 0:
                    return True
            return False
        except:
            return False

#E: una matriz y un numero entero
#S: un numero entero
#D: retorna la siguiente fila disponible para una columna
def nextOpenRow (board, column):
    global rows
    openRow = rows[-1]
    for row in rows:
        if board[row][column] == 0:
            continue
        else:
            openRow = row - 1
            break
    return openRow

#E: una matriz y tres numeros enteros
#S: ninguna
#D: remplaza una posicion en la matriz por una pieza
def placePiece(board, row, column, piece):
    board[row][column] = piece

#E: una matriz y un numero entero
#S: un booleano
#D: retorna si hay un 4 en linea
def checkWin(board, piece):
    #horizontal
    for column in columns[:-3]:
        for row in rows:
            if board[row][column] == piece and board[row][column+1] == piece and board[row][column+2] == piece and board[row][column+3] == piece:
                return True
    #vertical
    for row in rows[:-3]:
        for column in columns:
            if board[row][column] == piece and board[row+1][column] == piece and board[row+2][column] == piece and board[row+3][column] == piece:
                return True
    #diagonal increasing
    for row in rows[3:]:
        for column in columns[:-3]:
            if board[row][column] == piece and board[row-1][column+1] == piece and board[row-2][column+2] == piece and board[row-3][column+3] == piece:
                return True
    #diagonal decreasing
    for row in rows[:-3]:
        for column in columns[:-3]:
            if board[row][column] == piece and board[row+1][column+1] == piece and board[row+2][column+2] == piece and board[row+3][column+3] == piece:
                return True

#E: una matriz y un entero
#S: un numero entero
#D: retorna el puntaje de poner una pieza
def scoreValue(board, piece):
    score = 0
    #center
    centerArray = [int(i) for i in list(board[:,len(columns)//2])]
    centerCount = centerArray.count(piece)
    score += centerCount * 3
    #horizontal
    for row in rows:
        rowArray = [int(i) for i in list(board[row,:])]
        for column in columns[:-3]:
            window = rowArray[column:column+4]
            score += evaluateWindow(window, piece)
    #vertical
    for column in columns:
        columnArray = [int(i) for i in list(board[:,column])]
        for row in rows[:-3]:
            window = columnArray[row:row+4]
            score += evaluateWindow(window, piece)
    #diagonal increasing
    diagonalRow = rows[3:]
    for row in diagonalRow[::-1]:
        for column in columns[:-3]:
            window = [board[row-i][column+i] for i in range(4)]
            score += evaluateWindow(window, piece)
    # diagonal decreasing
    diagonalRow2 = rows[:-3]
    for row in diagonalRow2[::-1]:
        for column in columns[:-3]:
            window = [board[row+i][column+i] for i in range(4)]
            score += evaluateWindow(window, piece)
    return score

#E: una matriz y un entero
#S: un numero entero
#D: retorna el puntaje de una ventana
def evaluateWindow(window, piece):
    score = 0
    playerPiece = 1
    if piece == 1:
        playerPiece = 2
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2
    elif window.count(playerPiece) == 3 and window.count(0) == 1:
        score -= 4
    return score

#E: una matriz y un entero
#S: un numero entero
#D: retorna la mejor columna de acuerdo al puntaje
def bestMove(board, piece):
    validColumns = checkValidColumns(board)
    bestScore = -10000
    bestColumn = random.choice(validColumns)
    for column in validColumns:
        row = nextOpenRow(board, column)
        tempBoard = board.copy()
        placePiece(tempBoard, row, column, piece)
        score = scoreValue(tempBoard, piece)
        if score > bestScore:
            bestScore = score
            bestColumn = column
    return bestColumn

#E: una matriz, un numero entero, dos infinitos, y un booleano
#S: dos numeros enteros
#D: algoritmo minimax para evaluar arboles
def minimax(board, depth, alpha, beta, maxPlayer):
    validColumns = checkValidColumns(board)
    if depth == 0 or terminalNode(board) == True:
        if depth == 0:
            return (None, scoreValue(board, 2))
        else:
            if checkWin(board, 2):
                return (None, 100000000000)
            elif checkWin(board, 1):
                return (None, -10000000000)
            else:
                return (None, 0)
    if maxPlayer == True:
        value = -math.inf
        bestColumn = random.choice(validColumns)
        for column in validColumns:
            row = nextOpenRow(board, column)
            tempBoard = board.copy()
            placePiece(tempBoard, row, column, 2)
            newScore = minimax(tempBoard, depth-1, alpha, beta, False)[1]
            if newScore > value:
                value = newScore
                bestColumn = column
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return bestColumn, value
    else:
        value = math.inf
        bestColumn = random.choice(validColumns)
        for column in validColumns:
            row = nextOpenRow(board, column)
            tempBoard = board.copy()
            placePiece(tempBoard, row, column, 1)
            newScore = minimax(tempBoard, depth-1, alpha, beta, True)[1]
            if newScore < value:
                value = newScore
                bestColumn = column
            beta = min(beta, value)
            if alpha >= beta:
                break
        return bestColumn, value

#E: una matriz
#S: un booleano
#D: retorna si es un nodo terminal
def terminalNode(board):
    return checkWin(board, 1) or checkWin(board, 2) or len(checkValidColumns(board)) == 0

#E: una matriz
#S: una lista
#D: retorna las columnas que no estan llenas
def checkValidColumns(board):
    validColumns = []
    for column in columns:
        if columnNotFull(board, column) == True:
            validColumns.append(column)
    return validColumns

#E: una matriz
#S: una matriz
#D: agrega una columna a la izquierda
def addColumnLeft(board):
    newBoard = np.insert(board, 0, 0, 1)
    return newBoard

#E: una matriz
#S: una matriz
#D: agrega 7 columnas a la izquierda y aumenta la lista de columnas
def expandLeft(board):
    global columns
    i = 0
    j = len(columns)-1
    while i < 7:
        board = addColumnLeft(board)
        i += 1
        columns += [j+1]
        j += 1
    return board

#E: ninguna
#S: un booleano
#D: retorna si ya hay un tablero a la izquierda
def checkLeft():
    global center
    if center - 7 >= 0:
        return True
    else:
        return False

#E: una matriz
#S: una matriz
#D: agrega una columna a la derecha
def addColumnRight(board):
    global columns
    i = len(columns)
    newBoard = np.insert(board, i, 0, 1)
    return newBoard

#E: una matriz
#S: una matriz
#D: agrega 7 columnas a la derecha y aumenta la lista de columnas
def expandRight(board):
    global columns
    i = 0
    j = len(columns)-1
    while i < 7:
        board = addColumnRight(board)
        i += 1
        columns += [j+1]
        j += 1
    return board

#E: ninguna
#S: un booleano
#D: retorna si ya hay un tablero a la derecha
def checkRight():
    global center, columns
    if center + 7 <= len(columns) - 1:
        return True
    else:
        return False

#E: una matriz
#S: una matriz
#D: agrega una fila encima
def addRowUp(board):
    newBoard = np.insert(board, 1, 0, 0)
    return newBoard

#E: una matriz
#S: una matriz
#D: agrega 7 filas encima y aumenta la lista de filas
def expandUp(board):
    global rows
    i = 0
    j = len(rows)-1
    while i < 6:
        board = addRowUp(board)
        i += 1
        rows += [j+1]
        j += 1
    return board

#E: ninguna
#S: un booleano
#D: retorna si ya hay un tablero arriba
def checkUp():
    global tall
    if tall - 6 >= 0:
        return True
    else:
        return False

#E: ninguna
#S: un booleano
#D: retorna si ya hay un tablero abajo
def checkDown():
    global tall, rows
    if tall + 6 <= len(rows) - 1:
        return True
    else:
        return False

#E: una matriz
#S: una matriz
#D: corta el pedazo de la matriz que esta en juego
def cutBoard(board):
    global center, tall
    cutBoard = board[tall:tall+6, center:center+7]
    return cutBoard

#E: un string
#S: ninguna
#D: agrega una lista de jugador y puntaje a la lista ranking
def addScore(player):
    global scores
    result = []
    modified = False
    if scores == []:
        result += [[player, 1]]
    else:
        for element in scores:
            if element[0] == player:
                result += [[player, element[1]+1]]
                modified = True
            else:
                result += [element]
        if modified == False:
            result += [[player, 1]]
    scores = result
    saveDoc('Ranking.txt', str(scores))
    print('Point added to ' + player)
    return

#E: ninguna
#S: una lista
#D: retorna una lista con los primeros 5 puntajes
def topScore():
    global scores
    points = []
    result = []
    top = 1
    for element in scores:
        points += [element[1]]
        top = max(points)
    for i in reversed(range(1, top+1)):
        for element in scores:
            if element[1] == i:
                result += [element]
                if len(result) == 5:
                    return result
    while len(result) < 5:
        result += [['Empty', 0]]
    return result

#############################################################################
#               GRAPHICS
#############################################################################

#E: una matriz
#S: interfaz grafica
#D: dibuja la seccion del tablero que se esta jugando
def drawBoard(board):
    global rows, columns, window, purple, darkPurple, orange, blue, square, center
    for row in rows[:6]:
        for column in columns[:7]:
            pygame.draw.rect(window, purple, (column*square,row*square+square, square, square))
            if board[row][column] == 0:
                pygame.gfxdraw.aacircle(window, column*square+50, row*square+square+50, 45, darkPurple)
                pygame.gfxdraw.filled_circle(window, column*square+50, row*square+square+50, 45, darkPurple)
            elif board[row][column] == 1:
                pygame.gfxdraw.aacircle(window, column*square+50, row*square+square+50, 45, blue)
                pygame.gfxdraw.filled_circle(window, column*square+50, row*square+square+50, 45, blue)
            elif board[row][column] == 2:
                pygame.gfxdraw.aacircle(window, column*square+50, row*square+square+50, 45, orange)
                pygame.gfxdraw.filled_circle(window, column*square+50, row*square+square+50, 45, orange)
    pygame.display.update()

#E: ninguna
#S: interfaz grafica
#D: dibuja los indices en el eje X
def drawIndexX():
    global indexColumn
    draw = True
    positionX = 50
    positionY = 650
    while draw == True:
        if positionX <= 650:
            for i in range(indexColumn, indexColumn+7):
                displayText(str(i), smallFont, black, (positionX, positionY))
                positionX += 100
            pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:
                    draw = False

#E: ninguna
#S: interfaz grafica
#D: dibuja los indices en el eje Y
def drawIndexY():
    global indexRow
    draw = True
    positionX = 50
    positionY = 650
    while draw == True:
        if positionY >= 150:
            for i in range(indexRow, indexRow+6):
                displayText(str(i), smallFont, black, (positionX, positionY))
                positionY -= 100
            pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    draw = False

#E: un string
#S: interfaz grafica
#D: muestra un texto en pantalla
def displayText(text, font, color, location):
    textSurface = font.render(text, True, color)
    textRect = textSurface.get_rect()
    textRect.center = location
    window.blit(textSurface, textRect)

#D: funcion descargada para obtener la tecla presionada
def getKey():
  while 1:
      event = pygame.event.poll()
      if event.type == pygame.KEYDOWN:
          return event.key

#D: funcion descargada para crear un text box
def displayBox(screen, message):
  pygame.draw.rect(screen, (0, 0, 0), ((screen.get_width() / 2) - 130, (screen.get_height() / 2) - 10, 255, 20), 0)
  pygame.draw.rect(screen, darkPurple, ((screen.get_width() / 2) - 131, (screen.get_height() / 2) - 11, 257, 22), 2)
  if len(message) != 0:
      screen.blit(miniFont.render(message, 1, (255, 255, 255)), ((screen.get_width() / 2) - 125, (screen.get_height() / 2) - 5))
  pygame.display.update()

#D: funcion descargada para recibir input en texto
def inputText(screen, question):
  current_string = []
  string=''
  displayBox(screen, question + ": " + string.join(current_string))
  while 1:
      inkey = getKey()
      if inkey == pygame.K_BACKSPACE:
          current_string = current_string[0:-1]
      elif inkey == pygame.K_RETURN:
          break
      elif inkey == pygame.K_MINUS:
          current_string.append("_")
      elif inkey <= 127:
          current_string.append(chr(inkey))
      displayBox(screen, question + ": " + string.join(current_string))
  return string.join(current_string)

#E: un string, 5 enteros, dos colores y una accion
#S: interfaz grafica
#D: crea un boton para el menu principal
def mainButton(message, x, y, w, h, color, hover, pos):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if (x + w) > mouse[0] > x and (y + h) > mouse[1] > y:
        displayText(message, smallFont, hover, pos)
        if click[0] == 1:
            if message == "MULTIPLAYER":
                return multMenu()
            elif message == "SINGLEPLAYER":
                return singleMenu()
            elif message == "SCORE":
                return scoreMenu()
    else:
        displayText(message, smallFont, color, pos)

#E: un string, 5 enteros, dos colores y una accion
#S: interfaz grafica
#D: crea un boton para vovler al menu principal
def backButton(message, x, y, w, h, color, hover, pos):
    global loading
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if (x + w) > mouse[0] > x and (y + h) > mouse[1] > y:
        displayText(message, mediumFont, hover, pos)
        if click[0] == 1:
            loading = False
            if message == "<":
                return mainMenu()
            elif message == "BACK":
                return mainMenu()
    else:
        displayText(message, mediumFont, color, pos)

#E: un string, 5 enteros, dos colores y una accion
#S: interfaz grafica
#D: crea un boton para el menu singleplayer
def singleButton(message, x, y, w, h, color, hover, pos):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if (x + w) > mouse[0] > x and (y + h) > mouse[1] > y:
        displayText(message, smallFont, hover, pos)
        if click[0] == 1:
            if message == "NEW GAME":
                callNames2()
                return playSingle()
            elif message == "LOAD GAME":
                return loadSingle()
    else:
        displayText(message, smallFont, color, pos)

#E: un string, 5 enteros, dos colores y una accion
#S: interfaz grafica
#D: crea un boton para el menu multiplayer
def multButton(message, x, y, w, h, color, hover, pos):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if (x + w) > mouse[0] > x and (y + h) > mouse[1] > y:
        displayText(message, smallFont, hover, pos)
        if click[0] == 1:
            if message == "NEW GAME":
                callNames()
                return playMult()
            elif message == "LOAD GAME":
                return loadMult()
    else:
        displayText(message, smallFont, color, pos)

#E: un string, 5 enteros, dos colores y una accion
#S: interfaz grafica
#D: crea un boton para el menu de puntajes
def scoreButton(message, x, y, w, h, color, hover, pos):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if (x + w) > mouse[0] > x and (y + h) > mouse[1] > y:
        displayText(message, smallFont, hover, pos)
        if click[0] == 1:
            if message == "BACK":
                return mainMenu()
            elif message == "MORE":
                pass
    else:
        displayText(message, smallFont, color, pos)

#E: dos strings, 5 enteros, dos colores y una accion
#S: interfaz grafica
#D: crea un boton para el menu multiplayer
def pauseButton(message, x, y, w, h, color, hover, pos, directory):
    global pause
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if (x + w) > mouse[0] > x and (y + h) > mouse[1] > y:
        displayText(message, smallFont, hover, pos)
        if click[0] == 1:
            if message == "CONTINUE":
                pause = False
            elif message == "SAVE":
                pause = False
                saveGame(directory)
                reset()
                return start()
            elif message == "EXIT":
                pause = False
                reset()
                return start()
    else:
        displayText(message, smallFont, color, pos)

#E: un string, 5 enteros, dos colores y una lista
#S: interfaz grafica
#D: crea un boton para el cargar una partida
def loadButton(message, x, y, w, h, color, hover, pos, game):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if (x + w) > mouse[0] > x and (y + h) > mouse[1] > y:
        displayText(message, tinyFont, hover, pos)
        if click[0] == 1:
            return loadGame(game)
    else:
        displayText(message, tinyFont, color, pos)

#############################################################################
#                 START
#############################################################################

#Variables Globales
square = 100
width = 7*100
height = (6+1)*100
background = pygame.image.load("Background Resize.jpg")
icon = pygame.image.load("Icon.png")
logo = pygame.image.load("Logo.png")

pygame.init()
pygame.mixer.pre_init(44100, 16, 2, 4096)

window = pygame.display.set_mode((width, height))
pygame.display.set_caption('4 In A Row')
pygame.display.set_icon(icon)

#Fonts
titleFont = pygame.font.SysFont('Arcade Normal', 60)
mediumFont = pygame.font.SysFont('Arcade Normal', 50)
smallFont = pygame.font.SysFont('Arcade Normal', 25)
tinyFont = pygame.font.SysFont('Arcade Normal', 15)
miniFont = pygame.font.SysFont('Arcade Normal', 10)

#Sounds
#selector1 = pygame.mixer.Sound("Selector 1 Sound.wav")
#selector2 = pygame.mixer.Sound("Selector 2 Sound.wav")
#fanfare = pygame.mixer.Sound("Fanfare Sound.wav")
correct = pygame.mixer.Sound("Correct Sound.wav")
correct.set_volume(0.6)
error = pygame.mixer.Sound("Error Sound.wav")
error.set_volume(0.7)

#############################################################################
#              GAME LOOPS
#############################################################################

#D: plays Once Upon a Time
def playSong1():
    pygame.mixer.music.load("Warp Drive.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)

#D: plays Ruins
def playSong2():
    pygame.mixer.music.load("Mechanism Pilot.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)

#D: call for input of 2 names
def callNames():
    global Player1, Player2
    pygame.draw.rect(window, gray, (193, 305, 310, 100))
    pygame.draw.rect(window, darkPurple, (193, 305, 310, 100), 4)
    Player1 = inputText(window, "Player 1")
    Player2 = inputText(window, "Player 2")

#D: call for input of 1 name
def callNames2():
    global Player1, Player2
    pygame.draw.rect(window, gray, (193, 305, 310, 100))
    pygame.draw.rect(window, darkPurple, (193, 305, 310, 100), 4)
    Player1 = inputText(window, "Player")
    Player2 = 'System'

#D: starts main theme, loads documents and main menu
def start():
    global scores, multGames, singleGames
    playSong1()
    scores = loadDoc("Ranking.txt")
    multGames = loadDoc("Multiplayer Games.txt")
    singleGames = loadDoc("Singleplayer Games.txt")
    return mainMenu()

#D: sets all values to originals
def reset():
    global Player1, Player2, board, turn, columns, rows, center, tall, indexColumn, indexRow
    Player1 = ""
    Player2 = ""
    center = 0
    tall = 0
    columns = [0, 1, 2, 3, 4, 5, 6]
    rows = [0, 1, 2, 3, 4, 5]
    board = createBoard()
    turn = False
    indexColumn = 0
    indexRow = 0

#D: saves all global variables to a directory
def saveGame(directory):
    global Player1, Player2, board, turn, columns, rows, center, tall, indexColumn, indexRow, multGames, singleGames
    from datetime import datetime
    today = datetime.now()
    date = today.strftime("%d/%m/%Y %I:%M:%S %p")
    board = board.tolist()
    if directory == 'Multiplayer Games.txt':
        multGames += [[date, Player1, Player2, board, turn, columns, rows, center, tall, indexColumn, indexRow]]
        saveDoc(directory, str(multGames))
    elif directory == 'Singleplayer Games.txt':
        singleGames += [[date, Player1, Player2, board, turn, columns, rows, center, tall, indexColumn, indexRow]]
        saveDoc(directory, str(singleGames))
    print("Game has been saved in", directory, 'at', date)
    return

#D: loads all global variables from a list
def loadGame(Game):
    global Player1, Player2, board, turn, columns, rows, center, tall, indexColumn, indexRow, loading
    Player1 = Game[1]
    Player2 = Game[2]
    board = Game[3]
    board = np.asarray(board)
    turn = Game[4]
    columns = Game[5]
    rows = Game[6]
    center = Game[7]
    tall = Game[8]
    indexColumn = Game[9]
    indexRow = Game[10]
    loading = False
    if Player2 == "System":
        return playSingle()
    else:
        return playMult()

#D: opens pause pop up
def paused(player, directory):
    global pause

    while pause == True:
        pygame.draw.rect(window, gray, (193, 125, 310, 340))
        pygame.draw.rect(window, darkPurple, (193, 125, 310, 340), 4)
        displayText("PAUSE", titleFont, darkPurple, (width / 2, 170))
        displayText("Current Turn:", tinyFont, darkPurple, (width / 2, 220))
        displayText(player, tinyFont, darkPurple, (width / 2, 250))
        pauseButton("CONTINUE", 250, 315, 200, 25, darkPurple, purple, (width / 2, 330), directory)
        pauseButton("SAVE", 300, 365, 100, 25, darkPurple, purple, (width / 2, 380), directory)
        pauseButton("EXIT", 300, 415, 100, 25, darkPurple, purple, (width / 2, 430), directory)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

#D: main menu display
def mainMenu():
    intro = True

    while intro == True:
        window.blit(background, (0, 0))
        window.blit(logo, (width/2 - 200, 50))
        # pygame.draw.rect(window, green, (205, 315, 290, 25))
        mainButton("SINGLEPLAYER", 205, 315, 290, 25, purple, violet, (width / 2, 330))
        mainButton("MULTIPLAYER", 215, 395, 270, 25, purple, violet, (width / 2, 410))
        mainButton("SCORE", 290, 475, 120, 25, purple, violet, (width / 2, 490))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

#D: singleplayer menu display
def singleMenu():
    introS = True

    while introS == True:
        window.blit(background, (0, 0))
        window.blit(logo, (width/2 - 200, 50))
        singleButton("NEW GAME", 250, 315, 200, 25, purple, violet, (width / 2, 330))
        singleButton("LOAD GAME", 240, 395, 220, 25, purple, violet, (width / 2, 410))
        backButton("<", 40, 40, 35, 40, purple, violet, (63, 63))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

#D: multipayer menu display
def multMenu():
    introM = True

    while introM == True:
        window.blit(background, (0, 0))
        window.blit(logo, (width/2 - 200, 50))
        multButton("NEW GAME", 250, 315, 200, 25, purple, violet, (width / 2, 330))
        multButton("LOAD GAME", 240, 395, 220, 25, purple, violet, (width / 2, 410))
        backButton("<", 40, 40, 35, 40, purple, violet, (63, 63))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

#D: score menu display
def scoreMenu():
    introR = True

    while introR == True:
        window.blit(background, (0, 0))
        ranking = topScore()
        displayText("HIGH SCORES", titleFont, purple, (width / 2, 90))
        displayText(ranking[0][0] + ' ' + str(ranking[0][1]), smallFont, purple, (width / 2, 170))
        displayText(ranking[1][0] + ' ' + str(ranking[1][1]), smallFont, purple, (width / 2, 250))
        displayText(ranking[2][0] + ' ' + str(ranking[2][1]), smallFont, purple, (width / 2, 330))
        displayText(ranking[3][0] + ' ' + str(ranking[3][1]), smallFont, purple, (width / 2, 410))
        displayText(ranking[4][0] + ' ' + str(ranking[4][1]), smallFont, purple, (width / 2, 490))
        scoreButton("BACK", 300, 555, 100, 25, purple, violet, (width / 2, 570))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

#D: multiplayer load box display
def loadMult():
    global multGames, loading
    reversedMultGames = multGames[::-1]
    loading = True

    while loading == True:
        backButton("<", 40, 40, 35, 40, purple, violet, (63, 63))
        pygame.draw.rect(window, gray, (178, 60, 346, 590))
        pygame.draw.rect(window, darkPurple, (178, 60, 346, 590), 4)
        moveY = 0
        for game in reversedMultGames:
            loadButton(game[0], 185, 70 + moveY, 333, 20, darkPurple, purple, (width / 2, 80 + moveY), game)
            moveY += 25
            if moveY > 550:
                break

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

#D: singleplayer load box display
def loadSingle():
    global singleGames, loading
    reversedSingleGames = singleGames[::-1]
    loading = True

    while loading == True:
        backButton("<", 40, 40, 35, 40, purple, violet, (63, 63))
        pygame.draw.rect(window, gray, (178, 60, 346, 590))
        pygame.draw.rect(window, darkPurple, (178, 60, 346, 590), 4)
        moveY = 0
        for game in reversedSingleGames:
            loadButton(game[0], 185, 70 + moveY, 333, 20, darkPurple, purple, (width / 2, 80 + moveY), game)
            moveY += 25
            if moveY > 550:
                break

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

#D: game loop for multiplayer
def playMult():
    global turn, window, width, square, Player1, Player2, board, columns, rows, pause, center, tall, indexColumn, indexRow
    gameOver = False
    firstTurn = True
    playSong2()
    print(board)
    if turn == False:
        print(Player1 + " make your move")
    else:
        print(Player2 + " make your move")

    while gameOver == False:
        playBoard = cutBoard(board)
        drawBoard(playBoard)
        if firstTurn == True:
            pygame.draw.rect(window, darkPurple, (0, 0, width, square))
            firstTurn = False
        pygame.display.update()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Pause game
                if event.key == pygame.K_TAB:
                    pause = True
                    if turn == False:
                        paused(Player1, 'Multiplayer Games.txt')
                    else:
                        paused(Player2, 'Multiplayer Games.txt')
                # Draw index
                if event.key == pygame.K_x:
                    drawIndexX()
                if event.key == pygame.K_y:
                    drawIndexY()
                # Move board left
                if event.key == pygame.K_LEFT:
                    indexColumn -= 7
                    if checkLeft() == False:
                        board = expandLeft(board)
                        center = 0
                        playBoard = cutBoard(board)
                        drawBoard(playBoard)
                    else:
                        center -= 7
                        playBoard = cutBoard(board)
                        drawBoard(playBoard)
                # Move board right
                if event.key == pygame.K_RIGHT:
                    indexColumn += 7
                    if checkRight() == False:
                        board = expandRight(board)
                        center += 7
                        playBoard = cutBoard(board)
                        drawBoard(playBoard)
                    else:
                        center += 7
                        playBoard = cutBoard(board)
                        drawBoard(playBoard)
                # Move board up
                if event.key == pygame.K_UP:
                    indexRow += 6
                    if checkUp() == False:
                        board = expandUp(board)
                        tall = 0
                        playBoard = cutBoard(board)
                        drawBoard(playBoard)
                    else:
                        tall -= 6
                        playBoard = cutBoard(board)
                        drawBoard(playBoard)
                # Move board down
                if event.key == pygame.K_DOWN:
                    if checkDown() == True:
                        indexRow -= 6
                        tall += 6
                        playBoard = cutBoard(board)
                        drawBoard(playBoard)
                pygame.display.update()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(window, darkPurple, (0, 0, width, square))
                moveX = event.pos[0]
                if turn == False:
                    pygame.gfxdraw.aacircle(window, moveX, square//2, square//2-5, blue)
                    pygame.gfxdraw.filled_circle(window, moveX, square//2, square//2-5, blue)
                else:
                    pygame.gfxdraw.aacircle(window, moveX, square//2, square//2-5, orange)
                    pygame.gfxdraw.filled_circle(window, moveX, square//2, square//2-5, orange)
                pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(window, darkPurple, (0, 0, width, square))
                # Player 1
                if turn == False:
                    clickX = event.pos[0]
                    column = math.floor(clickX / 100) + center
                    if columnNotFull(board, column) == True and correctDistance(board, column) == True:
                        row = nextOpenRow(board, column)
                        placePiece(board, row, column, 1)
                        print(board)
                        if checkWin(board, 1) == True:
                            print(Player1 + " wins!")
                            gameOver = True
                            winner = Player1
                        else:
                            turn = not turn
                            print(Player2 + " make your move")
                    else:
                        error.play()
                        print('Out of bounds')
                # Player 2
                else:
                    clickX = event.pos[0]
                    column = math.floor(clickX / 100) + center
                    if columnNotFull(board, column) == True and correctDistance(board, column) == True:
                        row = nextOpenRow(board, column)
                        placePiece(board, row, column, 2)
                        print(board)
                        if checkWin(board, 2) == True:
                            print(Player2 + " wins!")
                            gameOver = True
                            winner = Player2
                        else:
                            turn = not turn
                            print(Player1 + " make your move")
                    else:
                        error.play()
                        print('Out of bounds')

                playBoard = cutBoard(board)
                drawBoard(playBoard)
                pygame.display.update()
                if gameOver == True:
                    correct.play()
                    displayText(winner + ' wins!', smallFont, black, (width/2, height/2))
                    addScore(winner)
                    reset()
                    pygame.display.update()
                    pygame.time.wait(4000)
    playSong1()

#D: game loop for singleplayer
def playSingle():
    global turn, window, width, square, Player1, Player2, board, columns, rows, pause, center, tall, indexColumn, indexRow
    gameOver = False
    firstTurn = True
    playSong2()
    print(board)
    if turn == False:
        print(Player1 + " make your move")
    else:
        print(Player2 + " make your move")

    while gameOver == False:
        playBoard = cutBoard(board)
        drawBoard(playBoard)
        if firstTurn == True:
            pygame.draw.rect(window, darkPurple, (0, 0, width, square))
            firstTurn = False
        pygame.display.update()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Pause game
                if event.key == pygame.K_TAB:
                    pause = True
                    if turn == False:
                        paused(Player1, 'Singleplayer Games.txt')
                    else:
                        paused(Player2, 'Singleplayer Games.txt')
                # Draw index
                if event.key == pygame.K_x:
                    drawIndexX()
                if event.key == pygame.K_y:
                    drawIndexY()
                # Move board left
                if event.key == pygame.K_LEFT:
                    indexColumn -= 7
                    if checkLeft() == False:
                        board = expandLeft(board)
                        center = 0
                        playBoard = cutBoard(board)
                        drawBoard(playBoard)
                    else:
                        center -= 7
                        playBoard = cutBoard(board)
                        drawBoard(playBoard)
                # Move board right
                if event.key == pygame.K_RIGHT:
                    indexColumn += 7
                    if checkRight() == False:
                        board = expandRight(board)
                        center += 7
                        playBoard = cutBoard(board)
                        drawBoard(playBoard)
                    else:
                        center += 7
                        playBoard = cutBoard(board)
                        drawBoard(playBoard)
                # Move board up
                if event.key == pygame.K_UP:
                    indexRow += 6
                    if checkUp() == False:
                        board = expandUp(board)
                        tall = 0
                        playBoard = cutBoard(board)
                        drawBoard(playBoard)
                    else:
                        tall -= 6
                        playBoard = cutBoard(board)
                        drawBoard(playBoard)
                # Move board down
                if event.key == pygame.K_DOWN:
                    if checkDown() == True:
                        indexRow -= 6
                        tall += 6
                        playBoard = cutBoard(board)
                        drawBoard(playBoard)
                pygame.display.update()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(window, darkPurple, (0, 0, width, square))
                moveX = event.pos[0]
                if turn == False:
                    pygame.gfxdraw.aacircle(window, moveX, square//2, square//2-5, blue)
                    pygame.gfxdraw.filled_circle(window, moveX, square//2, square//2-5, blue)
                else:
                    pygame.gfxdraw.aacircle(window, moveX, square//2, square//2-5, orange)
                    pygame.gfxdraw.filled_circle(window, moveX, square//2, square//2-5, orange)
                pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(window, darkPurple, (0, 0, width, square))
                # Player 1
                if turn == False:
                    clickX = event.pos[0]
                    column = math.floor(clickX / 100) + center
                    if columnNotFull(board, column) == True and correctDistance(board, column) == True:
                        row = nextOpenRow(board, column)
                        placePiece(board, row, column, 1)
                        print(board)
                        if checkWin(board, 1) == True:
                            print(Player1 + " wins!")
                            gameOver = True
                            winner = Player1
                        else:
                            turn = not turn
                            print(Player2 + " make your move")
                    else:
                        error.play()
                        print('Out of bounds')

                playBoard = cutBoard(board)
                drawBoard(playBoard)
                pygame.display.update()

        # Player 2
        if turn == True and gameOver == False:
            column, minimaxScore = minimax(board, 4, -math.inf, math.inf, True)
            if columnNotFull(board, column) == True and correctDistance(board, column) == True:
                row = nextOpenRow(board, column)
                placePiece(board, row, column, 2)
                print(board)
                if checkWin(board, 2) == True:
                    print(Player2 + " wins!")
                    gameOver = True
                    winner = Player2
                else:
                    turn = not turn
                    print(Player1 + " make your move")
            else:
                print('Out of bounds')

            playBoard = cutBoard(board)
            drawBoard(playBoard)
            pygame.display.update()

        if gameOver == True:
            correct.play()
            displayText(winner + ' wins!', smallFont, black, (width / 2, height / 2))
            reset()
            pygame.display.update()
            pygame.time.wait(4000)

    playSong1()

start()