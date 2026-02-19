from core.sheets_service import get_pilots, get_drones, get_missions
from core.assignment_engine import calculate_pilot_cost
from datetime import datetime
import logging


# ===============================
# DATE OVERLAP CHECK
# ===============================

def dates_overlap(start1, end1, start2, end2):

    return start1 <= end2 and start2 <= end1


# ===============================
# PILOT DOUBLE BOOKING CHECK
# ===============================

def check_pilot_double_booking(pilot_row, mission_row):

    try:

        if pilot_row["current_assignment"] == "":
            return None

        missions = get_missions()

        assigned_mission = missions[
            missions["project_id"] == pilot_row["current_assignment"]
        ]

        if assigned_mission.empty:
            return None

        assigned_mission = assigned_mission.iloc[0]

        start1 = datetime.strptime(
            mission_row["start_date"], "%Y-%m-%d"
        )
        end1 = datetime.strptime(
            mission_row["end_date"], "%Y-%m-%d"
        )

        start2 = datetime.strptime(
            assigned_mission["start_date"], "%Y-%m-%d"
        )
        end2 = datetime.strptime(
            assigned_mission["end_date"], "%Y-%m-%d"
        )

        if dates_overlap(start1, end1, start2, end2):

            return "Pilot double-booked during mission dates"

        return None

    except Exception as e:

        logging.error(f"Pilot double booking check error: {e}")

        return "Pilot booking check failed"


# ===============================
# DRONE DOUBLE BOOKING CHECK
# ===============================

def check_drone_double_booking(drone_row, mission_row):

    try:

        if drone_row["current_assignment"] == "":
            return None

        missions = get_missions()

        assigned_mission = missions[
            missions["project_id"] == drone_row["current_assignment"]
        ]

        if assigned_mission.empty:
            return None

        assigned_mission = assigned_mission.iloc[0]

        start1 = datetime.strptime(
            mission_row["start_date"], "%Y-%m-%d"
        )
        end1 = datetime.strptime(
            mission_row["end_date"], "%Y-%m-%d"
        )

        start2 = datetime.strptime(
            assigned_mission["start_date"], "%Y-%m-%d"
        )
        end2 = datetime.strptime(
            assigned_mission["end_date"], "%Y-%m-%d"
        )

        if dates_overlap(start1, end1, start2, end2):

            return "Drone double-booked during mission dates"

        return None

    except Exception as e:

        logging.error(f"Drone double booking check error: {e}")

        return "Drone booking check failed"


# ===============================
# BUDGET CHECK
# ===============================

def check_budget(pilot_row, mission_row):

    try:

        cost = calculate_pilot_cost(pilot_row, mission_row)

        budget = mission_row["mission_budget_inr"]

        if cost > budget:

            return f"Pilot cost exceeds mission budget ({cost} > {budget})"

        return None

    except Exception as e:

        logging.error(f"Budget check error: {e}")

        return "Budget check failed"


# ===============================
# DRONE MAINTENANCE CHECK
# ===============================

def check_drone_maintenance(drone_row):

    try:

        maintenance_due = datetime.strptime(
            drone_row["maintenance_due"], "%Y-%m-%d"
        )

        today = datetime.today()

        if maintenance_due <= today:

            return "Drone requires maintenance"

        return None

    except Exception as e:

        logging.error(f"Maintenance check error: {e}")

        return "Maintenance check failed"


# ===============================
# WEATHER COMPATIBILITY CHECK
# ===============================

def check_weather(drone_row, mission_row):

    try:

        if mission_row["weather_forecast"].lower() == "rainy":

            if "IP43" not in drone_row["weather_resistance"]:

                return "Drone not compatible with rainy weather"

        return None

    except Exception as e:

        logging.error(f"Weather check error: {e}")

        return "Weather compatibility check failed"


# ===============================
# MAIN CONFLICT DETECTOR
# ===============================

def detect_conflicts(project_id, pilot_id, drone_id):

    try:

        pilots = get_pilots()
        drones = get_drones()
        missions = get_missions()

        pilot = pilots[pilots["pilot_id"] == pilot_id].iloc[0]
        drone = drones[drones["drone_id"] == drone_id].iloc[0]
        mission = missions[missions["project_id"] == project_id].iloc[0]

        conflicts = []

        # Pilot checks
        conflict = check_pilot_double_booking(pilot, mission)
        if conflict:
            conflicts.append(conflict)

        conflict = check_budget(pilot, mission)
        if conflict:
            conflicts.append(conflict)

        # Drone checks
        conflict = check_drone_double_booking(drone, mission)
        if conflict:
            conflicts.append(conflict)

        conflict = check_drone_maintenance(drone)
        if conflict:
            conflicts.append(conflict)

        conflict = check_weather(drone, mission)
        if conflict:
            conflicts.append(conflict)

        if not conflicts:

            logging.info("No conflicts detected")

            return "No conflicts detected"

        logging.warning(f"Conflicts detected: {conflicts}")

        return conflicts

    except Exception as e:

        logging.error(f"Conflict detection failed: {e}")

        return "Conflict detection failed"
