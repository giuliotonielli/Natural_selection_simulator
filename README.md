# Natural_selection_simulator
This project will simulate the effects of natural selection on a 3D map populated by wolves, sheeps and plants which will interact with each other in order to survive. 

## General Information:
A 3D map is populated by three diffferent kinds of living beings: wolves, sheeps and plants. The two animals can move around the map. The direction each animals moves depends on its current priorities. For example, if a sheep detects a wolf in its range, the sheep will start running away from the wolf. At the same time, if the wolf detects a sheep is in its range, it will start running towards the sheep. If the wolf is faster than the sheep, the wolf will eat the sheep. Else, the sheep will be able to run away. Similarly, sheeps eat plants and will walk towards them if there's one close enough to them. Each animal has 4 attributes or genes: 

1. velocity: how fast the animal moves.
2. range radius: the radius within which an animal can detect other entities (for example, if a sheep's range radius is 5, the    sheep will be able to detect all animals and plants that are not more than 5 units away)
3. autonomy: the total distance an animal can travel without any food. When the animal eats, autonomy will go back to its          normal level. If the autonomy goes to 0, the animal dies. 
4. amount of sex hormones: the higher it is, the more likely it is that the animal will reproduce. Once the animal reproduces,    this attribute will go to 0 and slowly increase till it reaches it's maximum amount.

When two animals reproduce, there's a 50% chance each offspring will receive one of the four genes from the father and a 50% chance it will receive the gene from the mother. Then, each gene will be mutated the following function:
MutatedGene = ParentGene * x, where x is a random number between 0 and 1. This means the gene has a higher chance of remaining about the same rather than changing dramatically (look at the function below). Genes have the same probablity of mutating in a positive and a negative way. Therefore, any improvement in the quality of the genes is either caused by randomness or by the effect of natural selection. 


## Guide to run the simulation:
The Blender file can only be opened with Blender 3.0.0.

In order to access and run the program, go to the "script" section of the Blender file. Before running the code, you can enter the number of plants, sheeps and wolves that you want to have at the beginning of the simulation. Plants will randomly spawn throughout the simulation, so you don't need to have an initial amount of them (unless you want to). You can also choose how long you want the simulation to be by changing the "simulation_duration" variable. Remember that a higher number of animals and a longer duration time will lead to better results at the cost of a longer computation time. 

When you are ready, run the code. It may take quite some time before the simulation is ready. Once the animation has been fully computated, go to the "Scene" section of the Blender file and press the space-tab to start the simulation. During the animation, you can move, rotate and zoom-in or out of the scene. To stop the animation, press the space-tab. 

At the end of the simulation, if you want to visualize how the different genes of each animal have evolved over time, open , open the terminal (Window -> Terminal) and copy the whole output. Then, open the "Data.py" python script and paste it as the input of the "graph()" function. Then, run the code. You should be able to see how the different genes of each type of animal (sheep or wolf) have changed over time. You will also be able to see how the population of each group varies over time.

## More Useful Information:
The graphics of the simulation (including the map, the water, the animals and the animations) are made in Blender 3.0.0. 

The objects in the layout scene are animated by Python code in the script section of the Blender file. 

There are two python files in the script directory. "Main.py" is the script used in the simulation, "Data.py" is an optional python file useful to visualize how wolves and sheeps' attributes vary over time during the simulation. You do not need to copy any of these python files and paste them in the script section of the Blender file, since they should already be stored in the Blender file itself.



