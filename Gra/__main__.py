#-------------BIBLIOTEKI-------------
import os                                                       #systemowe rzeczy
import time                                                     #czas
import math                                                     #krolowa nauk
import random                                                   #losowosc
import colorama                                                 #|kolorki
from colorama import *                                          #|
colorama.init()                                                 #|
import console_cursor                                           #ustawienia kursora
import uniqueTexts as texts                                     #customowe napisy
from pynput.keyboard import Key, Listener                       #wykrywanie klawiatury, poruszanie sie
InstructionFile = open("InstructionFile.txt", encoding="utf8")  #tekst z intrukcją
from SymbolsDictionaryFile import SymbolsDictionary as symDict  #słownik z grafiką
#--------------WARTOSCI--------------
#---ustawienia---
GAME_TIME = 0.07 #resetuje mape w sekundach
MAP_SIZE_X = 50
MAP_SIZE_Y = 50
minROOM_SIZE_X = 7
minROOM_SIZE_Y = 7
maxROOM_SIZE_X = 11
maxROOM_SIZE_Y = 11
ROOM_NUMBER = 11#11
ROOM_SPACING = 2

game_on = 0
#------mapa------
board = []
rooms = [] 
numeredRooms = []
resetNumber = 0
#-----gracz-----
plrX = 0
plrY = 0

press_key = 0
canMove = True
visitedNodes = []
inRoom = 0
inFight = False
projectiles = []
enemies = []
#-----inne------
consolei = 0
health = 3
score = 0
#---------------FUNKCJE---------------
#sprawdza czy w danym polozeniu moze znajdowac sie pokoj( czy nie zawadza o inne pokoje)
def CanRoomPlace(sizeX, sizeY, posX, posY):
    global board
    for x in range(posX - ROOM_SPACING, posX+sizeX + ROOM_SPACING):
        for y in range(posY - ROOM_SPACING, posY+sizeY + ROOM_SPACING):
            if board[x][y][0] != 0:
                return False
    return True

