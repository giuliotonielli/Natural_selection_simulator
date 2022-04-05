import bpy, math, copy, random, time, pickle, sys
from math import pi
from bpy import context

# choose here the starting number of plants, sheeps and wolves
plants_starting_number = 0
sheeps_starting_number = 6
wolves_starting_number = 4


# REMOVING ALL PREVIOUSLY USED ANIMALS
for i in bpy.context.selected_objects:
    i.select_set(False)

for i in bpy.context.scene.objects:
    x = i.name
    if x != "Wolf" and x != "Sheep" and x != "Plant" and x != "water" and x != "world" and x != "z-ray":
        i.select_set(True)
    
bpy.ops.object.delete() 

# DATA STRUCTURES INSTANTIATION
S_speeds, S_ranges, S_autos, S_sexes, S_popul = [], [], [], [], []
W_speeds, W_ranges, W_autos, W_sexes, W_popul = [], [], [], [], []
timeflow = 0.5
frame_num = [0]
plants = []    
sheeps = []
wolves = []
reject = {}

# world and water locations
bpy.data.objects['world'].location = (46,45,0)
bpy.data.objects['water'].location = (50,50,-2)


# Find the elevation at a given (x,y) coordinate 
def raycast(x,y):
    bpy.data.objects['z-ray'].location = (x,y,-10)
    mesh_eval = context.object.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
    vals = [0.] * len(mesh_eval.attributes['UVMap'].data)
    mesh_eval.attributes['UVMap'].data.foreach_get("value", vals)
    return vals[0] - 9
    
    
# ADDING AN ANIMAL / PLANT
def add_obj(what, speed, pos, range, dir, auto, sex):
    # get elevation 
    pos[2] = raycast(pos[0], pos[1])
    if pos[2] < -1:
        return False
    
    # deselect all object
    for i in bpy.context.selected_objects:
        i.select_set(False)
    
    # random direction
    new = random.randint(1, 360) + dir  
    if new > 360:
        new -= 360
    
    # depending on the type of object (wolf, sheep or plant) create 
    # the object and  append it to the list of wolves.
    if what == "WOLF":
        bpy.data.objects["Wolf"]. select_set(True)
        bpy.ops.object.duplicate(linked=0, mode='TRANSLATION')
        wolves.append(Animal(what, speed, pos, range, new, bpy.context.selected_objects[-1], auto, sex))
        
    elif what == "SHEEP":   
        bpy.data.objects["Sheep"].select_set(True)
        bpy.ops.object.duplicate(linked=0, mode='TRANSLATION')
        sheeps.append(Animal(what, speed, pos, range, new, bpy.context.selected_objects[-1], auto, sex))
        
    elif what == "PLANT":
        bpy.data.objects["Plant"].select_set(True)
        bpy.ops.object.duplicate(linked=0, mode='TRANSLATION')
        plants.append(Animal(what, speed, pos, range, new, bpy.context.selected_objects[-1], auto, sex))
        bpy.context.selected_objects[-1].location = pos
    
    # rotate the new object by the random direction chosen previosuly
    bpy.context.selected_objects[-1].rotation_euler[2] += new*pi/180 
    return True
        
# check if there are predators, preys, or possible mates in a given range
def check_range(self, what):
    who, min = None, math.inf
    for i in what:
        dist = math.dist(self.pos, i.pos)
        if dist < min and dist < self.range and i != self:
            min = dist
            who = i
    return who

# this function will hide and delete an object when it dies
def hide_obj(who):
    # hide a given object at a given frame
    who.obj.hide_viewport = True
    who.obj.keyframe_insert("hide_viewport", frame = frame_num[0]+1)
    
    who.obj.hide_viewport = False
    who.obj.keyframe_insert(data_path="hide_viewport", frame=frame_num[0])
    
    # remove object from the scene
    if who.what == "SHEEP":
        sheeps.remove(who)
    elif who.what == "PLANT":
        plants.remove(who)
    else:
        wolves.remove(who)

