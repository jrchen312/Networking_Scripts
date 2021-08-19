import json
from pprint import pprint

c = open('./cortez_network.json')
G = json.load(c)

#start = input("Starting node: ")
#end = input("Ending node: ")
start = "CZPLADMIN-SW4"
#end = "CZMCC111-SW3"
end = "CZPLSOUTHSUB-SW1"

print("Starting location: " + start)
print("Ending location: " + end)

assert(start in G and end in G)
print("Finding best path:")


#get the neighbors of the first node as the syntax of the first node is different
que = [ [ G[start]["neighbors"][i] ] for i in range(len(G[start]["neighbors"]))]
#print(que)
G[start]["marked"] = True

valid_paths = []

while(que != []):
    first_path = que.pop(0)
    #print(G[first['name']]) # first
    first = first_path[-1]

    
    if first['name'] == end:
        #print("We are here.")
        #pprint(first_path)
        #print(len(first_path))
        #break
        valid_paths.append(first_path)

    #if not G[first['name']]['marked']:
    G[first['name']]['marked'] = True;
    
    neighbors = G[first['name']]['neighbors']
    
    for neighbor in neighbors:
        if neighbor.get("NOTE", None) == None and not G[neighbor['name']]['marked']:
            temp = list(first_path)
            temp.append(neighbor)
            que.append(temp)


#print("unable to find if no gigantic list was printed. ")
pprint(valid_paths)
for path in valid_paths:
    print(len(path))