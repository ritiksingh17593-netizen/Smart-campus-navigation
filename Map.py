import heapq
import math

# 1. Define Campus Nodes with approximate (x, y) grid coordinates from the map
nodes = {
    "Entry_Gate": (20, 10),
    "Admin_Accounts": (55, 25),
    "Canteen_Jct": (45, 48),       # High congestion during lunch
    "BMS_Jct": (62, 48),           # Junction between GF-BMS and Toilet
    "LS_Lab": (78, 48),            # START NODE (Green arrow)
    "East_Corridor_Mid": (73, 62), # Between Room 11-14 and Sport/Tut Room
    "Room_16_18_Jct": (73, 73),    # Junction south of Lab 3
    "Central_Corridor": (62, 65),  # Between Room No. 15 and Room 11-14
    "Botany_Corridor": (48, 70),   # Between Botany Lab and Room No. 5-10
    "Lab_3": (65, 76)              # GOAL NODE (Green circle)
}

# 2. Define Edges: (Neighbor, Zone_Type)
# Base distance is calculated automatically using Euclidean distance
edges = {
    "Entry_Gate": [("Canteen_Jct", "main_walkway"), ("Admin_Accounts", "main_walkway")],
    "Admin_Accounts": [("Entry_Gate", "main_walkway"), ("BMS_Jct", "admin_zone")],
    "LS_Lab": [
        ("East_Corridor_Mid", "lecture_corridor"), 
        ("BMS_Jct", "central_walkway")
    ],
    "East_Corridor_Mid": [
        ("LS_Lab", "lecture_corridor"), 
        ("Room_16_18_Jct", "lecture_corridor")
    ],
    "Room_16_18_Jct": [
        ("East_Corridor_Mid", "lecture_corridor"), 
        ("Lab_3", "lab_access"),
        ("Central_Corridor", "lecture_corridor")
    ],
    "BMS_Jct": [
        ("LS_Lab", "central_walkway"), 
        ("Central_Corridor", "central_walkway"), 
        ("Canteen_Jct", "canteen_zone"),
        ("Admin_Accounts", "admin_zone")
    ],
    "Central_Corridor": [
        ("BMS_Jct", "central_walkway"), 
        ("Lab_3", "lab_access"),
        ("Room_16_18_Jct", "lecture_corridor")
    ],
    "Canteen_Jct": [
        ("BMS_Jct", "canteen_zone"), 
        ("Botany_Corridor", "canteen_zone"),
        ("Entry_Gate", "main_walkway")
    ],
    "Botany_Corridor": [
        ("Canteen_Jct", "canteen_zone"), 
        ("Lab_3", "lab_access")
    ],
    "Lab_3": [
        ("Room_16_18_Jct", "lab_access"), 
        ("Central_Corridor", "lab_access"), 
        ("Botany_Corridor", "lab_access")
    ]
}

def euclidean_distance(node1, node2):
    x1, y1 = nodes[node1]
    x2, y2 = nodes[node2]
    return math.hypot(x2 - x1, y2 - y1)

# 3. A* Search Algorithm with Dynamic ML Multipliers
def a_star_search(start, goal, congestion_multipliers=None):
    if congestion_multipliers is None:
        # Default static baseline: all multipliers = 1.0
        congestion_multipliers = {
            "lecture_corridor": 1.0,
            "central_walkway": 1.0,
            "canteen_zone": 1.0,
            "admin_zone": 1.0,
            "main_walkway": 1.0,
            "lab_access": 1.0
        }

    # Priority queue stores tuples: (f_score, g_score, current_node, path_list)
    open_set = [(euclidean_distance(start, goal), 0, start, [start])]
    visited_g = {}

    while open_set:
        f, g, current, path = heapq.heappop(open_set)

        if current == goal:
            return path, round(g, 2)

        if current in visited_g and visited_g[current] <= g:
            continue
        visited_g[current] = g

        for neighbor, zone_type in edges.get(current, []):
            base_dist = euclidean_distance(current, neighbor)
            # Apply the ML-predicted congestion factor for that zone
            multiplier = congestion_multipliers.get(zone_type, 1.0)
            step_cost = base_dist * multiplier
            
            new_g = g + step_cost
            new_f = new_g + euclidean_distance(neighbor, goal)
            heapq.heappush(open_set, (new_f, new_g, neighbor, path + [neighbor]))

    return None, float("inf")

# --- TEST 1: Static Shortest Path (Empty hallways) ---
path_static, cost_static = a_star_search("LS_Lab", "Lab_3")
print(f"Normal Hours Route: {' -> '.join(path_static)} (Cost: {cost_static})")

# --- TEST 2: Simulated Class Change Bottleneck in Lecture Corridors ---
simulated_ml_weights = {
    "lecture_corridor": 2.2,  # Heavy crowd near Room 11-14 & Room 16-18
    "central_walkway": 1.1,   # Clearer central path
    "canteen_zone": 1.5,
    "lab_access": 1.0
}
path_dynamic, cost_dynamic = a_star_search("LS_Lab", "Lab_3", simulated_ml_weights)
print(f"Peak Lecture Traffic Route: {' -> '.join(path_dynamic)} (Cost: {cost_dynamic})")