# the ask function will simulate the situation where two animals
# decide whether to accept or reject a possible partner based on the 
# amout of sexual hormones that they have (the higher the better)
def ask(self, who):

    # if the amount of hormones of the first animal is greater than 0...
    if self.sex[0] > 0:

        # add both animals to the rejected list. This means that the two animals
        # will not be able to reproduce with each other for 10 frames. It doesn't matter 
        # whether the two animals decide to reproduce or not: in any case they won't
        # be able to mate for a certain period of time to "recharge their hormones".
        for i in reject:
            if self in reject[i]:
                reject[self].append([who, 10])
            else:
                reject[self] = [[who, 10]]
            if who in reject[i]:
                reject[who].append([self, 10])
                who_in = 1
            else:
                reject[who] = [[self, 10]]
        
        # the highest amount of sexual hormones is 69 ;)
        # the current amount of hormones in both animals divided by 69 will
        # be compared to a random number between 0 and 1. if the percentages of 
        # hormones are both higher than the random numbers, the animals will mate. 
        if self.sex[0]/69 >= random.random() and who.sex[0]/69 >= random.random(): 
            self.sex[0] = who
            who.sex[0] = self
            return who
    return None

# MATING FUNCTION
def mate(self, who):
    # set current partner to 0 (none).
    self.sex[2] = 0
    who.sex[2] = 0
    
    # if the animal reproducing is a wolf, it will have either 2 or 3 offsprings.
    if self.what == "WOLF":
        n = random.randint(2,3)
    
    # if the animal reproducing is a sheep, it will have either 2, 3 or 4 offsprings.
    elif self.what == "SHEEP":
        n = random.randint(2,4)
    
    # assigning genes to each offspring
    i = 0
    while i < n:
        # the speed gene will come from one of the two parents chosen randomly
        b = random.choice([self, who]).speed

        # the gene is modified by the function new_speed = parent_speed * (x**3),
        # where x is a random number from 0 to 1. This means it is really hard for the
        # gene to change dramatically, either in a positive or negative way.
        speed = b + ((random.uniform(0, 1))**3)*b

        # the maximum speed of all animals is 6
        if speed > 6:
            speed = 6
        
        # a very similar process is repeated for all genes
        b = random.choice([self, who]).range
        range = b + ((random.uniform(0, 1))**3)*b
        if range > 16:
            range = 16
        
        b = random.choice([self, who]).auto[1]
        auto = b + ((random.uniform(0, 1))**3)*b
        if auto > 256:
            auto = 256
        
        b = random.choice([self, who]).sex[1]
        sex = b + ((random.uniform(0, 1))**3)*b
        if sex > 69:
            sex = 69
        
        # create the object
        add_obj(self.what, speed, copy.deepcopy(self.pos), range, self.dir, [auto, auto], [-sex, sex, 0])
        
        # hide the object from the scene until the frame at which it's born
        x = bpy.context.selected_objects[-1]
        x.hide_viewport = True
        x.keyframe_insert( "hide_viewport", frame = 0)
        x.hide_viewport = False
        x.keyframe_insert( data_path= "hide_viewport", frame = frame_num[0])
        
        i += 1

# KEYFRAMING LOCATION, ROTATION, AND RIGID BODY      
def key(self, old_pos, old_dir):
    # Rotate
    diff = self.dir - old_dir
    
    self.obj.rotation_euler[2] += diff*pi/180
    self.obj.keyframe_insert("rotation_euler", frame=frame_num[0]) 
    
    # Move 
    self.pos[2] = raycast(self.pos[0], self.pos[1]) 
    
    self.obj.location = (self.pos[0], self.pos[1], self.pos[2])
    self.obj.keyframe_insert(data_path = "location", frame = frame_num[0]+10)
    
    self.obj.location = ((self.pos[0] + old_pos[0]) / 2, (self.pos[1] + old_pos[1]) / 2, self.pos[2] + 1)
    self.obj.keyframe_insert(data_path = "location", frame = frame_num[0]+5)
    
    self.obj.location = old_pos
    self.obj.keyframe_insert(data_path = "location", frame = frame_num[0]) 

# update the current frame
def frame_up(self):
    if len(wolves) > 0:
        if self == wolves[-1]:
            frame_num[0] += 10  
    elif len(sheeps) > 0:
        if self == sheeps[-1]:
            frame_num[0] += 10