# numeruje pokoje w kolejnosci
def NumerRooms():
    global rooms, numeredRooms,board
    roomNum = 0
    while len(rooms) > 0:
        select = rooms[0]
        for room in rooms:
            if room[1] < select[1]:
                select = room
        rooms.remove(select)
        if select[4] == "startRoom":
            board[select[0]][select[1]] = [str(roomNum),Fore.LIGHTRED_EX, False]
        else:
            board[select[0]][select[1]] = [str(roomNum),Fore.WHITE, False]
        faces = {}
        center1 = [select[0] + select[2]//2, select[1] + select[3]//2]
        leftJoin = [center1[0], center1[1] - math.floor( select[3]/2 ) -2, False]; faces["left"] = leftJoin ;      #board[leftJoin[0]][leftJoin[1] + 1] = " ← "
        rightJoin = [center1[0], center1[1] + math.ceil( select[3]/2 ) + 1, False]; faces["right"] = rightJoin ;   #board[rightJoin[0]][rightJoin[1] - 1] = " → "
        topJoin = [center1[0] - math.floor( select[2]/2 ) - 2, center1[1],False]; faces["top"] = topJoin ;        #board[topJoin[0] + 1][topJoin[1]] = " ↑ "
        downJoin = [center1[0] + math.ceil( select[2]/2 ) + 1, center1[1],False]; faces["down"] = downJoin ;      #board[downJoin[0] - 1][downJoin[1]] = " ↓ "
        
        newRoom = {
            "posX" : select[0],
            "posY" : select[1],
            "sizeX": select[2],
            "sizeY": select[3],
            "faces": faces,
            "connectedRooms": [],
            "connecterCorridors": [],
            "roomType": select[4],
            "visited" : False
        }

        if newRoom["roomType"] == "healthRoom":
            board[newRoom["posX"] + newRoom["sizeX"]//2][newRoom["posY"] + newRoom["sizeY"]//2] = [12, Fore.LIGHTRED_EX, False]
            board[newRoom["posX"] + newRoom["sizeX"]//2][newRoom["posY"] + newRoom["sizeY"]//2 - 1] = [12, Fore.LIGHTRED_EX, False]
            board[newRoom["posX"] + newRoom["sizeX"]//2][newRoom["posY"] + newRoom["sizeY"]//2 + 1] = [12, Fore.LIGHTRED_EX, False]

        numeredRooms.append(newRoom)

        roomNum += 1


#korytarze
gridPoints = []
pointB = 0
def Pathfinding_AddPoint(x, y, point):
    global gridPoints, board
    newPoint = [x, y, point, board[x][y][0]]
    for enemy in enemies:
        if enemy[0] == newPoint[0] and enemy[1] == newPoint[1]:
            return False#Stoi tu przeciwnik
    if newPoint in gridPoints:
        return False#juz uzyty

    board[newPoint[0]][newPoint[1]][0] = " x "
    if newPoint[0] == pointB[0] and newPoint[1] == pointB[1]:
        return newPoint
    gridPoints.append(newPoint)
    return False 

def Pathfinding(pointA, _pointB, enemy = False): # punkt - [posX, posY, elder, lastState]
    global gridPoints, pointB, board
    pointB = _pointB
    path = [pointA]
    gridPoints = [pointA]
    for point in gridPoints:
        if point[0] - 1 >= 0:
            if board[point[0] - 1][point[1]][0] == 0 or board[point[0] - 1][point[1]][0] == 10 or(enemy and board[point[0] - 1][point[1]][0] == 11):
                ret = Pathfinding_AddPoint(point[0] - 1, point[1], point)
                if ret != False:
                    pointB = ret
                    break
        if point[0] + 1 < MAP_SIZE_X:
            if board[point[0] + 1][point[1]][0] == 0 or board[point[0] + 1][point[1]][0] == 10 or(enemy and board[point[0] + 1][point[1]][0] == 11):
                ret = Pathfinding_AddPoint(point[0] + 1, point[1], point)
                if ret != False:
                    pointB = ret
                    break
        if point[1] - 1 >= 0:
            if board[point[0]][point[1] - 1][0] == 0 or board[point[0]][point[1] - 1][0] == 10 or(enemy and board[point[0]][point[1] - 1][0] == 11):
                ret = Pathfinding_AddPoint(point[0], point[1] - 1, point)
                if ret != False:
                    pointB = ret
                    break
        if point[1] + 1 < MAP_SIZE_Y:
            if board[point[0]][point[1] + 1][0] == 0 or board[point[0]][point[1] + 1][0] == 10 or(enemy and board[point[0]][point[1] + 1][0] == 11):
                ret = Pathfinding_AddPoint(point[0], point[1] + 1, point)
                if ret != False:
                    pointB = ret
                    break
    for point in gridPoints:
         board[point[0]][point[1]][0] = point[3]
    while pointB[2] != 0:
        path.append([pointB[0],pointB[1]])
        pointB = pointB[2]
    return path
    
def Corridors():
    global numeredRooms,board
    #korytarze
    for i in range(len( numeredRooms ) - 1):
        select = numeredRooms[i]
        nearestRoom = numeredRooms[i+1]
        selectJoin = select["faces"]["left"]
        nearestJoin = nearestRoom["faces"]["left"]
        sName = "left"
        nName = "left"
        for sJ in select["faces"]:
            for nJ in nearestRoom["faces"]:
                a = abs(select["faces"][sJ][0] - nearestRoom["faces"][nJ][0])
                b = abs(select["faces"][sJ][1] - nearestRoom["faces"][nJ][1])
                a2 = abs(selectJoin[0] - nearestJoin[0])
                b2 = abs(selectJoin[1] - nearestJoin[1])
                if a*a + b*b < a2* a2 + b2*b2:
                    selectJoin = select["faces"][sJ]
                    nearestJoin = nearestRoom["faces"][nJ]
                    sName = sJ
                    nName = nJ

        nearestRoom["connectedRooms"].append(select)
        select["connectedRooms"].append(nearestRoom)

        sX = 0; sY = 0; nX = 0; nY = 0
        select["faces"][sName][2] = True
        nearestRoom["faces"][nName][2] = True
        if sName == "left": sY = 1
        elif sName == "right": sY = -1
        elif sName == "top": sX = 1
        elif sName == "down": sX = -1

        if nName == "left": nY = 1
        elif nName == "right": nY = -1
        elif nName == "top": nX = 1
        elif nName == "down": nX = -1
        select["connecterCorridors"].append([nearestJoin[0] + nX, nearestJoin[1] + nY])
        select["connecterCorridors"].append([selectJoin[0] + sX, selectJoin[1] + sY])
        nearestRoom["connecterCorridors"].append([nearestJoin[0] + nX, nearestJoin[1] + nY])
        nearestRoom["connecterCorridors"].append([selectJoin[0] + sX, selectJoin[1] + sY])

        path = Pathfinding([selectJoin[0], selectJoin[1], 0, 0],[nearestJoin[0], nearestJoin[1], 0])        
        for point in path:
            board[point[0]][point[1]] = [10,Fore.BLACK,False]
            select["connecterCorridors"].append([point[0], point[1]])
            nearestRoom["connecterCorridors"].append([point[0], point[1]])
        board[selectJoin[0] + sX][selectJoin[1] + sY] =   [10,Fore.BLACK,False]
        board[nearestJoin[0] + nX][nearestJoin[1] + nY] = [10,Fore.BLACK,False]

#tworzy sciany pokoi
def RoomWall(x,y, roomJoinColor, vis):
    top = False; down = False; right = False; left =False
    if board[x-1][y][0] in range(1,10): top=True
    if board[x+1][y][0] in range(1,10): down=True
    if board[x][y+1][0] in range(1,10): right=True
    if board[x][y-1][0] in range(1,10): left=True

    if   top  and left:  board[x][y] = [4,roomJoinColor,vis]
    elif top  and right: board[x][y] = [5,roomJoinColor,vis]
    elif down and left:  board[x][y] = [6,roomJoinColor,vis]
    elif down and right: board[x][y] = [7,roomJoinColor,vis]
    elif left and right: board[x][y] = [3,roomJoinColor,vis]
    elif top  and down:  board[x][y] = [2,roomJoinColor,vis]

    elif top  or down:   board[x][y] = [8,roomJoinColor,vis]
    elif left or right:  board[x][y] = [9,roomJoinColor,vis]

# Generowanie mapy
def Generate2DMap():
    global board, rooms, resetNumber, plrX, plrY
    board = [[[0,Fore.BLACK,False] for x in range(MAP_SIZE_Y)] for y in range(MAP_SIZE_Y)]
    rooms = []
    roomNum = 1
    for i in range(ROOM_NUMBER):
        placement = False
        tryCount = 0
        while not placement:
            tryCount += 1
            if tryCount >= 200: # brutforsowo troche ale dziala
                # print("resetuje mape")
                resetNumber +=1
                Generate2DMap()
                return
            sizeX = random.randint(minROOM_SIZE_X, maxROOM_SIZE_X)
            sizeY = random.randint(minROOM_SIZE_Y, maxROOM_SIZE_Y)

            posX = random.randint(ROOM_SPACING, MAP_SIZE_X - sizeX - ROOM_SPACING)
            posY = random.randint(ROOM_SPACING, MAP_SIZE_Y - sizeY - ROOM_SPACING)
            
            placement = CanRoomPlace(sizeX, sizeY, posX, posY)
            
        rooms.append([posX, posY, sizeX, sizeY, "normal"])
        for x in range(posX-1, posX+sizeX+1):
            for y in range(posY-1, posY+sizeY+1):
                board[x][y] = [1,Fore.LIGHTBLACK_EX,False]
        for x in range(posX, posX+sizeX):
            for y in range(posY, posY+sizeY):
                board[x][y] = [11,Fore.BLACK,False]
        if roomNum == 1:    # pokoj startowy
            plrX = posX + sizeX//2
            plrY = posY + sizeY//2
            rooms[roomNum-1][4] = "startRoom"
        elif roomNum == 2:  # pokoj z itemem
            rooms[roomNum-1][4] = "healthRoom"
        else:               # cala reszta
            rooms[roomNum-1][4] = "enemyRoom"

        roomNum += 1
    NumerRooms()
    Corridors()
    for room in numeredRooms:
        rj = Fore.LIGHTBLACK_EX
        if room["roomType"] == "healthRoom":
            rj = Fore.LIGHTRED_EX
        for x in range( room["posX"] - 1, room["posX"] + room["sizeX"] + 1 ):
            for y in range(room["posY"] -1, room["posY"] + room["sizeY"] + 1 ):
                if board[x][y][0] == 1:
                    RoomWall(x, y, rj, False)

# Spawni przeciwnikow
def SpawnEnemies(room, eNumber):
    global enemies
    for i in range(eNumber):
        rX = 0
        rY = 0
        while rX == 0:
            rX = random.randint(room["posX"] + 3, room["posX"] + room["sizeX"] - 3)
            rY = random.randint(room["posY"] + 3, room["posY"] + room["sizeY"] - 3)
            for en in enemies:
                if en[0] == rX and en[1] == rY:
                    rX = 0

        enemy = [rX, rY, 3]
        enemies.append(enemy)

def EnemyMove():
    for enemy in enemies:
        if enemy[0] == plrX and enemy[1] > plrY:
            projectiles.append([enemy[0], enemy[1], [0, -1], "leftAtack", 1])
        elif enemy[0] == plrX and enemy[1] < plrY:
            projectiles.append([enemy[0], enemy[1], [0, 1], "rightAtack", 1])
        elif enemy[0] > plrX and enemy[1] == plrY:
            projectiles.append([enemy[0], enemy[1], [-1, 0], "upAtack", 1])
        elif enemy[0] < plrX and enemy[1] == plrY:
            projectiles.append([enemy[0], enemy[1], [1, 0], "downAtack", 1])
        else:
            path = Pathfinding( [enemy[0], enemy[1], 0, 11], [plrX, plrY, 0, 11], True)
            for i in path:
                board[i[0]][i[1]] = [11,Fore.WHITE, True]
            enemy[0] = path[-1][0]
            enemy[1] = path[-1][1]
# Gdy przycisk klikniety
def on_press(key):
    global plrX, plrY, projectiles, canMove, press_key, shootDelay, game_on, health, board
    if game_on == 2:
        if canMove and 'char' in dir(key):
            canMove = False
            press_key = key
            if key.char == 'w'        and board[plrX - 1][plrY][0]   in range(10,15) and board[plrX - 1][plrY][2] == True: plrX -= 1
            elif key.char == 's'      and board[plrX + 1][plrY][0]   in range(10,15) and board[plrX + 1][plrY][2] == True: plrX += 1
            if key.char == 'a'        and board[plrX][plrY-1][0]     in range(10,15) and board[plrX][plrY - 1][2] == True:plrY -= 1
            elif key.char == 'd'      and board[plrX][plrY+1][0]     in range(10,15) and board[plrX][plrY + 1][2] == True:plrY += 1
            
        if key == Key.up        and board[plrX - 1][plrY][0]   == 11: projectiles.append([plrX, plrY,[-1,0], "upAtack", 0])
        elif key == Key.down    and board[plrX + 1][plrY][0]   == 11: projectiles.append([plrX, plrY,[1,0], "downAtack", 0])
        elif key == Key.left    and board[plrX][plrY-1][0]     == 11: projectiles.append([plrX, plrY,[0,-1], "leftAtack", 0])
        elif key == Key.right   and board[plrX][plrY+1][0]     == 11: projectiles.append([plrX, plrY,[0,1], "rightAtack", 0])

        if health < 3 and board[plrX][plrY][0] == 12:
            board[plrX][plrY][0] = 11
            health += 1
        if board[plrX][plrY][0] == 14:
            game_on = 3
    if game_on == 0 and key == Key.space:
        game_on = 1
    SearchRooms()

# Gdy przycisk wypuszczony
def on_release(key):
    global canMove, press_key
    if key == press_key and not canMove:
        canMove = True
        press_key = 0

# Wypisuje granice gry
def Print2DBorder():
    #tytul
    print()
    texts.PrintName(Fore.LIGHTBLACK_EX,Fore.LIGHTRED_EX)
    #ekran gry 
    print(Fore.LIGHTBLACK_EX + symDict["backgroundCornerRightDown"],symDict["backgroundVertical"] * (MAP_SIZE_Y-1),symDict["backgroundCornerLeftDown"],sep="", end="")
    for y in range(MAP_SIZE_Y):
        print(Fore.LIGHTBLACK_EX + "\n", symDict["backgroundHorizontal"], symDict["empty"] * MAP_SIZE_Y,symDict["backgroundHorizontal"],  sep="", end="")
    print(Fore.LIGHTBLACK_EX +  "\n", symDict["backgroundCornerRightUp"],symDict["backgroundVertical"] * (MAP_SIZE_Y-1),symDict["backgroundCornerLeftUp"],sep="")
    # ekran z opisem kontrolek
    console_cursor.setCursorAt(8,3*(MAP_SIZE_Y+1))
    print(Fore.LIGHTBLACK_EX + symDict["backgroundCornerRightDown"],symDict["backgroundVertical"] * 2," INSTRUKCJA ",symDict["backgroundVertical"] * 14,symDict["backgroundCornerLeftDown"],sep="", end="")
    for y in range(20):
        console_cursor.setCursorAt(9 + y,3*(MAP_SIZE_Y+1))
        print(Fore.LIGHTBLACK_EX + symDict["backgroundHorizontal"], symDict["empty"] * 21,symDict["backgroundHorizontal"],  sep="", end="")
    console_cursor.setCursorAt(29,3*(MAP_SIZE_Y+1))
    print(Fore.LIGHTBLACK_EX + symDict["backgroundCornerRightUp"],symDict["backgroundVertical"] * 20,symDict["backgroundCornerLeftUp"],sep="")
    #ekran z dialogami/eventami
    console_cursor.setCursorAt(30,3*(MAP_SIZE_Y+1))
    print(Fore.LIGHTBLACK_EX + symDict["backgroundCornerRightDown"],symDict["backgroundVertical"] * 2," KONSOLA ",symDict["backgroundVertical"] * 15,symDict["backgroundCornerLeftDown"],sep="", end="")
    for y in range(28):
        console_cursor.setCursorAt(31 + y,3*(MAP_SIZE_Y+1))
        print(Fore.LIGHTBLACK_EX + symDict["backgroundHorizontal"], symDict["empty"] * 21,symDict["backgroundHorizontal"],  sep="", end="")
    console_cursor.setCursorAt(59,3*(MAP_SIZE_Y+1))
    print(Fore.LIGHTBLACK_EX + symDict["backgroundCornerRightUp"],symDict["backgroundVertical"] * 20,symDict["backgroundCornerLeftUp"],sep="")

# Wypisuje instrukcje z pliku
def PrintInstrucions():
    lines = InstructionFile.readlines()
    i = 0
    for line in lines:
        console_cursor.setCursorAt(9 + i ,3*(MAP_SIZE_Y+1) + 1)
        print(Fore.WHITE + line)
        i+=1

# Wypisuje tekst w konsoli
def PrintInConsole(tekst, replace = False):
    global consolei
    n = len(tekst)
    if replace and consolei > 0: consolei -= 1
    for j in range(n//40+1):
        console_cursor.setCursorAt(31 + consolei ,3*(MAP_SIZE_Y+1) + 1)
        print(" "*60)
        console_cursor.setCursorAt(31 + consolei ,3*(MAP_SIZE_Y+1) + 1)
        print(tekst[j*60:(j+1)*60])
        consolei+=1
#ustawia pokoj z przeciwnikami
def SetEnemyRoom(room):
    global inFight
    inFight = True
    room["roomType"] = "cleared"
    for x in range(MAP_SIZE_X - 1):
        for y in range(MAP_SIZE_Y):
            board[x][y][2] = False
    for x in range(room["posX"] - 1, room["posX"] + room["sizeX"] + 1):
        for y in range(room["posY"] - 1,room["posY"] + room["sizeY"] + 1):
            board[x][y][2] = True
    for face in room["faces"]:
        sX = 0; sY = 0
        if face == "left": sY = 1
        elif face == "right": sY = -1
        elif face == "top": sX = 1
        elif face == "down": sX = -1
        board[room["faces"][face][0] + sX][room["faces"][face][1] + sY][0] = 1
        board[room["faces"][face][0] + sX][room["faces"][face][1] + sY][1] = Fore.LIGHTBLACK_EX
        RoomWall(room["faces"][face][0] + sX, room["faces"][face][1] + sY, Fore.LIGHTBLACK_EX, True)
    SpawnEnemies(room, random.randint(1,3))

#resetuje mape po pokonaniu przeciwnikow
def DeSetEnemyRoom(iRoom):
    for room in numeredRooms:
        if room["visited"] == True:
            for x in range(room["posX"] -1, room["posX"] + room["sizeX"] + 1 ):
                for y in range(room["posY"] - 1,room["posY"] + room["sizeY"] + 1 ):
                    board[x][y][2] = True
            for neighbour in room["connectedRooms"]:
                for x in range(neighbour["posX"] -1, neighbour["posX"] + neighbour["sizeX"] + 1 ):
                    for y in range(neighbour["posY"] - 1,neighbour["posY"] + neighbour["sizeY"] + 1 ):
                        board[x][y][2] = True
            for cor in room["connecterCorridors"]:
                board[cor[0]][cor[1]][2] = True
            for face in room["faces"]:
                if room["faces"][face][2] == False:
                    continue
                sX = 0; sY = 0
                if face == "left": sY = 1
                elif face == "right": sY = -1
                elif face == "top": sX = 1
                elif face == "down": sX = -1
                board[room["faces"][face][0] + sX][room["faces"][face][1] + sY] = [10,Fore.BLACK,True]
    board[iRoom["posX"]][iRoom["posY"]][1] = Fore.LIGHTRED_EX
# Sprawdza pokoj w ktorym stoi gracz
def SearchRooms():
    global inRoom, visitedNodes, board, numeredRooms

    if not [plrX, plrY] in visitedNodes:
        visitedNodes.append([plrX, plrY])
        for room in numeredRooms:
            if plrX in range(room["posX"], room["posX"] + room["sizeX"] ) and plrY in range(room["posY"],room["posY"] + room["sizeY"] ) and inRoom != room:
                inRoom = room
                room["visited"] = True
                if room["roomType"] == "enemyRoom":
                    SetEnemyRoom(room)
                else:
                    for x in range(room["posX"] - 1, room["posX"]+ room["sizeX"] + 1):
                        for y in range(room["posY"] - 1, room["posY"] + room["sizeY"] + 1):
                            board[x][y][2] = True
                    for cor in room["connecterCorridors"]:
                        board[cor[0]][cor[1]][2] = True

                    for nRoom in room["connectedRooms"]:
                        for x in range(nRoom["posX"] - 1, nRoom["posX"]+ nRoom["sizeX"] + 1):
                            for y in range(nRoom["posY"] - 1, nRoom["posY"] + nRoom["sizeY"] + 1):
                                board[x][y][2] = True
                return

def RefreshBoard(first = False):
    for x in range(MAP_SIZE_X):
        if first:
            PrintInConsole(Fore.WHITE +  "Wczytuje mape " + str((x+1)/MAP_SIZE_X * 100) + "%.", True)
            time.sleep(0.02)

        console_cursor.setCursorAt(x+9,2)
        for y in range(MAP_SIZE_Y):
            textType = board[x][y][0]
            frontColor = board[x][y][1]
            isVis = board[x][y][2]
            if x == plrX and y == plrY:
                back = Back.BLACK
                if textType == 10:
                    back = Back.LIGHTBLACK_EX
                print(back + Fore.LIGHTRED_EX + symDict["player"], end="")
                continue
            else:
                isProt = False
                for enemy in enemies:
                    if enemy[0] == x and enemy[1] == y:
                        print(Back.BLACK + Fore.RED + symDict["enemy"], end="")
                        isProt = True
                        break
                if isProt:
                    continue
                for projectile in projectiles:
                    if projectile[0] == x and projectile[1] == y:
                        color = Fore.LIGHTRED_EX
                        if projectile[4] == 1:
                            color = Fore.RED
                        print(Back.BLACK + color + symDict[projectile[3]], end="")
                        isProt = True
                        break
                if isProt:
                    continue

            if isVis:
                if textType == 0:    print( Back.BLACK + frontColor + symDict["empty"],               end="")
                elif textType == 1:  print( Back.BLACK + frontColor + symDict["solidWall"],           end="")
                elif textType == 2:  print( Back.BLACK + frontColor + symDict["roomVertical"],        end="")
                elif textType == 3:  print( Back.BLACK + frontColor + symDict["roomHorizontal"],      end="")
                elif textType == 4:  print( Back.BLACK + frontColor + symDict["roomCornerLeftUp"],    end="")
                elif textType == 5:  print( Back.BLACK + frontColor + symDict["roomCornerRightUp"],   end="")
                elif textType == 6:  print( Back.BLACK + frontColor + symDict["roomCornerLeftDown"],  end="")
                elif textType == 7:  print( Back.BLACK + frontColor + symDict["roomCornerRightDown"], end="")
                elif textType == 8:  print( Back.BLACK + frontColor + symDict["doorVertical"],        end="")
                elif textType == 9:  print( Back.BLACK + frontColor + symDict["doorHorizontal"],      end="")
                elif textType == 10: print( Back.LIGHTBLACK_EX + frontColor + symDict["corridor"],    end="")
                elif textType == 11: print( Back.BLACK +                      symDict["roomInside"],  end="")
                elif textType == 12: print( Back.BLACK + frontColor + symDict["health fruit"],        end="")
                elif textType == 13: print( Back.BLACK + frontColor + symDict["health point"],        end="")
                elif textType == 14: print( Back.BLACK + frontColor + symDict["nextFloor"],           end="")
                else:                print( Back.BLACK + frontColor         + textType.zfill(3),      end="")
            else:
                print(Back.BLACK + "   ", end="")

#--------------LADOWANIE GRY--------------
os.system("mode 800")                                           #maksymalizacja okna
os.system('cls')
Print2DBorder()
PrintInstrucions()
texts.PrintMenu(MAP_SIZE_X//2 ,60, Fore.LIGHTRED_EX, Fore.WHITE)
# testowe wywolanie PrintInConsole(Fore.WHITE + "Ktos mowi: " + Fore.LIGHTBLACK_EX + "Jakis tam tekst.")
#--------------GRANIE--------------
with Listener(on_press = on_press, on_release= on_release) as listener:
    eni = 5
    while True:
        if game_on == 2:
            eni+=1
            if eni >= 10:
                EnemyMove()
                eni = 0
            for prot in projectiles:
                if board[prot[0] + prot[2][0]][prot[1] + prot[2][1]][0] == 11:
                    prot[0] = prot[0] + prot[2][0]
                    prot[1] = prot[1] + prot[2][1]
                    if prot[4] == 0:
                        for enemy in enemies:
                            if prot[0] == enemy[0] and prot[1] == enemy[1]:
                                enemy[2] -= 1
                                if enemy[2] == 0:
                                    enemies.remove(enemy)
                                    score += 5
                                projectiles.remove(prot)
                                break
                    if prot[4] == 1:
                        if prot[0] == plrX and prot[1] == plrY:
                            PrintInConsole(Fore.RED + "Otrzymales obrazenia")
                            health -= 1
                            projectiles.remove(prot)
                            if score - 5>=0:
                                score -= 5
                            else: score = 0
                else:
                    projectiles.remove(prot)

            if inFight and len(enemies) == 0:
                PrintInConsole(Fore.LIGHTRED_EX + "Pokoj ukonczony")
                score += 10
                inFight = False
                DeSetEnemyRoom(inRoom)

                clearFloor = True
                for room in numeredRooms:
                    if room["roomType"] == "enemyRoom":
                        clearFloor = False
                if clearFloor:
                    board[inRoom["posX"] + inRoom["sizeX"]//2][inRoom["posY"] + inRoom["sizeY"]//2] = [14, Fore.WHITE, True]
            
            board[MAP_SIZE_X-1][1] = ["Hea",Fore.LIGHTRED_EX,True]
            board[MAP_SIZE_X-1][2] = ["lth",Fore.LIGHTRED_EX,True]
            board[MAP_SIZE_X-1][3] = [":  ",Fore.LIGHTRED_EX,True]
            for i in range(3):
                board[MAP_SIZE_X-1][4+i] = [0,Fore.LIGHTRED_EX ,True]
            for i in range(health):
                board[MAP_SIZE_X-1][4+i] = [13,Fore.LIGHTRED_EX ,True]

            board[MAP_SIZE_X-1][8] = ["Poi",Fore.LIGHTRED_EX,True]
            board[MAP_SIZE_X-1][9] = ["nts",Fore.LIGHTRED_EX,True]
            board[MAP_SIZE_X-1][10] = [":  ",Fore.LIGHTRED_EX,True]     
            for i in range(10):
                board[MAP_SIZE_X-1][11+i] = [0,Fore.LIGHTRED_EX ,True]
            for i in range(len(str(score))):
                board[MAP_SIZE_X-1][11+i] = [" " + str(score)[i] + " ",Fore.LIGHTRED_EX ,True]

            if health <= 0:#koniec gry
                for x in range(MAP_SIZE_X):
                    for y in range(MAP_SIZE_X):
                        board[x][y][2] = True
                RefreshBoard()
                texts.PrintEndGame(MAP_SIZE_X//2+3 ,38, Fore.LIGHTRED_EX, Fore.WHITE, score)
                game_on = 0
                continue

            RefreshBoard()
            time.sleep(GAME_TIME)
        elif game_on == 1:#zaczecie gry
            board = []
            rooms = [] 
            numeredRooms = []
            inFight = False
            enemies = []
            projectiles = []
            health = 3
            consolei = 0
            for y in range(28):
                console_cursor.setCursorAt(31 + y,3*(MAP_SIZE_Y+1))
                print(Fore.LIGHTBLACK_EX + symDict["backgroundHorizontal"], symDict["empty"] * 21,symDict["backgroundHorizontal"],  sep="", end="")
            GAME_TIME = 0.07
            Generate2DMap()
            SearchRooms()
            PrintInConsole(Fore.WHITE + "Generuje mape, przy generacji mapa byla resetowana " + str(resetNumber) + " razy.")
            RefreshBoard(True)  
            PrintInConsole(Fore.WHITE +  "Pomyslnie wczytano mape!")
            time.sleep(0.2)
            PrintInConsole("")
            PrintInConsole(Fore.LIGHTRED_EX + "Nie daj sie zabic i idz coraz dalej")
            time.sleep(0.2)
            PrintInConsole(Fore.LIGHTRED_EX + "Powodzenia podrozniku!")
            PrintInConsole("")
            game_on = 2
        elif game_on == 3:#kolejne pietro
            board = []
            rooms = [] 
            numeredRooms = []
            for y in range(28):
                console_cursor.setCursorAt(31 + y,3*(MAP_SIZE_Y+1))
                print(Fore.LIGHTBLACK_EX + symDict["backgroundHorizontal"], symDict["empty"] * 21,symDict["backgroundHorizontal"],  sep="", end="")
            consolei = 0
            Generate2DMap()
            SearchRooms()
            RefreshBoard(True)
            if GAME_TIME - 0.005 > 0:  
                GAME_TIME -= 0.005
            PrintInConsole(Fore.LIGHTRED_EX + "Przeszedles na kolejne pietro!")
            time.sleep(0.2)
            PrintInConsole(Fore.LIGHTRED_EX + "Teraz gra bedzie coraz szybsza")
            game_on = 2

    listener.join()