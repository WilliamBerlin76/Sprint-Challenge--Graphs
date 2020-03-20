from room import Room
from player import Player
from world import World
import sys
import random
from ast import literal_eval
sys.path.append('../graph')
from util import Queue

sys.setrecursionlimit(1000000)
# Load world
world = World()


# You may uncomment the smaller graphs for development and testing purposes.
map_file = "maps/test_line.txt"
map_file = "maps/test_cross.txt"
map_file = "maps/test_loop.txt"
map_file = "maps/test_loop_fork.txt"
map_file = "maps/main_maze.txt"

# Loads the map into a dictionary
room_graph=literal_eval(open(map_file, "r").read())
world.load_graph(room_graph)

# Print an ASCII map
world.print_rooms()

player = Player(world.starting_room)

# Fill this out with directions to walk
# traversal_path = ['n', 'n']
traversal_path = []
################ PLANNING ###################
# For the graph, make dicionary, room number is key, value is adjacency list with room exits
# adjacency list by default stores a '?' for neighbors of unknown room values
# traversal is complete when all rooms have a key in dict, and no values are '?' in the adjacency list

# Start by writing an algorithm that picks a random unexplored direction from the player's current room, 
# travels and logs that direction, then loops. This should cause your player to walk a depth-first traversal. 
# When you reach a dead-end (i.e. a room with no unexplored paths), 
# walk back to the nearest room that does contain an unexplored path.

# use BFS to find closest room with a "?" in the adjacency list
adj_rooms= {}
# initialize adjacency list with an empty dict for each room
for i in range(len(room_graph)):
    adj_rooms[i] = {}

opposites = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'} # used to record previous room in dft

def dft_maze(starting_room):
    # pick random unexplored direction
    # travel that direction, log it, and loop
    # when reaching dead end, use bfs to find closest room with unexplored neighbors

    prev_dir = None
    def recurse_helper(cur_room, prev):
        if adj_rooms[cur_room.id] == {}:
            exits = cur_room.get_exits()
            for i in range(len(exits)):
                if prev is not None:
                    if exits[i] == prev[1]:
                        adj_rooms[cur_room.id][exits[i]] = prev[0]
                    else:
                        adj_rooms[cur_room.id][exits[i]] = '?'
                else:
                    adj_rooms[cur_room.id][exits[i]] = '?'
        elif prev is not None:
            if adj_rooms[cur_room.id][prev[1]] == '?':
                adj_rooms[cur_room.id][prev[1]] = prev[0]

        unexplored = set()
        # create list of viable directions to move
        for key in adj_rooms[cur_room.id]:
            if adj_rooms[cur_room.id][key] == '?':
                unexplored.add(key)
        # check if there are unexplored neighbors
        if len(unexplored) == 0:
            # run bfs to find shortest path to room with unexplored neighbors
            return bfs_maze(cur_room)
       
        next_dir = random.choice(tuple(unexplored)) # choose next move
        traversal_path.append(next_dir) # add to path
        player.travel(next_dir) # travel that way
        next_room = player.current_room # record next room
        adj_rooms[cur_room.id][next_dir] = next_room.id # update adjacency list
        return recurse_helper(next_room, [cur_room.id, opposites[next_dir]]) # loop, passing prev room and direction as second arg
    
    recurse_helper(starting_room, prev_dir)

def bfs_maze(cur_room):
    # BFS function, use to find shortest path to room with unknown neighbors
    # this should record the path, add it to traversal path
    q = Queue()
    available_directions = player.current_room.get_exits()
    # initialize queue with all possible directions
    for i in range(len(available_directions)):
        q.enqueue([available_directions[i]])
        
    visited = set() # store room id

    while q.size() > 0:
        path = q.dequeue()
        # print('PATH', path)
        temp_room = cur_room.id
        for i in range(len(path)):
            temp_room = adj_rooms[temp_room][path[i]]

        if temp_room not in visited:
            visited.add(temp_room) 

            for direciton in adj_rooms[temp_room]:
                if adj_rooms[temp_room][direciton] == '?':
                    for i in range(len(path)):
                        player.travel(path[i])
                        traversal_path.append(path[i])
                        return dft_maze(player.current_room)

                path_copy = path.copy()
                path_copy.append(direciton)
                q.enqueue(path_copy)
                    

# Traverse the maze
dft_maze(player.current_room)
    

print(traversal_path)
# TRAVERSAL TEST
visited_rooms = set()
player.current_room = world.starting_room
visited_rooms.add(player.current_room)

for move in traversal_path:
    player.travel(move)
    visited_rooms.add(player.current_room)

if len(visited_rooms) == len(room_graph):
    print(f"TESTS PASSED: {len(traversal_path)} moves, {len(visited_rooms)} rooms visited")
else:
    print("TESTS FAILED: INCOMPLETE TRAVERSAL")
    print(f"{len(room_graph) - len(visited_rooms)} unvisited rooms")



#######
# UNCOMMENT TO WALK AROUND
#######
# player.current_room.print_room_description(player)
# while True:
#     cmds = input("-> ").lower().split(" ")
#     if cmds[0] in ["n", "s", "e", "w"]:
#         player.travel(cmds[0], True)
#     elif cmds[0] == "q":
#         break
#     else:
#         print("I did not understand that command.")
