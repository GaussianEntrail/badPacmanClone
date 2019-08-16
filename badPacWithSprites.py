import numpy, random, pyglet
from pyglet.window import mouse, key
import pyglet.graphics

WINDOW_WIDTH, WINDOW_HEIGHT = 640, 480
CELL_WIDTH, CELL_HEIGHT = 16, 16
CURSOR_X, CURSOR_Y = 0, 0
TIME_CONST = 60
window = pyglet.window.Window(width = WINDOW_WIDTH, height = WINDOW_HEIGHT)

#TEST_MAP = [line.rstrip('\n') for line in open("D:\\Python36_projects\\test_map.txt","r")]

#load some sprites
wallSprite = pyglet.image.load("resources//kabe.bmp")
ghostSprite = pyglet.image.load("resources//oni.bmp")
playerSprite = pyglet.image.load("resources//akuma.bmp")
coinSprite = pyglet.image.load("resources//kane.bmp")

characterSpritesBatch = pyglet.graphics.Batch()
objectSpritesBatch = pyglet.graphics.Batch()

def distance(x1,y1,x2,y2, dist_euclid = True):
    if dist_euclid:
        #actually returns square of distance
        return (y2-y1)**2 + (x2-x1)**2
    else:
        return abs(y2-y1) + abs(x2-x1)

def draw_mouse(x,y):
    #DRAW CURSOR
    X1,Y1 = x * CELL_WIDTH,  y * CELL_HEIGHT,
    X2,Y2 = X1 + CELL_WIDTH,Y1 + CELL_HEIGHT
    pyglet.graphics.draw(8 ,pyglet.gl.GL_LINES, ('v2i',[X1,Y1, X2,Y1,  X2,Y1, X2,Y2,  X1,Y2, X2,Y2,  X1,Y1, X1,Y2] ), ('c3B', (255,255,255)* 8 ) )

class GameModes:
    GameRunning = 0
    GamePaused = 1
    GhostCaughtYou = 2
    
gameMode = GameModes.GameRunning
gameScore = 0
  
  
class Node:
    def __init__ (self,x,y):
        self.x, self.y = x,y
    
