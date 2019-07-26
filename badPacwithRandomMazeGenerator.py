import numpy, random, pyglet
from pyglet.window import mouse, key

WINDOW_WIDTH, WINDOW_HEIGHT = 640, 480
CELL_WIDTH, CELL_HEIGHT = 16, 16
TIME_CONST = 120
window = pyglet.window.Window(width = WINDOW_WIDTH, height = WINDOW_HEIGHT)

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
        self.maze = numpy.ones((height,width), dtype = int)
        self.generateMaze()
        
    def generateMaze(self):
        self.stack.append( Node(1,1) )
        while self.stack:
            next = self.stack.pop()
            if self.validNextNode(next):
                self.maze[next.y][next.x] = 0
                neighbors = self.findNeighbors(next)
                self.randomlyAddNodesToStack(neighbors)
            
        
        
        
    def validNextNode(self, node):
        numNeighboringOnes = 0
        coords = [(node.x-1,node.y-1),(node.x-1,node.y),(node.x-1,node.y+1), (node.x,node.y-1) ,(node.x,node.y+1), (node.x+1,node.y-1),(node.x+1,node.y),(node.x+1,node.y+1)]
        numNeighboringOnes = sum([1 for x,y in coords if self.pointOnGrid(x, y) and self.maze[y][x]==0])
        return numNeighboringOnes in (0,1,2,3) and not self.maze[node.y][node.x] == 0
    
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
            return self.maze[y][x] == 0
                
        return False
    
    def get_list_positions_open(self):
        return [(x,y) for y in range(self.height) for x in range(self.width) if self.maze[y][x] == 0]
    
    def draw(self):
        for y in range(self.height):
            for x in range(self.width): 
                currentCell = self.maze[y][x]
                if currentCell == 1:
                    X1,Y1 = x * CELL_WIDTH, y * CELL_HEIGHT,
                    X2,Y2 = X1 + CELL_WIDTH,Y1 + CELL_HEIGHT
                    pyglet.graphics.draw(4 ,pyglet.gl.GL_POLYGON, ('v2i',[X1,Y1, X2,Y1, X2,Y2, X1,Y2] ), ('c3B', (0,255,0) * 4 ) )    
                
             
        
    
    
