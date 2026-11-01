import networkx as nx
import matplotlib.pyplot as plt

# Connect to your files
from phase1_navigation import CAMPUS_NODES, TREE_EDGES, LOOP_EDGES
from phase3_astar import build_smart_graph, distance_heuristic, time_heuristic

def plot_route_comparison(start, goal, day_type=0, time_hour=12.85):
    G = build_smart_graph(day_type, time_hour)
    pos = nx.get_node_attributes(G, "pos")

    # Get Shortest Distance Path & Fastest ML Time Path
    path_dist = nx.astar_path(G, start, goal, heuristic=distance_heuristic, weight="distance")
    dist_m1 = sum(G[path_dist[i]][path_dist[i+1]]["distance"] for i in range(len(path_dist)-1))
    time_s1 = sum(G[path_dist[i]][path_dist[i+1]]["time"] for i in range(len(path_dist)-1))

    path_time = nx.astar_path(G, start, goal, heuristic=time_heuristic, weight="time")
    dist_m2 = sum(G[path_time[i]][path_time[i+1]]["distance"] for i in range(len(path_time)-1))
    time_s2 = sum(G[path_time[i]][path_time[i+1]]["time"] for i in range(len(path_time)-1))

    edges_dist = list(zip(path_dist[:-1], path_dist[1:]))
    edges_time = list(zip(path_time[:-1], path_time[1:]))

    plt.figure(figsize=(12, 10))

    # Draw background walkways in light gray
    nx.draw_networkx_edges(G, pos, edgelist=TREE_EDGES + LOOP_EDGES, width=1.5, edge_color="#CBD5E1")

    # Draw Shortest Distance Path (Red Dashed)
    nx.draw_networkx_edges(
        G, pos, edgelist=edges_dist, width=3.5, edge_color="#EF4444", style="dashed",
        label=f"Shortest Distance: {dist_m1:.0f}m | {time_s1:.0f}s (Hits Lunch Crowd)"
    )

    # Draw Fastest ML Route (Green Solid)
    nx.draw_networkx_edges(
        G, pos, edgelist=edges_time, width=4.0, edge_color="#16A34A",
        label=f"Fastest ML Route: {dist_m2:.0f}m | {time_s2:.0f}s (Saves {time_s1 - time_s2:.0f}s!)"
    )

    landmarks = [n for n in G.nodes() if not n.startswith("J_")]
    junctions = [n for n in G.nodes() if n.startswith("J_")]

    node_colors = [
        "#FDE047" if n == start else ("#86EFAC" if n == goal else ("#FCA5A5" if n == "Canteen" else "#E0F2FE"))
        for n in landmarks
    ]

    nx.draw_networkx_nodes(G, pos, nodelist=landmarks, node_color=node_colors, node_size=520, edgecolors="#1E293B", linewidths=1.5)
    nx.draw_networkx_nodes(G, pos, nodelist=junctions, node_color="#FDBA74", node_shape="s", node_size=140, edgecolors="#9A3412", label="Corridor Junction (J_)")

    landmark_labels = {n: n for n in landmarks}
    nx.draw_networkx_labels(G, pos, labels=landmark_labels, font_size=8, font_weight="bold")

    plt.title(f"Smart Campus A* Navigation (12:50 PM Lunch Rush)\n{start} → {goal}", fontsize=13, fontweight="bold")
    plt.legend(loc="lower right", fontsize=9.5, frameon=True, facecolor="white", framealpha=0.9)
    plt.grid(True, linestyle=":", alpha=0.4)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Get the list of 20 actual campus landmarks (ignoring J_ junctions)
    landmarks = [node for node in CAMPUS_NODES.keys() if not node.startswith("J_")]

    print("\n" + "="*50)
    print("   SMART CAMPUS AI-ML NAVIGATION SYSTEM")
    print("="*50)

    # 1. Show all 20 Campus Locations with numbers
    for i, place in enumerate(landmarks, 1):
        print(f"  {i:2d}. {place}")

    # 2. Let the user/teacher pick ANY Start and Destination
    start_num = int(input("\nEnter Start Location Number (1-20): "))
    goal_num  = int(input("Enter Destination Number (1-20):    "))

    start_place = landmarks[start_num - 1]
    goal_place  = landmarks[goal_num - 1]

    # 3. Let the user/teacher pick ANY Day
    print("\nSelect Day Type:")
    print("  0 = Weekday (Mon-Fri) | 1 = Saturday (Light Rush) | 2 = Sunday (Holiday)")
    day_choice = int(input("Enter Day (0, 1, or 2): "))

    # 4. Let the user/teacher type ANY Time in normal HH:MM format (24-hr)
    time_str = input("\nEnter Time in 24-hr format (e.g., 08:45, 10:30, 12:50, 17:00): ")
    hours, minutes = map(int, time_str.split(":"))
    decimal_time = round(hours + (minutes / 60.0), 2)

    print(f"\nCalculating smartest route from '{start_place}' to '{goal_place}' at {time_str}...")
    plot_route_comparison(start_place, goal_place, day_type=day_choice, time_hour=decimal_time)