# update the position of a given animal
def pos_up(self, time):
    old_dir = copy.deepcopy(self.dir)
    x, y = None, 1

    # the magnitude of the distance vector is speed * time
    vector_magnitude = self.speed * time

    # get any predators, possible partners and preys
    predators, us, prey = self.chain()

    # check range for predators or preys
    predator = check_range(self, predators)
    prey = check_range(self, prey) 
    
    # check if currently with a partner
    if self.sex[0] in us:

        # if the distance between the two partners is less than 2, they reproduce
        if math.dist(self.pos, self.sex[0].pos) < 2:
            key(self, copy.deepcopy(self.pos), copy.deepcopy(self.dir))
            frame_up(self)
            self.sex[2] = self.sex[0]

            # return False means the animal doesn't move (it's currently mating)
            return False

        # if they're far apart, the animal will go towards its mate
        else:
            x = self.sex[0]
    
    # checking borders and lakes
    elif self.pos[1] + vector_magnitude > 100 or raycast(self.pos[0], self.pos[1] + vector_magnitude) < -1:
        self.dir = random.randint(250, 290)
        y = 0
    elif self.pos[1] - vector_magnitude < 0 or raycast(self.pos[0], self.pos[1] - vector_magnitude) < -1:
        self.dir = random.randint(70, 110)
        y = 0
    elif self.pos[0] + vector_magnitude > 100 or raycast(self.pos[0] + vector_magnitude, self.pos[1]) < -1:
        self.dir = random.randint(160, 200)
        y = 0
    elif self.pos[0] - vector_magnitude < 0 or raycast(self.pos[0] - vector_magnitude, self.pos[1]) < -1:
        self.dir = random.randint(340, 380)
        y = 0
    
    # if the animal sees a predator, it will escape from it
    elif predator:  
        x = predator
        
    # elif the animal sees food, it will walk towards it
    elif prey:   
        if math.dist(self.pos, prey.pos) < self.speed:
            self.auto[0] = self.auto[1]
            hide_obj(prey)
        x = prey
    
    # else check for a partner
    elif (type(self.sex[0]) == int or type(self.sex[0]) == float):
        partner = check_range(self, us)
        if partner and self.sex[0] >= 0:
            if (type(partner.sex[0]) == int or type(partner.sex[0]) == float):
                if self in reject:
                    if len(reject[self]) > 0:
                        if reject[self][0][0] != partner:
                            x = ask(self, partner)
                else:
                    x = ask(self, partner)
    
    # if the animal is currently going towards / running 
    # away from another animal:
    if x:
        deltax = (self.pos)[0] - (x.pos)[0]
        deltay = (self.pos)[1] - (x.pos)[1]

        # if deltax = 0 we python cannot find the angle because it can't divide by 0
        if deltax == 0:
            if deltay > 0:
                self.dir = 270
            else:
                self.dir = 90
        else:           
            self.dir = math.degrees(math.atan(deltay / deltax))
            
            if (deltax >= 0 and deltay >= 0) or (deltax >= 0 and deltay < 0):
                self.dir += 180
            elif deltax < 0 and deltay >= 0:
                self.dir += 360
        
        # if the animal is a sheep and it detected a wolf in its range
        # go to the opposite direction of the wolf.
        if self.what == "SHEEP" and x.what == "WOLF":
            if self.dir > 180:
                self.dir -= 180
            else:
                self.dir += 180
    
    # if the animal doesn't have any other entity in its range and it is
    # not going towards a lake or the border, it goes in a random direction
    elif y:  
        self.dir = random.randint(int(self.dir) - 40, int(self.dir) + 40)
        if self.dir <= 0:
            self.dir += 360

    # if the angle obtained is > 360, subtract 360.
    if self.dir > 360:
        self.dir -= 360
    
    # move the object and store its previous location
    old_pos = copy.deepcopy(self.pos)
    self.pos[0] += vector_magnitude * math.cos(math.radians(self.dir))
    self.pos[1] += vector_magnitude * math.sin(math.radians(self.dir))

    # keyframe the old and new locations
    key(self, old_pos, old_dir)

    # decrease the autonomy left by the magnitude of the distance vector
    self.auto[0] -= vector_magnitude

    # update the frame
    frame_up(self)

    # return True means that animal has moved (it returns False only if 
    # it is currently mating)
    return True
         
# at every frame, update the time left before two animals can mate
def reject_up(self):
    if self in reject:
        for i in reject[self]:
            if len(i) > 1:
                if i[1] == 0:
                    reject[self].remove(i)
                else:
                    i[1] -= 1
    
