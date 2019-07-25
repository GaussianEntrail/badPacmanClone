import numpy, random, pyglet
from pyglet.window import mouse, key

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 640
CELL_WIDTH = 16
CELL_HEIGHT = 16
TIME_CONST = 60
window = pyglet.window.Window(width = WINDOW_WIDTH, height = WINDOW_HEIGHT)


TEST_MAP = [line.rstrip('\n') for line in open("D:\\Python36_projects\\test_map.txt","r")]

def distance(x1,y1,x2,y2):
    return (y2-y1)**2 + (x2-x1)**2

CURSOR_X, CURSOR_Y = 0,0
def draw_mouse(x,y):
    #DRAW CURSOR
    X1,Y1 = x * CELL_WIDTH,  y * CELL_HEIGHT,
    X2,Y2 = X1 + CELL_WIDTH,Y1 + CELL_HEIGHT
    pyglet.graphics.draw(8 ,pyglet.gl.GL_LINES, ('v2i',[X1,Y1, X2,Y1,  X2,Y1, X2,Y2,  X1,Y2, X2,Y2,  X1,Y1, X1,Y2] ), ('c3B', (255,255,255)* 8 ) )
        
class Node:
    def __init__ (self,x,y):
        self.x, self.y = x,y
    
class Maze:
    """
    I'm not sure how to give credit for things on GitHub, but basically I adapted this maze generator algorithm from 
    https://github.com/oppenheimj/maze-generator/blob/master/MazeGenerator.java
    
    so big thanks to oppenheimj for putting it up
    """
    def __init__(self, width = WINDOW_WIDTH//CELL_WIDTH, height = WINDOW_HEIGHT//CELL_HEIGHT):
        self.stack = []
        self.height = height
        self.width = width
        self.maze = numpy.zeros((height,width), dtype = int)
        self.generateMaze()
        
    def generateMaze(self):
        self.stack.append( Node(1,1) )
        while self.stack:
            next = self.stack.pop()
            if self.validNextNode(next):
                self.maze[next.y][next.x] = 1
                neighbors = self.findNeighbors(next)
                self.randomlyAddNodesToStack(neighbors)
            
        
        
        
    def validNextNode(self, node):
        numNeighboringOnes = 0
        coords = [(node.x-1,node.y-1),(node.x-1,node.y),(node.x-1,node.y+1), (node.x,node.y-1) ,(node.x,node.y+1), (node.x+1,node.y-1),(node.x+1,node.y),(node.x+1,node.y+1)]
        numNeighboringOnes = sum([1 for x,y in coords if self.pointOnGrid(x, y) and self.maze[y][x]==1])
        return numNeighboringOnes<3 and not self.maze[node.y][node.x] == 1
    
    def randomlyAddNodesToStack(self, nodes):
        random.shuffle(nodes)
        for node in nodes: self.stack.append(node)
        
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
    
    def check_cell_open(self,x,y):
        #Check if a particular cell is open/free
        if x in range(self.width) and y in range(self.height):
            return self.maze[y][x] == 1
                
        return False
    
    def draw(self):
        for y in range(self.height):
            for x in range(self.width): 
                currentCell = self.maze[y][x]
                if currentCell == 0:
                    X1,Y1 = x * CELL_WIDTH, y * CELL_HEIGHT,
                    X2,Y2 = X1 + CELL_WIDTH,Y1 + CELL_HEIGHT
                    pyglet.graphics.draw(4 ,pyglet.gl.GL_POLYGON, ('v2i',[X1,Y1, X2,Y1, X2,Y2, X1,Y2] ), ('c3B', (0,255,0) * 4 ) )
                
            
        
    
    
class Pathfinder:
    def __init__(self, X = 1, Y = 1, TARGET_X = 22, TARGET_Y = 9, color = (255,0,0), speed = 1/60 ):
        self.X, self.Y = X, Y
        self.PREV_X, self.PREV_Y = X,Y
        self.TARGET_X, self.TARGET_Y = TARGET_X, TARGET_Y
        self.color = color
        self.trailcolor = tuple([x//2 for x in color])
        self.speed = speed
        self.timer = 0
           
    def set_target(self,TARGET_X,TARGET_Y):
        self.TARGET_X, self.TARGET_Y = TARGET_X, TARGET_Y
        
    def move(self,DX,DY):
        #Move in a particular direction
        self.PREV_X, self.PREV_Y = self.X, self.Y
        self.X, self.Y = self.X+DX, self.Y+DY 
      
    def pick_direction_random(self, map):
        #test method
        directions = [(1,0), (0,1), (-1,0), (0,-1)] #List of directions: Right, Up, Left, Down
        open_cells = [map.check_cell_open(self.X + DX, self.Y + DY) for DX, DY in directions] #Check if each neighboring cell is open
        print("Right: "+str(open_cells[0])+" Up: "+str(open_cells[1])+" Left: "+str(open_cells[2]) + " Down: "+str(open_cells[3]))
        distances = [distance(self.X + DX, self.Y + DY, self.TARGET_X, self.TARGET_Y) for DX, DY in directions]
        print("Right: "+str(distances[0])+" Up: "+str(distances[1])+" Left: "+str(distances[2]) + " Down: "+str(distances[3]))
        
        #directions that can be moved in
        valid_directions_noreturn_indexes = [d for d in (0,1,2,3) if open_cells[d] and not (self.X + directions[d][0], self.Y + directions[d][1]) == (self.PREV_X, self.PREV_Y)]
        #allow moving back into previous space ONLY if there's no way to move forward
        valid_directions_indexes = [d for d in (0,1,2,3) if open_cells[d]]
        
        if valid_directions_noreturn_indexes:
            return directions[random.choice(valid_directions_noreturn_indexes)]
        
        if valid_directions_indexes:
            return directions[random.choice(valid_directions_indexes)]
        
        #don't move 
        return (0,0)

    def pick_direction_greedy(self, map):
        #If you're already at the target, you're done!
        #If there's no map you're screwed
        if self.is_at_target() or map==None: return (0,0)
            
        #List of directions: Right, Up, Left, Down
        directions = [(1,0), (0,1), (-1,0), (0,-1)] 
        
        #Check if each neighboring cell is open
        open_cells = [map.check_cell_open(self.X + DX, self.Y + DY) for DX, DY in directions] 
        #print("Right: "+str(open_cells[0])+" Up: "+str(open_cells[1])+" Left: "+str(open_cells[2]) + " Down: "+str(open_cells[3]))
        
        #Distance of each neighboring cell from the target cell
        distances = [distance(self.X + DX, self.Y + DY, self.TARGET_X, self.TARGET_Y) for DX, DY in directions]
        #print("Right: "+str(distances[0])+" Up: "+str(distances[1])+" Left: "+str(distances[2]) + " Down: "+str(distances[3]))
        
        #directions that are "open" (can be moved into) without walking into a previous space
        valid_directions_noreturn_indexes = [d for d in (0,1,2,3) if open_cells[d] and not (self.X + directions[d][0], self.Y + directions[d][1]) == (self.PREV_X, self.PREV_Y)]
        #allow moving back into previous space ONLY if there's no way to move forward otherwise
        valid_directions_indexes = [d for d in (0,1,2,3) if open_cells[d]]
        
        #if there's nowhere to go, then don't move
        if not valid_directions_noreturn_indexes and not valid_directions_indexes: return (0,0)
       
        #if there's only one way to go then go there
        if len(valid_directions_noreturn_indexes) == 1:
            return directions[valid_directions_noreturn_indexes[0]]
        
        if not valid_directions_noreturn_indexes and len(valid_directions_indexes) == 1:
            return directions[valid_directions_indexes[0]]
              
        #If there's more than one direction you can pick from, pick the one that's the smallest
        i1, d_min= -1, 99999
        if valid_directions_noreturn_indexes:
            for dir in valid_directions_noreturn_indexes:
                if distances[dir] <= d_min: 
                    i1, d_min = dir, distances[dir]
                
            
        
        i2, d_min = -1, 99999
        if valid_directions_indexes:
            for dir in valid_directions_indexes:
                if distances[dir] <= d_min: 
                    i2, d_min = dir, distances[dir]
                
            
        if not i1 == -1: return directions[i1]
        else:
            if not i2 == -1: return directions[i2]
            else:
                return (0,0)
            
        
        print("The algorithm should return something well before it gets to this point")
        return (0,0)
         
    def is_at_target(self):
        return (self.X,self.Y) == (self.TARGET_X,self.TARGET_Y)
    
    def step(self,map,t):
        #automatic movement to target
        self.timer += t
        if self.timer >= self.speed: 
            dx, dy = self.pick_direction_greedy(map)
            self.move(dx,dy)
            self.timer = 0
        
        
    def hasnt_moved(self):
        return (self.X, self.Y) == (self.PREV_X, self.PREV_Y)
    
    def draw(self):
        #Draw self
        X1,Y1 = self.X * CELL_WIDTH, self.Y * CELL_HEIGHT
        X2,Y2 = X1 + CELL_WIDTH,Y1 + CELL_HEIGHT
        pyglet.graphics.draw(4 ,pyglet.gl.GL_POLYGON, ('v2i',[X1,Y1, X2,Y1, X2,Y2, X1,Y2] ), ('c3B', self.color * 4 ) )
        
        #Draw a trail
        if not self.hasnt_moved():
            X1,Y1 = self.PREV_X * CELL_WIDTH, self.PREV_Y * CELL_HEIGHT
            X2,Y2 = X1 + CELL_WIDTH,Y1 + CELL_HEIGHT
            pyglet.graphics.draw(4 ,pyglet.gl.GL_POLYGON, ('v2i',[X1,Y1, X2,Y1, X2,Y2, X1,Y2] ), ('c3B', self.trailcolor * 4 ) )    
        
        #Draw target
        '''
        if not self.is_at_target():
            X1,Y1 = self.TARGET_X * CELL_WIDTH, self.TARGET_Y * CELL_HEIGHT
            X2,Y2 = X1 + CELL_WIDTH,Y1 + CELL_HEIGHT
            pyglet.graphics.draw(4 ,pyglet.gl.GL_POLYGON, ('v2i',[X1,Y1, X2,Y1, X2,Y2, X1,Y2] ), ('c3B', (255,255,0) * 4 ) )
        '''



class PlayerObject:
    def __init__(self, X = 1, Y = 1, TARGET_X = 22, TARGET_Y = 9, color = (255,255,0)):
        self.X, self.Y = X, Y
        self.PREV_X, self.PREV_Y = X,Y
        self.VX, self.VY = 0,0
        self.color = color
        self.trailcolor = tuple([x//2 for x in color])    
        
    def move(self, map):
        #Move in a particular direction
        self.PREV_X, self.PREV_Y = self.X, self.Y
        self.X, self.Y = self.X+self.VX, self.Y+self.VY
        if not map.check_cell_open(self.X,self.Y): self.X, self.Y = self.PREV_X, self.PREV_Y
        
    def on_key_press(self,symbol,map):
        if symbol == key.W:
            #Move up
            self.VX, self.VY = 0, 1
        elif symbol == key.D:
            #Move right
            self.VX, self.VY = 1, 0
        elif symbol == key.A:
            #Move left
            self.VX, self.VY = -1, 0
        elif symbol == key.S:
            #Move down
            self.VX, self.VY = 0,-1

    def on_key_release(self, symbol, map):
        if symbol in (key.W, key.S): self.VY = 0 #Cease vertical movement
        if symbol in (key.D, key.A): self.VX = 0 #Cease horizontal movement
      
    def hasnt_moved(self):
        return (self.X, self.Y) == (self.PREV_X, self.PREV_Y)    
    
    def draw(self): 
        #Draw self
        X1,Y1 = self.X * CELL_WIDTH, self.Y * CELL_HEIGHT
        X2,Y2 = X1 + CELL_WIDTH,Y1 + CELL_HEIGHT
        pyglet.graphics.draw(4 ,pyglet.gl.GL_POLYGON, ('v2i',[X1,Y1, X2,Y1, X2,Y2, X1,Y2] ), ('c3B', self.color * 4 ) )
        
        #Draw a trail
        if not self.hasnt_moved():
            X1,Y1 = self.PREV_X * CELL_WIDTH, self.PREV_Y * CELL_HEIGHT
            X2,Y2 = X1 + CELL_WIDTH,Y1 + CELL_HEIGHT
            pyglet.graphics.draw(4 ,pyglet.gl.GL_POLYGON, ('v2i',[X1,Y1, X2,Y1, X2,Y2, X1,Y2] ), ('c3B', self.trailcolor * 4 ) )   
        pass
        
        

MAP = Maze()
GHOSTS = [Pathfinder(X= 1, Y=15, TARGET_X = 46, TARGET_Y = 1, color = (255,0,0), speed = 5/TIME_CONST), 
    Pathfinder(X= 1, Y=9, TARGET_X = 46, TARGET_Y = 1, color = (0,255,255), speed = 4/TIME_CONST),
    Pathfinder(X= 1, Y=1, TARGET_X = 46, TARGET_Y = 1, color = (255,128,0), speed = 4/TIME_CONST),
    Pathfinder(X= 1, Y=30, TARGET_X = 46, TARGET_Y = 1, color = (255,0,255), speed = 6/TIME_CONST)] #speed is paradoxical- the higher it is, the slower the ghost is.

PLAYER = PlayerObject(X= 15, Y=16, color = (255,255,0))

@window.event
def on_draw():
    window.clear()
    MAP.draw()
    for GHOST in GHOSTS: GHOST.draw()
    PLAYER.draw()
    draw_mouse(CURSOR_X, CURSOR_Y)


@window.event
def on_key_release(symbol, modifiers):
    PLAYER.on_key_release(symbol, MAP)
    pass

  
@window.event
def on_key_press(symbol, modifiers):
    PLAYER.on_key_press(symbol, MAP)
    pass
        
@window.event
def on_mouse_motion(x,y,dx,dy):
    global CURSOR_X, CURSOR_Y
    CURSOR_X = x // CELL_WIDTH
    CURSOR_Y = y // CELL_HEIGHT

@window.event        
def on_mouse_press(x, y, button, modifiers):
    
    if button == mouse.LEFT:
        if MAP.check_cell_open(CURSOR_X, CURSOR_Y):
            for GHOST in GHOSTS: GHOST.set_target(CURSOR_X, CURSOR_Y)
            
           
      
def update(t):
    #print(t)
    PLAYER.move(MAP)
    for GHOST in GHOSTS: 
        GHOST.set_target(PLAYER.X, PLAYER.Y)
        GHOST.step(MAP,t)
    pass
    
pyglet.clock.schedule_interval(update, 1/TIME_CONST)
pyglet.app.run()
