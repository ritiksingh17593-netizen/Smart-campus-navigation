import math
import networkx as nx
import matplotlib.pyplot as plt

# =====================================================================
# 1. NODES: 20 Landmarks + 10 Corridor Corner Junctions (J_)
# Coordinates aligned to horizontal & vertical corridors so paths 
# never cut diagonally through buildings.
# =====================================================================
CAMPUS_NODES = {
    # --- 20 Main Campus Landmarks ---
    "Entry Gate":                  (20, 15),
    "Guard Room":                  (20, 35),
    "Back Gate":                   (5, 175),
    "Lawn 1":                      (70, 35),
    "Sports Ground & Badminton":   (180, 150),

    "Dhwani":                      (20, 95),
    "N.S.S. & Photo Copy":         (20, 145),
    "Canteen":                     (60, 175),
    "Girls Common Rm & Principal": (95, 130),

    "Admin Block & Accounts":      (105, 85),
    "Library & Web Center":        (150, 85),

    "BMS Dept & R.Lab (Rm 24)":    (120, 175),
    "Lab 1":                       (55, 85),
    "Chem & Physics (Lab 2)":      (55, 110),
    "Electronics & CS Block":      (60, 150),
    "L.S. Lab & Phy Lab 3":        (150, 150),
    "Chem Lab (GF-3 / FF-4)":      (20, 215),
    "Botany Lab (Rm 5-10)":        (95, 215),
    "Research Wing & IGNOU":       (20, 255),
    "Lab 3 & Seminar Block":       (125, 255),

    # --- 10 Corridor Corner Junctions (From Your Route Tree) ---
    "J_Entry_Corner":              (55, 35),
    "J_Admin_South":               (105, 35),
    "J_Central_South":             (95, 110),
    "J_Central_Mid":               (95, 150),
    "J_Canteen_West":              (20, 175),
    "J_Canteen_East":              (95, 175),
    "J_East_South":                (150, 115),
    "J_East_Mid":                  (150, 175),
    "J_North_Mid":                 (125, 215),
    "J_North_East":                (150, 215)
}

# =====================================================================
# 2. MAIN TREE CORRIDORS (Follows your Route Tree diagram)
# =====================================================================
TREE_EDGES = [
    # Entry & South Split
    ("Entry Gate", "Guard Room"),
    ("Guard Room", "J_Entry_Corner"),
    ("J_Entry_Corner", "Lawn 1"),
    ("Lawn 1", "J_Admin_South"),

    # West Society Corridor (Straight vertical line at x=20)
    ("Guard Room", "Dhwani"),
    ("Dhwani", "N.S.S. & Photo Copy"),
    ("N.S.S. & Photo Copy", "J_Canteen_West"),
    ("J_Canteen_West", "Back Gate"),
    ("J_Canteen_West", "Canteen"),
    ("J_Canteen_West", "Chem Lab (GF-3 / FF-4)"),
    ("Chem Lab (GF-3 / FF-4)", "Research Wing & IGNOU"),

    # Central Lab Spine
    ("J_Entry_Corner", "Lab 1"),
    ("Lab 1", "Chem & Physics (Lab 2)"),
    ("Chem & Physics (Lab 2)", "J_Central_South"),
    ("J_Central_South", "Girls Common Rm & Principal"),
    ("Girls Common Rm & Principal", "J_Central_Mid"),
    ("J_Central_Mid", "Electronics & CS Block"),
    ("J_Central_Mid", "J_Canteen_East"),
    ("J_Canteen_East", "Botany Lab (Rm 5-10)"),

    # East Admin & BMS Corridor (Straight vertical line at x=150)
    ("J_Admin_South", "Admin Block & Accounts"),
    ("Admin Block & Accounts", "Library & Web Center"),
    ("Library & Web Center", "J_East_South"),
    ("J_East_South", "L.S. Lab & Phy Lab 3"),
    ("L.S. Lab & Phy Lab 3", "Sports Ground & Badminton"),
    ("L.S. Lab & Phy Lab 3", "J_East_Mid"),
    ("J_East_Mid", "BMS Dept & R.Lab (Rm 24)"),
    ("J_East_Mid", "J_North_East"),
    ("J_North_East", "J_North_Mid"),
    ("J_North_Mid", "Lab 3 & Seminar Block")
]

# =====================================================================
# 3. ALTERNATIVE CORRIDOR CONNECTIONS (For A* Crowd Detours)
# =====================================================================
LOOP_EDGES = [
    ("Lab 1", "Admin Block & Accounts"),
    ("J_Central_South", "Admin Block & Accounts"),
    ("Canteen", "Electronics & CS Block"),
    ("Canteen", "J_Canteen_East"),
    ("J_Canteen_East", "BMS Dept & R.Lab (Rm 24)"),
    ("Chem Lab (GF-3 / FF-4)", "Botany Lab (Rm 5-10)"),
    ("Botany Lab (Rm 5-10)", "J_North_Mid")
]

WALK_SPEED = 1.4  # meters per second

def build_corridor_graph():
    G = nx.Graph()
    for node, coords in CAMPUS_NODES.items():
        G.add_node(node, pos=coords, is_junction=node.startswith("J_"))

    all_edges = [(u, v, "tree") for u, v in TREE_EDGES] + [(u, v, "loop") for u, v in LOOP_EDGES]
    for u, v, edge_type in all_edges:
        x1, y1 = CAMPUS_NODES[u]
        x2, y2 = CAMPUS_NODES[v]
        distance = round(math.hypot(x2 - x1, y2 - y1), 1)
        base_time = round(distance / WALK_SPEED, 1)
        G.add_edge(u, v, distance=distance, base_time=base_time, edge_type=edge_type)

    return G

# =====================================================================
# 4. PLOT THE ORTHOGONAL CORRIDOR GRAPH
# =====================================================================
G_campus = build_corridor_graph()
pos = nx.get_node_attributes(G_campus, "pos")

plt.figure(figsize=(12, 10))

# Separate Landmarks vs. Orange J_ Junctions
landmarks = [n for n in G_campus.nodes() if not n.startswith("J_")]
junctions = [n for n in G_campus.nodes() if n.startswith("J_")]

landmark_colors = [
    "#FCA5A5" if n == "Entry Gate" else ("#86EFAC" if "BMS" in n else "#BAE6FD")
    for n in landmarks
]

# Draw Landmarks (Circles) and J_ Junctions (Orange Squares matching your tree)
nx.draw_networkx_nodes(G_campus, pos, nodelist=landmarks, node_color=landmark_colors, node_size=500, edgecolors="#1E293B")
nx.draw_networkx_nodes(G_campus, pos, nodelist=junctions, node_color="#FDBA74", node_shape="s", node_size=220, edgecolors="#9A3412", label="Corridor Corner Junction (J_)")

# Draw Main Tree Edges (Blue) & Loop Edges (Dashed Green)
nx.draw_networkx_edges(G_campus, pos, edgelist=TREE_EDGES, width=2.2, edge_color="#2563EB", label="Main Tree Corridors")
nx.draw_networkx_edges(G_campus, pos, edgelist=LOOP_EDGES, width=2.0, edge_color="#16A34A", style="dashed", label="Alternative Cross-Corridors")

nx.draw_networkx_labels(G_campus, pos, font_size=7.5, font_weight="bold")

plt.title("Step 2.2: Campus Corridor Graph (Zero Building Collisions)", fontsize=13, fontweight="bold")
plt.legend(loc="lower right", fontsize=9)
plt.grid(True, linestyle=":", alpha=0.4)
plt.tight_layout()
plt.show()