# Class Animal                       
class Animal(object):
    def __init__(self, what, speed, pos, range, dir, obj, auto, sex):
        self.what = what
        self.speed = speed   #
        self.pos = pos
        self.range = range   #
        self.dir = dir
        self.obj = obj
        self.auto = auto     #
        self.sex = sex       #
    
    # returns useful info on the animal (useful at the end to compare how 
    # the average wolf and sheep has changed over time)
    def info(self):
        return [self.speed, self.range, self.auto[1], self.sex[1]]
    
    # returns the food chain of a given animal
    def chain(self):
        if self.what == "WOLF":
            return [], wolves, sheeps
        if self.what == "SHEEP":
            return wolves, sheeps, plants
    
    # updates the state of the animal
    def update(self):
        # increase sex hormone
        if type(self.sex[0]) == int or type(self.sex[0]) == float:
            if self.sex[0] < self.sex[1]:
                self.sex[0] += self.sex[1] / 20
        
        # die if no autonomy left
        if self.auto[0] <= 0:
            hide_obj(self) 
            return  
        
        # move or, else, reproduce
        if not pos_up(self, timeflow): # if the animal has not moved, it means it's reproducing
            if self.sex[2] != 0:
                if self.sex[2].sex[2] == self:
                    self.sex[0] = 0
                    self.sex[2].sex[0] = 0
                    mate(self, self.sex[2])
                else:
                    key(self, copy.deepcopy(self.pos), copy.deepcopy(self.dir))

# store data that can be analyzed at the end
def data():
    S_sheeps = [0,0,0,0,0]
    S_wolves = [0,0,0,0,0]

    for i in sheeps:
        info = i.info()
        S_sheeps[0] += info[0]
        S_sheeps[1] += info[1]
        S_sheeps[2] += info[2]
        S_sheeps[3] += info[3]

    for i in wolves:
        info = i.info()
        S_wolves[0] += info[0]
        S_wolves[1] += info[1]
        S_wolves[2] += info[2]
        S_wolves[3] += info[3]

    S_len = len(sheeps)
    W_len = len(wolves)

    try:   #sheeps
        S_speeds.append(S_sheeps[0] / S_len) 
        S_ranges.append(S_sheeps[1] / S_len)
        S_autos. append(S_sheeps[2] / S_len)  
        S_sexes. append(S_sheeps[3] / S_len)  
        S_popul. append(S_len)

    except Exception:
        S_speeds.append(0)
        S_ranges.append(0)
        S_autos. append(0)
        S_sexes. append(0)
        S_popul. append(0)

    try:
        W_speeds.append(S_wolves[0] / W_len) 
        W_ranges.append(S_wolves[1] / W_len)
        W_autos. append(S_wolves[2] / W_len)  
        W_sexes. append(S_wolves[3] / W_len)
        W_popul. append(W_len)

    except Exception:
        W_speeds.append(0)
        W_ranges.append(0)
        W_autos. append(0)
        W_sexes. append(0)
        W_popul. append(0)

# GAME (main function)
def game(time):
    # if no time left, return
    if time == 0:
        return
    # update all animals
    for i in sheeps + wolves:
        i.update()

    # every 5 frames, a plant will spawn at a random position
    if frame_num[0] % 5 == 0:
        if add_obj("PLANT",0,[random.randint(1,99), random.randint(1,99), 0], 0, 0, 0, 0):
            x = bpy.context.selected_objects[-1]
            x.hide_viewport = True
            x.keyframe_insert("hide_viewport", frame = 0)
            x.hide_viewport = False
            x.keyframe_insert(data_path= "hide_viewport", frame = frame_num[0])

    # store data
    data()

    # do it again and subtract 1 unit of time
    game(time-1)

# get user inputs and spwan the given animals and plants at random positions on the map
def start(p,s,w):
    for i in [0]*p:
        add_obj("PLANT", 0, [random.randint(1,99), random.randint(1,99), 0], 0, 0, 0, 0)
    for i in [0]*s:
        auto = random.randint(10,200)
        sex = random.randint(3,60)
        add_obj("SHEEP", random.randint(1,5), [random.randint(1,99), random.randint(1,99), 0], random.randint(1,16), random.randint(1,360), [auto, auto], [sex, sex, 0])
    for i in [0]*w:
        auto = random.randint(10,200)
        sex = random.randint(3,60)
        add_obj("WOLF", random.randint(1,5), [random.randint(1,99), random.randint(1,99), 0], random.randint(1,16), random.randint(1,360), [auto, auto], [sex, sex, 0])

# first input: # of plants
# second input: # of sheeps
# third input: # of wolves
start(plants_starting_number, sheeps_starting_number, wolves_starting_number)

# how many frames long do you want the simulation to be? (input x 10)
game(60) 

# print stored on sheeps and wolves during the simulation
print(S_speeds, ",", S_ranges, ",", S_autos, ",", S_sexes,",", S_popul,",", W_speeds, ",",W_ranges,",", W_autos,",", W_sexes,",", W_popul)