class Ghost:
    def __init__(self, X = 1, Y = 1, TARGET_X = 22, TARGET_Y = 9, color = (255,0,0), speed = 1/60 ):
        self.X, self.Y = X, Y
        self.PREV_X, self.PREV_Y = X,Y
        self.TARGET_X, self.TARGET_Y = TARGET_X, TARGET_Y
        self.color = color
        self.trailcolor = tuple([x//2 for x in color])
        self.speed = speed
        self.timer = 0
        
        self.states = ("SEEKING", "WANDERING", "FLEEING")
        self.state = random.choice(self.states)
           
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

    def pick_direction_chase(self, map):
        #If you're already at the target, you're done!
        #If there's no map you're screwed
        if self.is_at_target() or map==None: return (0,0)
        #List of directions: Right, Up, Left, Down
        directions = [(1,0), (0,1), (-1,0), (0,-1)] 
        #Check if each neighboring cell is open
        open_cells = [map.check_cell_open(self.X + DX, self.Y + DY) for DX, DY in directions] 
        #Distance of each neighboring cell from the target cell
        distances = [distance(self.X + DX, self.Y + DY, self.TARGET_X, self.TARGET_Y) for DX, DY in directions]
        #directions that are "open" (can be moved into) without walking into a previous space
        valid_directions_noreturn_indexes = [d for d in (0,1,2,3) if open_cells[d] and not (self.X + directions[d][0], self.Y + directions[d][1]) == (self.PREV_X, self.PREV_Y)]
        #allow moving back into previous space ONLY if there's no way to move forward otherwise
        valid_directions_indexes = [d for d in (0,1,2,3) if open_cells[d]]
        #if there's nowhere to go, then don't move
        if not valid_directions_noreturn_indexes and not valid_directions_indexes: return (0,0)
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
        
    def pick_direction_run_away(self, map):
        #If you're already at the target, you're done!
        #If there's no map you're screwed
        if self.is_at_target() or map==None: return (0,0)
        #List of directions: Right, Up, Left, Down
        directions = [(1,0), (0,1), (-1,0), (0,-1)] 
        #Check if each neighboring cell is open
        open_cells = [map.check_cell_open(self.X + DX, self.Y + DY) for DX, DY in directions] 
        #Distance of each neighboring cell from the target cell
        distances = [distance(self.X + DX, self.Y + DY, self.TARGET_X, self.TARGET_Y) for DX, DY in directions]
        #directions that are "open" (can be moved into) without walking into a previous space
        valid_directions_noreturn_indexes = [d for d in (0,1,2,3) if open_cells[d] and not (self.X + directions[d][0], self.Y + directions[d][1]) == (self.PREV_X, self.PREV_Y)]
        #allow moving back into previous space ONLY if there's no way to move forward otherwise
        valid_directions_indexes = [d for d in (0,1,2,3) if open_cells[d]]
        #if there's nowhere to go, then don't move
        if not valid_directions_noreturn_indexes and not valid_directions_indexes: return (0,0)
        #if there's only one way to go then go there
        if len(valid_directions_noreturn_indexes) == 1: return directions[valid_directions_noreturn_indexes[0]]
        if not valid_directions_noreturn_indexes and len(valid_directions_indexes) == 1: return directions[valid_directions_indexes[0]]
              
        #If there's more than one direction you can pick from, pick the one that's gonna maximize your distance from your target
        i1, d_min= -1, 0
        if valid_directions_noreturn_indexes:
            for dir in valid_directions_noreturn_indexes:
                if distances[dir] > d_min: i1, d_min = dir, distances[dir]
                
            
        
        i2, d_min = -1, 0
        if valid_directions_indexes:
            for dir in valid_directions_indexes:
                if distances[dir] > d_min: i2, d_min = dir, distances[dir]
            
        
        
        if not i1 == -1: return directions[i1]
        else:
            if not i2 == -1: return directions[i2]
            else:
                return (0,0)
            
        
        
        return (0,0)
        
    def is_at_target(self):
        return (self.X,self.Y) == (self.TARGET_X,self.TARGET_Y)
    
    def step(self,map,t):
        #automatic movement to target
        self.timer += t
        if self.timer >= self.speed: 
            if self.state == "SEEKING":
                dx, dy = self.pick_direction_chase(map)
            elif self.state == "FLEEING":
                dx, dy = self.pick_direction_run_away(map)
                dx, dy = dx, dy
            else:
                dx, dy = self.pick_direction_random(map)
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
        self.PREV_X, self.PREV_Y = X, Y
        self.VX, self.VY = 0,0
        self.timerX, self.timerY = 0,0
        self.color = color
        self.trailcolor = tuple([x//2 for x in color])    
        
    def step(self, map):
        self.move(self.VX,self.VY)
        if not map.check_cell_open(self.X,self.Y): self.X, self.Y = self.PREV_X, self.PREV_Y
        
    def move(self, DX, DY):
        #Move in a particular direction
        self.PREV_X, self.PREV_Y = self.X, self.Y
        self.X, self.Y = self.X+self.VX, self.Y+self.VY
        
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
list_open = MAP.get_list_positions_open()

#some sort of algorithm to find some open locations 
def pick_open_location_within_range(x0, y0, list_open, r):
    return random.choice( [(x,y) for x,y in list_open if x in range(x0-r,x0+r) and y in range(y0-r,y0+r)] )


#Spawn the player in an open space in the center of the maze
px, py = pick_open_location_within_range(MAP.width//2, MAP.height//2, list_open, 4)
PLAYER = PlayerObject(X= px, Y= py, color = (255,255,0))

#Spawn the ghosts in the corners
GHOSTS = []
colors_corners = (
    ((128,0,255), (1,1)),
    ((255,128,0), (MAP.width-2,1)),
    ((0,255,128), (1,MAP.height-2)),
    ((255,0,128), (MAP.width-2,MAP.height-2))
    )
for color, corner in colors_corners:
    gx, gy = pick_open_location_within_range(corner[0], corner[1], list_open, 4)
    GHOSTS.append( Ghost(X= gx, Y=gy, TARGET_X = px, TARGET_Y = py, color = color, speed = 7/TIME_CONST) )
    

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
    
@window.event
def on_key_press(symbol, modifiers):
    PLAYER.on_key_press(symbol, MAP)
            
@window.event
def on_mouse_motion(x,y,dx,dy):
    global CURSOR_X, CURSOR_Y
    CURSOR_X, CURSOR_Y = x // CELL_WIDTH, y // CELL_HEIGHT
    
@window.event        
def on_mouse_press(x, y, button, modifiers):
    
    if button == mouse.LEFT:
        if MAP.check_cell_open(CURSOR_X, CURSOR_Y):
            for GHOST in GHOSTS: GHOST.set_target(CURSOR_X, CURSOR_Y)
            
           
      
def update(t):
    PLAYER.step(MAP)
    for GHOST in GHOSTS: 
        GHOST.set_target(PLAYER.X, PLAYER.Y)
        GHOST.step(MAP,t)
    pass
    
pyglet.clock.schedule_interval(update, 1/TIME_CONST)
pyglet.app.run()