class Maze:
    """
    I'm not sure how to give credit for things on GitHub, but basically I adapted this maze generator algorithm from 
    https://github.com/oppenheimj/maze-generator/blob/master/MazeGenerator.java
    
    so big thanks to oppenheimj for putting it up
    """
    def __init__(self, width = WINDOW_WIDTH//CELL_WIDTH, height = (WINDOW_HEIGHT//CELL_HEIGHT) -1):
        self.stack = []
        self.height = height
        self.width = width
        self.maze = numpy.ones((height,width), dtype = int)
        
        #self.vertex_list = pyglet.graphics.vertex_list(self.width * self.height, 'v2i', 'c3B')
        self.maze_batch = pyglet.graphics.Batch()
        self.sprites = []
        self.generateMaze()
           
    def generateMaze(self):
        self.stack.append( Node(1,1) )
        while self.stack:
            next = self.stack.pop()
            if self.validNextNode(next):
                self.maze[next.y][next.x] = 0
                neighbors = self.findNeighbors(next)
                self.randomlyAddNodesToStack(neighbors)
            
        #Maybe also do the addition of polygons to batches here too?
        #What if I were to use sprites instead?
        for x,y in [ (x,y) for x in range(self.width) for y in range(self.height) if self.maze[y][x] ]:
            #X1, Y1, X2, Y2 = self.getCoordRect(x,y)
            #self.maze_batch.add( 4 ,pyglet.gl.GL_QUADS, None, ('v2i', [ X1,Y1, X2,Y1, X2,Y2, X1,Y2 ] ), ('c3B', (0,255,0) * 4 ) )  
            X, Y = x * CELL_WIDTH, y * CELL_HEIGHT
            wall = pyglet.sprite.Sprite(wallSprite, X, Y, batch = self.maze_batch)
            wall.color = (128,255,0)
            self.sprites.append(wall)
                            
    def validNextNode(self, node):
        numNeighboringOnes = 0
        coords = [(node.x-1,node.y-1),(node.x-1,node.y),(node.x-1,node.y+1), (node.x,node.y-1) ,(node.x,node.y+1), (node.x+1,node.y-1),(node.x+1,node.y),(node.x+1,node.y+1)]
        numNeighboringOnes = sum([1 for x,y in coords if self.pointOnGrid(x, y) and self.maze[y][x]==0])
        return numNeighboringOnes in (0,1,2,3) and not self.maze[node.y][node.x] == 0
    
    def randomlyAddNodesToStack(self, nodes):
        random.shuffle(nodes)
        self.stack += nodes #for node in nodes: self.stack.append(node)
        
    def findNeighbors(self, node):
        coords = [(node.x-1,node.y-1),(node.x-1,node.y),(node.x-1,node.y+1), (node.x,node.y-1) ,(node.x,node.y+1), (node.x+1,node.y-1),(node.x+1,node.y),(node.x+1,node.y+1)]
        neighbors = [Node(x,y) for x,y in coords if self.pointOnGrid(x, y) and self.pointNotCorner(node, x, y)]
        return neighbors
    
    def pointOnGrid(self, x, y):
        return x in range(1, self.width-1) and y in range(1, self.height-1)
    
    def pointNotCorner(self, node, x, y):
        return x == node.x or y == node.y
    
    def pointNotNode(self,node,x,y):
        return not (x,y) == (node.x, node.y)
    
    def printMaze(self):
        maze_string = ""
        for row in self.maze:
            maze_string += "".join(["#","."][col] for col in row)
            maze_string += "\n"
        
        print(maze_string)
    
    def checkCellOpen(self,x,y):
        #Check if a particular cell is open/free
        if x in range(self.width) and y in range(self.height):
            return self.maze[y][x] == 0
                
        return False
        
    def lineOfSight(self,x1,y1,x2,y2):
        #Check if you can "see" a particular cell from another cell
        can_see = False
        start_x, end_x = (x1, x2) if x2 > x1 else (x2, x1)
        start_y, end_y = (y1, y2) if y2 > y1 else (y2, y1)
        d = numpy.sqrt( distance(start_x, start_y, end_x, end_y) )
        
        
        return can_see
    
    def getListPositionsOpen(self):
        return [(x,y) for y in range(self.height) for x in range(self.width) if self.maze[y][x] == 0]
        
    def getRandomOpenPositionInRange(self,x,y,r):
        openPositions = self.getListPositionsOpen()
        xrange, yrange = range(x-r,x+r), range(y-r,y+r)
        return random.choice( [(x,y) for x,y in openPositions if x in xrange and y in yrange] )

    def getCoordRect(self,x,y):
        #returns the rect
        if x in range(self.width) and y in range(self.height):
            return [x * CELL_WIDTH, y * CELL_HEIGHT, (x * CELL_WIDTH) + CELL_WIDTH, (y * CELL_WIDTH) + CELL_HEIGHT]
                
        return [0, 0, CELL_WIDTH, CELL_HEIGHT]
    
    def draw(self):
        self.maze_batch.draw()
        '''
        for y in range(self.height):
            for x in range(self.width): 
                currentCell = self.maze[y][x]
                if currentCell == 1:
                    X1,Y1 = x * CELL_WIDTH, y * CELL_HEIGHT,
                    X2,Y2 = X1 + CELL_WIDTH,Y1 + CELL_HEIGHT
                    pyglet.graphics.draw(4 ,pyglet.gl.GL_QUADS, ('v2i',[X1,Y1, X2,Y1, X2,Y2, X1,Y2] ), ('c3B', (0,255,0) * 4 ) )    
        '''
          
class GhostAIType:
    CHASING = 0
    WANDERING = 1
    FLEEING = 2
    FLANKING = 3
    PATROLLING = 4
   
#At some point, I will make these sprite objects and add them to a batch
class Ghost (pyglet.sprite.Sprite):
    def __init__(self, X = 1, Y = 1, TARGET_X = 22, TARGET_Y = 9, color = (255,0,0), speed = 2/TIME_CONST, state = GhostAIType.PATROLLING, batch = None):
        super().__init__(ghostSprite, x = X * CELL_WIDTH, y = Y * CELL_HEIGHT, batch = batch)
        
        self.START_X, self.START_Y = X, Y
        self.X, self.Y = X, Y
        self.PREV_X, self.PREV_Y = X,Y
        self.TARGET_X, self.TARGET_Y = TARGET_X, TARGET_Y
        self.color = color
        self.trailcolor = tuple([c//2 for c in color])
        self.speed = speed
        self.timer = 0
        
        if not state:
            self.states = (GhostAIType.CHASING, GhostAIType.WANDERING, GhostAIType.FLEEING, GhostAIType.FLANKING, GhostAIType.PATROLLING)
            self.state = random.choice(self.states)
        else:
            self.state = state
           
    def setTarget(self,TARGET_X,TARGET_Y):
        self.TARGET_X, self.TARGET_Y = TARGET_X, TARGET_Y
        
    def move(self,DX,DY):
        #Move in a particular direction
        self.PREV_X, self.PREV_Y = self.X, self.Y
        self.X, self.Y = self.X+DX, self.Y+DY 
        self.x,self.y = self.X * CELL_WIDTH, self.Y * CELL_HEIGHT
      
    def pickDirectionRandom(self, map):
        #test method
        directions = [(1,0), (0,1), (-1,0), (0,-1)] #List of directions: Right, Up, Left, Down
        open_cells = [map.checkCellOpen(self.X + DX, self.Y + DY) for DX, DY in directions] #Check if each neighboring cell is open
        #directions that can be moved in
        valid_directions_noreturn_indexes = [d for d in (0,1,2,3) if open_cells[d] and not (self.X + directions[d][0], self.Y + directions[d][1]) == (self.PREV_X, self.PREV_Y)]
        #allow moving back into previous space ONLY if there's no way to move forward
        valid_directions_indexes = [d for d in (0,1,2,3) if open_cells[d]]
        
        #if there's nowhere to go, then don't move
        if not valid_directions_noreturn_indexes and not valid_directions_indexes: return (0,0)
       
        #if there's only one way to go then go there
        if len(valid_directions_noreturn_indexes) == 1: return directions[valid_directions_noreturn_indexes[0]]
        
        if not valid_directions_noreturn_indexes and len(valid_directions_indexes) == 1: return directions[valid_directions_indexes[0]]
              
        #If there's more than one direction you can pick from, pick one        
        if valid_directions_noreturn_indexes: return directions[random.choice(valid_directions_noreturn_indexes)]
        
        if valid_directions_indexes: return directions[random.choice(valid_directions_indexes)]
        
        #don't move 
        return (0,0)

    def pickDirectionGreedy(self, map):
        #If you're already at the target, you're done!
        #If there's no map you're screwed
        if self.isAtTarget() or map==None: return (0,0)
        #List of directions: Right, Up, Left, Down
        directions = [(1,0), (0,1), (-1,0), (0,-1)] 
        #Check if each neighboring cell is open
        open_cells = [map.checkCellOpen(self.X + DX, self.Y + DY) for DX, DY in directions] 
        #Distance of each neighboring cell from the target cell
        distances = [distance(self.X + DX, self.Y + DY, self.TARGET_X, self.TARGET_Y) for DX, DY in directions]
        #directions that are "open" (can be moved into) without walking into a previous space
        valid_directions_noreturn_indexes = [d for d in (0,1,2,3) if open_cells[d] and not (self.X + directions[d][0], self.Y + directions[d][1]) == (self.PREV_X, self.PREV_Y)]
        #allow moving back into previous space ONLY if there's no way to move forward otherwise
        valid_directions_indexes = [d for d in (0,1,2,3) if open_cells[d]]
        #if there's only one way to go then go there
        if len(valid_directions_noreturn_indexes) == 1: return directions[valid_directions_noreturn_indexes[0]]
        if not valid_directions_noreturn_indexes and len(valid_directions_indexes) == 1: return directions[valid_directions_indexes[0]]      
        #If there's more than one direction you can pick from, pick the one that's gonna minimize your distance to your target
        i1, d_min= -1, 99999
        if valid_directions_noreturn_indexes:
            for dir in valid_directions_noreturn_indexes:
                if distances[dir] <= d_min: i1, d_min = dir, distances[dir]
                
            
        i2, d_min = -1, 99999
        if valid_directions_indexes:
            for dir in valid_directions_indexes:
                if distances[dir] <= d_min: i2, d_min = dir, distances[dir]
            
        
        if not i1 == -1: return directions[i1]
        else:
            if not i2 == -1: return directions[i2]
            else:
                return (0,0)
            
                
        return (0,0)
       
    def distanceToTarget(self):
        return distance(self.X, self.Y, self.TARGET_X, self.TARGET_Y)
    
    def isAtTarget(self):
        return (self.X,self.Y) == (self.TARGET_X,self.TARGET_Y)
    
    def step(self,map,t,player):
        def caughtPlayer(player):
            return (self.X, self.Y) == (player.X, player.Y)

        def pickTarget(map,player):
            if self.state == GhostAIType.CHASING: 
                self.setTarget(player.X, player.Y)  
            if self.state == GhostAIType.FLEEING: 
                self.setTarget(self.START_X, self.START_Y)   
            if self.state == GhostAIType.FLANKING:
                X, Y = player.X + (player.VX * 4), player.Y + (player.VY * 4)
                self.setTarget(X,Y)
            if self.state == GhostAIType.PATROLLING or self.state == GhostAIType.WANDERING:
                X, Y = random.choice(map.getListPositionsOpen())
                self.setTarget(X,Y)
    
        def pickDirection(map,player):
            dx,dy = 0,0
            if self.state in (GhostAIType.CHASING, GhostAIType.FLEEING, GhostAIType.FLANKING, GhostAIType.PATROLLING):  
                dx, dy = self.pickDirectionGreedy(map)
            else:
                dx, dy = self.pickDirectionRandom(map)
            
            return dx, dy 
            
        self.timer += t
        if self.timer >= self.speed: 
            if self.isAtTarget() or random.random() > 0.7: pickTarget(map, player) #Pick a new target once you've reached your target, hopefully
            dx, dy = pickDirection(map,player)
            self.move(dx,dy)
            self.timer -= self.speed
        
        if caughtPlayer(player): pass
                   
    def hasntMoved(self):
        return (self.X, self.Y) == (self.PREV_X, self.PREV_Y)
    
    '''
    def draw(self):
        #Draw self
        X1,Y1 = self.X * CELL_WIDTH, self.Y * CELL_HEIGHT
        X2,Y2 = X1 + CELL_WIDTH,Y1 + CELL_HEIGHT
        pyglet.graphics.draw(4 ,pyglet.gl.GL_POLYGON, ('v2i',[X1,Y1, X2,Y1, X2,Y2, X1,Y2] ), ('c3B', self.color * 4 ) )
        
        #Draw a trail
        if not self.hasntMoved():
            X1,Y1 = self.PREV_X * CELL_WIDTH, self.PREV_Y * CELL_HEIGHT
            X2,Y2 = X1 + CELL_WIDTH,Y1 + CELL_HEIGHT
            pyglet.graphics.draw(4 ,pyglet.gl.GL_POLYGON, ('v2i',[X1,Y1, X2,Y1, X2,Y2, X1,Y2] ), ('c3B', self.trailcolor * 4 ) )    
        
        #Draw target
        if not self.isAtTarget():
            X1,Y1 = self.TARGET_X * CELL_WIDTH, self.TARGET_Y * CELL_HEIGHT
            X2,Y2 = X1 + CELL_WIDTH,Y1 + CELL_HEIGHT
            pyglet.graphics.draw(4 ,pyglet.gl.GL_POLYGON, ('v2i',[X1,Y1, X2,Y1, X2,Y2, X1,Y2] ), ('c3B', (255,255,0) * 4 ) )
    '''
class PlayerObject(pyglet.sprite.Sprite):
    def __init__(self, X = 1, Y = 1, speed = 1/TIME_CONST, color = (255,255,0), batch = None):
        super().__init__(playerSprite, x = X * CELL_WIDTH, y = Y * CELL_HEIGHT, batch = batch)
        self.X, self.Y = X, Y
        self.PREV_X, self.PREV_Y = X, Y
        self.VX, self.VY = 0,0
        self.timer = 0
        self.speed = speed
        self.color = color
        self.trailcolor = tuple([x//2 for x in color])    
        
    def step(self, map, t, coins = None):
        if self.timer < self.speed:
            self.timer += t
        else:
            self.move(self.VX, self.VY, map, coins)
            self.timer -= self.speed
        
    def move(self, DX, DY, map, coins = None):
        #Move in a particular direction
        if map.checkCellOpen(self.X+self.VX, self.Y+self.VY): 
            self.PREV_X, self.PREV_Y = self.X, self.Y
            self.X, self.Y = self.X+self.VX, self.Y+self.VY
                
        if coins:
            #collect coins
            coins.collect(self.X, self.Y) 
            
            
                
        self.x, self.y = self.X * CELL_WIDTH, self.Y * CELL_HEIGHT
        
    def on_key_press(self,symbol,map):
        if symbol in (key.W, key.UP):
            #Move up
            self.VX, self.VY = 0, 1
        elif symbol in (key.D, key.RIGHT):
            #Move right
            self.VX, self.VY = 1, 0
        elif symbol in (key.A, key.LEFT):
            #Move left
            self.VX, self.VY = -1, 0
        elif symbol in (key.S, key.DOWN):
            #Move down
            self.VX, self.VY = 0,-1

    def on_key_release(self, symbol, map):
        if symbol in (key.W, key.S, key.UP, key.DOWN): self.VY = 0 #Cease vertical movement
        if symbol in (key.D, key.A, key.LEFT, key.RIGHT): self.VX = 0 #Cease horizontal movement
      
    def hasntMoved(self):
        return (self.X, self.Y) == (self.PREV_X, self.PREV_Y)    
    
    '''
    def draw(self): 
        #Draw self
        X1,Y1 = self.X * CELL_WIDTH, self.Y * CELL_HEIGHT
        X2,Y2 = X1 + CELL_WIDTH,Y1 + CELL_HEIGHT
        pyglet.graphics.draw(4 ,pyglet.gl.GL_POLYGON, ('v2i',[X1,Y1, X2,Y1, X2,Y2, X1,Y2] ), ('c3B', self.color * 4 ) )
        
        #Draw a trail
        if not self.hasntMoved():
            X1,Y1 = self.PREV_X * CELL_WIDTH, self.PREV_Y * CELL_HEIGHT
            X2,Y2 = X1 + CELL_WIDTH,Y1 + CELL_HEIGHT
            pyglet.graphics.draw(4 ,pyglet.gl.GL_POLYGON, ('v2i',[X1,Y1, X2,Y1, X2,Y2, X1,Y2] ), ('c3B', self.trailcolor * 4 ) )   
        pass
    '''

#There should be some sort of collectible or something
class moneyObjectCollection():
    def __init__(self):
        #Contains a list of coins and their map positions
        self.coins = []
        self.coins_limit = 200
        
    def generateCoins(self, map, list_avoid_positions = None):
        valid_spaces_to_spawn_coins = map.getListPositionsOpen()
        if len(valid_spaces_to_spawn_coins) > self.coins_limit:
            spawnpoints = random.sample(valid_spaces_to_spawn_coins, self.coins_limit)
        else:
            spawnpoints = valid_spaces_to_spawn_coins
        
        random.shuffle(spawnpoints)
        
        for X,Y in spawnpoints:
            self.coins.append( moneyObject(X * CELL_WIDTH, Y * CELL_HEIGHT, batch = objectSpritesBatch) )
                        
    def checkCoin(self,x,y):
        return len([coin for coin in self.coins if (coin.x, coin.y) == (x, y)]) > 0
        
    def getCoinIndex(self,x,y):
        return [coin for coin in self.coins if (coin.x, coin.y) == (x * CELL_WIDTH, y * CELL_HEIGHT)]
    
    def isListEmpty(self):
        return len(self.coins) <= 0
    
    def collect(self, x, y):
        #Remove a coin from the list of coins in the map
        possible_coins = [coin for coin in self.coins if (coin.x, coin.y) == (x * CELL_WIDTH, y* CELL_HEIGHT)]
        if possible_coins:
            global gameScore
            for coin in possible_coins:
                coin.delete()
                self.coins.remove(coin)
                gameScore += 100
                        
class moneyObject(pyglet.sprite.Sprite):
    def __init__(self, x, y, batch = None):
        super().__init__(coinSprite, x, y, batch = batch)
        self.colors = ( (255,128,128),(255,255,128),(128,255,128),(128,255,255),(128,128,255),(255,128,255) )
        self.changeColor()
        
    def changeColor(self):
        self.color = random.choice(self.colors)
        


#Create the game map
MAP = Maze(width = WINDOW_WIDTH//CELL_WIDTH, height = (WINDOW_HEIGHT//CELL_HEIGHT) -1 )
#Spawn the player in an open space in the center of the maze
px, py = MAP.getRandomOpenPositionInRange(MAP.width//2, MAP.height//2, 3) #pickFreeSpaceInRange(MAP.width//2, MAP.height//2, list_open, 4)
PLAYER = PlayerObject(X= px, Y= py, speed = 1/TIME_CONST, color = (255,255,0), batch = characterSpritesBatch)

#Spawn the ghosts in the corners
GHOSTS = []
colors_corners_states = (
    ((128,0,255), (1,1), GhostAIType.FLANKING),
    ((255,128,0), (MAP.width-2,1), GhostAIType.WANDERING),
    ((0,255,128), (1,MAP.height-2), GhostAIType.PATROLLING),
    ((255,0,128), (MAP.width-2,MAP.height-2), GhostAIType.CHASING) )
for color, corner, state in colors_corners_states:
    gx, gy = MAP.getRandomOpenPositionInRange(corner[0], corner[1], 3)
    GHOSTS.append( Ghost(X= gx, Y=gy, TARGET_X = px, TARGET_Y = py, color = color, speed = 6/TIME_CONST, state = state, batch = characterSpritesBatch) )

#Spawn coins
MONEY = moneyObjectCollection()
MONEY.generateCoins(MAP)

#GUI elements?
GameFont = pyglet.font.load("Terminal", 10)
GamePausedLabel = pyglet.font.Text(GameFont, x = 8, y = WINDOW_HEIGHT - 15, text = "PAUSED")
GameScoreLabel = pyglet.font.Text(GameFont, x = WINDOW_WIDTH - 128, y = WINDOW_HEIGHT - 15, text = "SCORE: " + str(gameScore) )


@window.event
def on_draw():
    window.clear()
    MAP.draw()
    #COINS/POWERUPS
    objectSpritesBatch.draw()
    #GHOST/PLAYER
    characterSpritesBatch.draw()
    draw_mouse(CURSOR_X, CURSOR_Y)
    
    global gameMode
    if gameMode == GameModes.GamePaused:
        GamePausedLabel.draw()
    
    if gameMode == GameModes.GameRunning:
        GameScoreLabel.draw()
        


@window.event
def on_key_release(symbol, modifiers):
    PLAYER.on_key_release(symbol, MAP)
    
@window.event
def on_key_press(symbol, modifiers):
    global gameMode
    if gameMode == GameModes.GameRunning:
        if symbol == key.P: gameMode = GameModes.GamePaused
    
        PLAYER.on_key_press(symbol, MAP)
    else:
        if symbol == key.P: gameMode = GameModes.GameRunning
            
@window.event
def on_mouse_motion(x,y,dx,dy):
    global CURSOR_X, CURSOR_Y
    CURSOR_X, CURSOR_Y = x // CELL_WIDTH, y // CELL_HEIGHT
    
@window.event        
def on_mouse_press(x, y, button, modifiers):
    pass
    '''
    if button == mouse.LEFT:
        if MAP.checkCellOpen(CURSOR_X, CURSOR_Y):
            for GHOST in GHOSTS: GHOST.setTarget(CURSOR_X, CURSOR_Y)
    '''
           
      
def update(t):
    global gameMode, gameScore, GameScoreLabel
    
    GameScoreLabel.text = "SCORE: "+str(gameScore)
    if gameMode == GameModes.GameRunning:
        PLAYER.step(MAP, t, MONEY)
        for GHOST in GHOSTS: GHOST.step(MAP,t,PLAYER)
        
    pass
    
pyglet.clock.schedule_interval(update, 1/TIME_CONST)
pyglet.app.run()
