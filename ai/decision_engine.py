from core.assignment_engine import match_resources
from core.conflict_detector import detect_conflicts
import logging


# ===============================
# DECISION ENGINE
# ===============================

def decide_best_assignment(project_id):

    try:

        result = match_resources(project_id)

        if isinstance(result, str):

            return {
                "status": "error",
                "message": result
            }

        pilots = result["pilots"]
        drones = result["drones"]

        if pilots.empty:

            return {
                "status": "error",
                "message": "No suitable pilots found"
            }

        if drones.empty:

            return {
                "status": "error",
                "message": "No suitable drones found"
            }

        drone = drones.iloc[0]
        drone_id = drone["drone_id"]

        # Find conflict-free pilot
        for _, pilot in pilots.iterrows():

            pilot_id = pilot["pilot_id"]

            conflict = detect_conflicts(
                project_id,
                pilot_id,
                drone_id
            )

            if conflict == "No conflicts detected":

                explanation = f"""
Pilot {pilot['name']} selected because:
- Skill matches mission requirement
- Located in mission city
- High assignment score ({pilot['score']})
- No scheduling conflicts

Drone {drone['model']} selected because:
- Available in mission location
- Weather compatible
"""

                logging.info(
                    f"Decision made: Pilot {pilot_id}, Drone {drone_id}"
                )

                return {
                    "status": "success",
                    "pilot_id": pilot_id,
                    "pilot_name": pilot["name"],
                    "drone_id": drone_id,
                    "drone_model": drone["model"],
                    "explanation": explanation
                }

        return {
            "status": "error",
            "message": "No conflict-free assignment possible"
        }

    except Exception as e:

        logging.error(f"Decision engine error: {e}")

        return {
            "status": "error",
            "message": "Decision failed"
        }
