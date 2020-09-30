from tkinter import *
import time
import random
import math
import matplotlib.pyplot as plt

PLOT_TIME = 30

FRAME_LENGTH = 30 #ms/frame
DAY_LENGTH = 10 #frame/day

ANIMAL_SIZE = 10 

WORLD_HEIGHT = 640 
WORLD_WIDTH = 640 
BLOCK_WIDTH = 40   
BLOCK_NUMBER = 16 #per side

INIT_WOLF = 20 
INIT_SHEEP = 800 

MAX_GRASS = 100 #high
GRASS_REGENERATE = 0.25
GRASS_REDUCE = 2 #per bite
FERTILE = 20

MAX_HUNGER = 100
WOLF_HUNGER_REDUCE = 0.6 #/frame
SHEEP_HUNGER_REDUCE = 0.3
MOVE_REDUCE = 0.005 #/pixel
GRASS_RESTORE = 5 
FULL = 70
HUNGRY = 30

WANDER_SPEED = 1 
SHEEP_RUN_SPEED = 3
WOLF_RUN_SPEED = 5
MATE_SPEED = 3
WANDER_REGION = 96

MAX_AGE = 2048 #frame

SEE_WOLF_DISTANCE = 32
SEE_WOLF_SQUARED = SEE_WOLF_DISTANCE**2
SEE_WOLF_BLOCK = int(-(-SEE_WOLF_DISTANCE//BLOCK_WIDTH))
SEE_BLOCK_DISTANCE = 30
SEE_BLOCK = int(-(-SEE_BLOCK_DISTANCE//BLOCK_WIDTH))
SEE_PREY_DISTANCE = 36 #pixel
SEE_PREY_SQUARED = SEE_PREY_DISTANCE**2
SEE_PREY_BLOCK = int(-(-SEE_PREY_DISTANCE//BLOCK_WIDTH))
CAPTURE_DISTANCE = 4

SEE_MATE_DISTANCE = 128 
SEE_MATE_SQUARED = SEE_MATE_DISTANCE**2
SEE_MATE_BLOCK = int(-(-SEE_MATE_DISTANCE//BLOCK_WIDTH))
BREED_DISTANCE = 4
WOLF_BREED_COOLDOWN = 300 
SHEEP_BREED_COOLDOWN = 150 
INIT_COOLDOWN = 100

RED_FULL = 32 
RED_LOW = 144
GREEN = 90 
BLUE = 38 
hexadecimal = ["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F"]

class Frame:
    def __init__(self,height = WORLD_HEIGHT, width = WORLD_WIDTH):
        self.root = Tk()
        self.canvas = Canvas(self.root,width = width,height = height)
        self.canvas.pack()

        self.counter = 0 
        self.sheepCounts = [INIT_SHEEP]
        self.wolfCounts = [INIT_WOLF]
        self.time = [0]

        self.root.bind('<KeyPress>',self.drawPlot)

        self.world = World()

    def start(self):
        self.world.start()
        self.refresh()
        self.root.mainloop()

    def drawGame(self):
        self.canvas.delete("all")
        
        for l in self.world.blocks:
            for g in l:
                red = int(g.fertility/100*(RED_FULL-RED_LOW)+RED_LOW)
                R1 = hexadecimal[red//16]
                R2 = hexadecimal[red%16]
                color = "#"+R1+R2+str(GREEN)+str(BLUE)
                self.canvas.create_rectangle(g.x,g.y,\
                                             g.x+BLOCK_WIDTH,g.y+BLOCK_WIDTH,\
                                             fill = color,outline = "")
        for w in self.world.wolves:
            self.canvas.create_rectangle(w.position[0],w.position[1],\
                                         w.position[0]+ANIMAL_SIZE,w.position[1]+ANIMAL_SIZE,\
                                         fill = 'gray22',outline = "")
        
        for s in self.world.sheep:
            self.canvas.create_rectangle(s.position[0],s.position[1],\
                                         s.position[0]+ANIMAL_SIZE,s.position[1]+ANIMAL_SIZE,\
                                         fill = 'gray91',outline = "")

    def refresh(self):
        if self.counter == PLOT_TIME:
            self.sheepCounts.append(len(self.world.sheep))
            self.wolfCounts.append(len(self.world.wolves))
            self.time.append(self.time[-1]+1)
            self.counter = 0
        else:
            self.counter+=1
        #t = time.process_time()
        self.world.refresh()
        #e =  time.process_time() -t
        #print(e)
        #t =  time.process_time()
        self.drawGame()
        #e =  time.process_time()-t
        #print(e,"\n")
        self.root.after(FRAME_LENGTH,self.refresh)

    def drawPlot(self,event):
        print("plot")
        if event.keysym!="p":
            return
        fig, ax1 = plt.subplots()
        ax1.set_xlabel('time')
        ax1.set_ylabel('sheep',color = "blue")
        ax1.plot(self.time,self.sheepCounts,color = "blue") 
        ax1.tick_params(axis='y', labelcolor="blue")

        ax2 = ax1.twinx()
        ax2.set_ylabel('wolf', color="red")
        ax2.plot(self.time,self.wolfCounts,color = "red")
        ax2.tick_params(axis='y', labelcolor="red")
        
        fig.tight_layout()
        plt.show()

class GameObject:
    def __init__(self,x=-10,y=-10,breed = SHEEP_BREED_COOLDOWN):
        self.position = [x,y]
        self.hunger = random.randrange(FULL,MAX_HUNGER) 
        self.age = 1
        self.targetPlace =\
        [random.randrange(max(0,int(self.position[0]-WANDER_REGION)),min(WORLD_WIDTH,int(self.position[0]+WANDER_REGION))),\
         random.randrange(max(0,int(self.position[1]-WANDER_REGION)),min(WORLD_HEIGHT,int(self.position[1]+WANDER_REGION)))]
        self.breedCoolDown = breed 
        self.state = "wander"

    def renewTarget(self):
        self.targetPlace =\
        [random.randrange(max(0,int(self.position[0]-WANDER_REGION)),min(WORLD_WIDTH,int(self.position[0]+WANDER_REGION))),\
         random.randrange(max(0,int(self.position[1]-WANDER_REGION)),min(WORLD_HEIGHT,int(self.position[1]+WANDER_REGION)))]

    def moveToward(self, target,speed):
        xNy= [target[0]-self.position[0], target[1]-self.position[1]]
        distance = math.sqrt(xNy[0]**2+xNy[1]**2)
        if distance <= speed:
            self.position[0] = target[0]
            self.position[1] = target[1]
        else:
            self.position[0]+=speed*xNy[0]/distance
            self.position[1]+=speed*xNy[1]/distance
        self.hunger -= speed*MOVE_REDUCE

    def wander(self):
        
        self.moveToward(self.targetPlace,WANDER_SPEED)
        if self.position == self.targetPlace:
            self.renewTarget()


    def mate(self,mate):
        self.moveToward(mate.position,MATE_SPEED)
        
        if self.position == mate.position:
            if isinstance(mate,Sheep):
                self.breedCoolDown = SHEEP_BREED_COOLDOWN 
            else:
                self.breedCoolDown = WOLF_BREED_COOLDOWN
            return True
        return False

    def checkDeath(self):
        if self.hunger < 0 or self.age > MAX_AGE:
            return True
        else:
            return False

class Wolf(GameObject):
    def __init__(self,x=-10,y=-10,breed = WOLF_BREED_COOLDOWN):
        super().__init__(x,y,breed)

    def prey(self,sheep):
        self.moveToward(sheep.position,WOLF_RUN_SPEED)
        
        if self.position == sheep.position:
            self.hunger = MAX_HUNGER
            return True

        return False


class Sheep(GameObject):
    def __init__(self,x=-10,y=-10,breed = SHEEP_BREED_COOLDOWN):
        super().__init__(x,y,breed)
        self.state = "eat"

    def stateUpdate(self):
        if self.hunger < HUNGRY:
            self.state = "eat"
        elif self.hunger >= HUNGRY and self.breedCoolDown == 0:
            self.state = "mate"
        elif self.hunger >= FULL:
            self.state = "wander"
    
    def escape(self,wolf,speed):
        deltax = self.position[0]-wolf.position[0]
        deltay = self.position[1]-wolf.position[1]
        distance = math.sqrt(deltax**2+deltay**2)
        if distance == 0:
            return
        self.position[0] = (self.position[0]+speed*deltax/distance)%WORLD_WIDTH
        self.position[1] = (self.position[1]+speed*deltay/distance)%WORLD_HEIGHT

class Block():
    def __init__(self,x = -1,y = -1):
        self.x = x
        self.y = y
        self.fertility = random.randrange(0,MAX_GRASS)
        self.sheep= []
        self.wolves = []
    def refresh(self):
        self.sheep = []
        self.wolves = []


class World:
    def __init__(self):
        self.wolves = []
        self.sheep = []
        self.blocks = []
        self.distance = []
    def start(self):
        for w in range(INIT_WOLF):
            x = random.randrange(0,WORLD_WIDTH)
            y = random.randrange(0,WORLD_HEIGHT)
            self.wolves.append(Wolf(x,y,random.randrange(INIT_COOLDOWN,WOLF_BREED_COOLDOWN)))

        for s in range(INIT_SHEEP):
            x = random.randrange(0,WORLD_WIDTH)
            y = random.randrange(0,WORLD_HEIGHT)
            self.sheep.append(Sheep(x,y,random.randrange(INIT_COOLDOWN,SHEEP_BREED_COOLDOWN)))

        for x in range(BLOCK_NUMBER):
            self.blocks.append([])
            for y in range(BLOCK_NUMBER):
                self.blocks[x].append(Block(x*BLOCK_WIDTH,y*BLOCK_WIDTH))

        self.refreshBlock()

        
    def refresh(self):
        for x in range(BLOCK_NUMBER):
            for y in range(BLOCK_NUMBER):
                if self.blocks[x][y].fertility<100:
                    self.blocks[x][y].fertility += GRASS_REGENERATE
        for w in range(len(self.wolves)-1,-1,-1):
            self.blocks[int(self.wolves[w].position[0]//BLOCK_WIDTH)][int(self.wolves[w].position[1]//BLOCK_WIDTH)].wolves.remove(self.wolves[w])
            if self.wolves[w].hunger >= HUNGRY and  self.wolves[w].breedCoolDown == 0:
                mate = self.findAnimal(self.wolves[w],"mate")
                if mate != False:
                    if self.wolves[w].mate(mate):
                        newWolf = Wolf(self.wolves[w].position[0],self.wolves[w].position[1])
                        self.wolves.append(newWolf)
                        self.blocks[int(self.wolves[w].position[0]//BLOCK_WIDTH)][int(self.wolves[w].position[1]//BLOCK_WIDTH)].wolves.append(newWolf)
                        mateIndex = self.wolves.index(mate)
                        self.wolves[mateIndex].breedCoolDown = WOLF_BREED_COOLDOWN
                        self.wolves[w].renewTarget()
                else:
                    self.wolves[w].wander()
            elif self.wolves[w].hunger>=FULL:
                self.wolves[w].wander()
            else:
                nearSheep = self.findAnimal(self.wolves[w],"prey")
                if nearSheep!=False:
                    if self.wolves[w].prey(nearSheep):
                        self.sheep.remove(nearSheep)
                        self.blocks[int(nearSheep.position[0]//BLOCK_WIDTH)][int(nearSheep.position[1]//BLOCK_WIDTH)].sheep.remove(nearSheep)
                        self.wolves[w].renewTarget()
                else:
                    self.wolves[w].wander()
            if self.wolves[w].breedCoolDown>0:
                self.wolves[w].breedCoolDown -= 1
            self.wolves[w].age += 1
            self.wolves[w].hunger -= WOLF_HUNGER_REDUCE
            
            if self.wolves[w].checkDeath():
                self.wolves.pop(w)
                continue
            self.blocks[int(self.wolves[w].position[0]//BLOCK_WIDTH)][int(self.wolves[w].position[1]//BLOCK_WIDTH)].wolves.append(self.wolves[w])

        for s in range(len(self.sheep)-1,-1,-1):
            xCoordinate = int(self.sheep[s].position[0]//BLOCK_WIDTH)
            yCoordinate = int(self.sheep[s].position[1]//BLOCK_WIDTH)
            self.blocks[xCoordinate][yCoordinate].sheep.remove(self.sheep[s])
            self.sheep[s].stateUpdate()
            enemy = self.findAnimal(self.sheep[s],"escape")
            if enemy != False:
                self.sheep[s].escape(enemy,SHEEP_RUN_SPEED)
                self.sheep[s].renewTarget()
            if self.sheep[s].state == "mate":
                mate = self.findAnimal(self.sheep[s],"mate")
                if mate != False:
                    if self.sheep[s].mate(mate):
                        newSheep= Sheep(self.sheep[s].position[0],self.sheep[s].position[1])
                        self.sheep.append(newSheep)
                        self.blocks[int(self.sheep[s].position[0]//BLOCK_WIDTH)][int(self.sheep[s].position[1]//BLOCK_WIDTH)].sheep.append(newSheep)
                        mateIndex = self.sheep.index(mate)
                        self.sheep[mateIndex].breedCoolDown = SHEEP_BREED_COOLDOWN
                else:
                    self.sheep[s].wander()
            elif self.sheep[s].state == "wander":
                self.sheep[s].wander()
            elif self.sheep[s].state == "eat":
                if self.blocks[xCoordinate][yCoordinate].fertility>=GRASS_REDUCE:
                    self.sheep[s].hunger += GRASS_RESTORE
                    self.blocks[xCoordinate][yCoordinate].fertility-=GRASS_REDUCE
                else:
                    block = self.findBlock(self.sheep[s])             
                    if block != False:
                        self.sheep[s].moveToward(block,SHEEP_RUN_SPEED)
                        self.sheep[s].renewTarget()
                    else:
                        self.sheep[s].wander()
            if self.sheep[s].breedCoolDown>0:
                self.sheep[s].breedCoolDown -= 1
            self.sheep[s].age += 1
            self.sheep[s].hunger -= SHEEP_HUNGER_REDUCE
            if self.sheep[s].checkDeath():
                self.sheep.pop(s)
                continue
            self.blocks[int(self.sheep[s].position[0]//BLOCK_WIDTH)][int(self.sheep[s].position[1]//BLOCK_WIDTH)].sheep.append(self.sheep[s])

    def refreshBlock(self):
        for h in self.blocks:
            for v in h:
                v.refresh()
        for w in self.wolves:
            self.blocks[int(w.position[0]//BLOCK_WIDTH)][int(w.position[1]//BLOCK_WIDTH)].wolves.append(w)
        for s in self.sheep:
            self.blocks[int(s.position[0]//BLOCK_WIDTH)][int(s.position[1]//BLOCK_WIDTH)].sheep.append(s)

    def findAnimal(self,animal,action):
        dis = {}
        x = int(animal.position[0]//BLOCK_WIDTH)
        y = int(animal.position[1]//BLOCK_WIDTH)
        if action == "mate":
            scope = SEE_MATE_BLOCK
            maxDistance = SEE_MATE_SQUARED
        elif isinstance(animal,Wolf):
            scope = SEE_PREY_BLOCK
            maxDistance = SEE_PREY_SQUARED
        else:
            scope = SEE_WOLF_BLOCK
            maxDistance = SEE_WOLF_SQUARED

        for h in range(max(-scope,-x),min(BLOCK_NUMBER-x,scope+1)):
            for v in range(max(-scope,-y),min(BLOCK_NUMBER-y,scope+1)):
                if isinstance(animal,Wolf):
                    if action == "mate":
                        for w in self.blocks[x+h][y+v].wolves:
                            if w.breedCoolDown == 0 and w.hunger >= HUNGRY:
                                dis[w] = (w.position[0]-animal.position[0])**2+(w.position[1]-animal.position[1])**2
                    else:
                        for s in self.blocks[x+h][y+v].sheep:
                            dis[s] = (s.position[0]-animal.position[0])**2+(s.position[1]-animal.position[1])**2
                else:
                    if action == "mate":
                        for s in self.blocks[x+h][y+v].sheep:
                            if s.breedCoolDown == 0 and s.hunger >= HUNGRY:
                                dis[s] = (s.position[0]-animal.position[0])**2+(s.position[1]-animal.position[1])**2
                    else:
                        for w in self.blocks[x+h][y+v].wolves:
                            dis[w] = (w.position[0]-animal.position[0])**2+(w.position[1]-animal.position[1])**2
        if dis == {}:
            return False
        minDis = min(dis.keys(),key = lambda x:dis[x])
        if dis[minDis] > maxDistance:
            return False 
        else:
            return minDis

    def findBlock(self,sheep):
        dis = {}
        x = int(sheep.position[0]//BLOCK_WIDTH)
        y = int(sheep.position[1]//BLOCK_WIDTH)
        for h in range(max(-SEE_BLOCK,-x),min(BLOCK_NUMBER-x,SEE_BLOCK+1)):
            for v in range(max(-SEE_BLOCK,-y),min(BLOCK_NUMBER-y,SEE_BLOCK+1)):
                if self.blocks[x+h][y+v].fertility >= FERTILE:
                    cenX = (x+h)*BLOCK_WIDTH+BLOCK_WIDTH/2
                    cenY = (y+v)*BLOCK_WIDTH+BLOCK_WIDTH/2
                    dis[(cenX,cenY)]=(cenX-sheep.position[0])**2+(cenY-sheep.position[1])**2
        if dis == {}:
            return False 
        minDis = min(dis.keys(),key = lambda x:dis[x])
        return minDis







if __name__ == '__main__':
    f = Frame()
    f.start()
