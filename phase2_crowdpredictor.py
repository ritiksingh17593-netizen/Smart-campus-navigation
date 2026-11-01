import pandas as pd
from sklearn.tree import DecisionTreeRegressor

# =====================================================================
# 1. CREATE A SIMPLE TRAINING DATASET BASED ON YOUR COLLEGE SCHEDULE
# Day_Type: 0 = Weekday (Mon-Fri), 1 = Saturday (Light Rush), 2 = Sunday (Holiday)
# Time_Hour: 8.75 = 8:45 AM, 12.75 = 12:45 PM (Lunch), 17.0 = 5:00 PM
# Zone_ID: 0 = Gates, 1 = Canteen/Society, 2 = Central Spine, 3 = East/BMS/Lawns
# Crowd_Multiplier: 1.0 = Empty/Normal speed, 2.5 = 2.5x slower walking time
# =====================================================================
TRAINING_DATA = [
    # --- WEEKDAYS (Mon-Fri: Day_Type = 0) ---
    # 8:45 AM Opening Rush (Gates are busy, Canteen & Lawns are empty)
    [0, 8.75, 0, 2.0], [0, 8.75, 1, 1.1], [0, 8.75, 2, 1.4], [0, 8.75, 3, 1.1],
    # 10:30 AM Normal Class Hours (Light movement everywhere)
    [0, 10.50, 0, 1.1], [0, 10.50, 1, 1.2], [0, 10.50, 2, 1.3], [0, 10.50, 3, 1.0],
    # 12:45 PM - 1:00 PM Peak Lunch Rush (Canteen & Central Spine jammed!)
    [0, 12.85, 0, 1.3], [0, 12.85, 1, 2.6], [0, 12.85, 2, 1.9], [0, 12.85, 3, 1.1],
    # 3:00 PM Afternoon Classes
    [0, 15.00, 0, 1.1], [0, 15.00, 1, 1.3], [0, 15.00, 2, 1.3], [0, 15.00, 3, 1.0],
    # 5:00 PM College Dispersal Rush (Gates & Academic corridors busy)
    [0, 17.00, 0, 2.2], [0, 17.00, 1, 1.4], [0, 17.00, 2, 1.7], [0, 17.00, 3, 1.2],

    # --- SATURDAYS (Light Rush: Day_Type = 1) ---
    [1, 8.75, 0, 1.3], [1, 8.75, 1, 1.0], [1, 8.75, 2, 1.1], [1, 8.75, 3, 1.0],
    [1, 12.85, 0, 1.1], [1, 12.85, 1, 1.4], [1, 12.85, 2, 1.2], [1, 12.85, 3, 1.0],
    [1, 17.00, 0, 1.3], [1, 17.00, 1, 1.1], [1, 17.00, 2, 1.2], [1, 17.00, 3, 1.0],

    # --- SUNDAYS (Holiday - Zero Rush Everywhere: Day_Type = 2) ---
    [2, 8.75, 0, 1.0], [2, 8.75, 1, 1.0], [2, 8.75, 2, 1.0], [2, 8.75, 3, 1.0],
    [2, 12.85, 0, 1.0], [2, 12.85, 1, 1.0], [2, 12.85, 2, 1.0], [2, 12.85, 3, 1.0],
    [2, 17.00, 0, 1.0], [2, 17.00, 1, 1.0], [2, 17.00, 2, 1.0], [2, 17.00, 3, 1.0],
]

columns = ["Day_Type", "Time_Hour", "Zone_ID", "Crowd_Multiplier"]
df = pd.DataFrame(TRAINING_DATA, columns=columns)

# =====================================================================
# 2. TRAIN THE MACHINE LEARNING MODEL
# =====================================================================
X = df[["Day_Type", "Time_Hour", "Zone_ID"]]  # Input Features
y = df["Crowd_Multiplier"]                    # Target Output to Predict

ml_model = DecisionTreeRegressor(max_depth=5, random_state=42)
ml_model.fit(X, y)

# =====================================================================
# 3. TEST THE ML PREDICTIONS FOR CANTEEN (Zone 1) vs EAST BMS BYPASS (Zone 3)
# =====================================================================
test_cases = pd.DataFrame([
    [0, 12.85, 1],  # Weekday at 12:50 PM in Canteen (Zone 1)
    [0, 12.85, 3],  # Weekday at 12:50 PM in East BMS Bypass (Zone 3)
    [1, 12.85, 1],  # Saturday at 12:50 PM in Canteen (Zone 1)
    [2, 12.85, 1],  # Sunday at 12:50 PM in Canteen (Zone 1)
], columns=["Day_Type", "Time_Hour", "Zone_ID"])

predictions = ml_model.predict(test_cases)

print("=== ML CROWD PREDICTOR TEST ===")
print(f"1. Weekday 12:50 PM (Canteen Zone 1):      {predictions[0]:.2f}x delay")
print(f"2. Weekday 12:50 PM (East/BMS Zone 3):     {predictions[1]:.2f}x delay")
print(f"3. Saturday 12:50 PM (Canteen Zone 1):     {predictions[2]:.2f}x delay")
print(f"4. Sunday Holiday 12:50 PM (Canteen):      {predictions[3]:.2f}x delay")
