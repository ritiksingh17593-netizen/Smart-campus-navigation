import math
import pandas as pd
import networkx as nx

# Connect directly to your two existing files
from phase1_navigation import CAMPUS_NODES, TREE_EDGES, LOOP_EDGES
from phase2_crowdpredictor import ml_model

# =====================================================================
# STEP 1: ASSIGN ZONES & UPDATE GRAPH WITH ML CROWD TIME
# Zone 0 = Gates | Zone 1 = Canteen/Society | Zone 2 = Central Spine | Zone 3 = East/BMS
# =====================================================================
def get_zone_id(node_name):
    if node_name in ["Entry Gate", "Guard Room", "J_Entry_Corner"]:
        return 0
    elif node_name in ["Canteen", "N.S.S. & Photo Copy", "Dhwani", "Back Gate", "J_Canteen_West", "J_Canteen_East"]:
        return 1
    elif node_name in ["Lab 1", "Chem & Physics (Lab 2)", "Electronics & CS Block", "Girls Common Rm & Principal", "Chem Lab (GF-3 / FF-4)", "Botany Lab (Rm 5-10)", "Research Wing & IGNOU", "J_Central_South", "J_Central_Mid", "J_North_Mid"]:
        return 2
    else:
        return 3

def build_smart_graph(day_type, time_hour):
    G = nx.Graph()

    for name, coords in CAMPUS_NODES.items():
        G.add_node(name, pos=coords)

    for u, v in TREE_EDGES + LOOP_EDGES:
        x1, y1 = CAMPUS_NODES[u]
        x2, y2 = CAMPUS_NODES[v]

        # 1. Physical Distance (meters)
        distance = round(math.hypot(x2 - x1, y2 - y1), 1)

        # 2. Ask phase2_crowdpredictor ML model for the crowd delay
        zone_u = get_zone_id(u)
        zone_v = get_zone_id(v)
        crowd_u = ml_model.predict(pd.DataFrame([[day_type, time_hour, zone_u]], columns=["Day_Type", "Time_Hour", "Zone_ID"]))[0]
        crowd_v = ml_model.predict(pd.DataFrame([[day_type, time_hour, zone_v]], columns=["Day_Type", "Time_Hour", "Zone_ID"]))[0]
        crowd_multiplier = max(crowd_u, crowd_v)

        # 3. Walking Time (seconds) = (Distance / 1.4 m/s) * ML_Crowd_Prediction
        walking_time = round((distance / 1.4) * crowd_multiplier, 1)

        G.add_edge(u, v, distance=distance, time=walking_time)

    return G

# =====================================================================
# STEP 2: RUN A* SEARCH (SHORTEST DISTANCE vs FASTEST TIME)
# =====================================================================
def distance_heuristic(u, v):
    x1, y1 = CAMPUS_NODES[u]
    x2, y2 = CAMPUS_NODES[v]
    return math.hypot(x2 - x1, y2 - y1)

def time_heuristic(u, v):
    return distance_heuristic(u, v) / 1.4

def compare_routes(start, goal, day_type, time_hour):
    G = build_smart_graph(day_type, time_hour)

    # 1. A* for Shortest Physical Distance
    path_dist = nx.astar_path(G, start, goal, heuristic=distance_heuristic, weight="distance")
    dist_m1 = sum(G[path_dist[i]][path_dist[i+1]]["distance"] for i in range(len(path_dist)-1))
    time_s1 = sum(G[path_dist[i]][path_dist[i+1]]["time"] for i in range(len(path_dist)-1))

    # 2. A* for Fastest ML-Predicted Time
    path_time = nx.astar_path(G, start, goal, heuristic=time_heuristic, weight="time")
    dist_m2 = sum(G[path_time[i]][path_time[i+1]]["distance"] for i in range(len(path_time)-1))
    time_s2 = sum(G[path_time[i]][path_time[i+1]]["time"] for i in range(len(path_time)-1))

    clean_dist_path = [n for n in path_dist if not n.startswith("J_")]
    clean_time_path = [n for n in path_time if not n.startswith("J_")]

    print(f"\n=== ROUTE FROM '{start}' TO '{goal}' ===")
    print("\n1. SHORTEST DISTANCE ROUTE (Ignores Crowd):")
    print("   " + " -> ".join(clean_dist_path))
    print(f"   Distance: {round(dist_m1, 1)} m | Time in Crowd: {round(time_s1, 1)} sec")

    print("\n2. FASTEST TIME ROUTE (Uses ML Crowd Prediction):")
    print("   " + " -> ".join(clean_time_path))
    print(f"   Distance: {round(dist_m2, 1)} m | Time on Bypass: {round(time_s2, 1)} sec")

if __name__ == "__main__":
    # Test at 12:50 PM Weekday Lunch Rush (Day_Type = 0, Time_Hour = 12.85)
    compare_routes("Entry Gate", "BMS Dept & R.Lab (Rm 24)", day_type=0, time_hour=12.85)
