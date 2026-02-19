from core.assignment_engine import match_resources
from core.conflict_detector import detect_conflicts
from core.sheets_service import update_pilot_status
import logging


# ===============================
# INTELLIGENT URGENT REASSIGNMENT
# ===============================

def urgent_reassign(project_id):

    try:

        # Get ranked pilots and drones
        result = match_resources(project_id)

        if isinstance(result, str):

            logging.error("Mission not found during reassignment")

            return result

        pilots = result["pilots"]
        drones = result["drones"]

        if pilots.empty:

            logging.warning("No pilots available for reassignment")

            return "No suitable pilots found"

        if drones.empty:

            logging.warning("No drones available for reassignment")

            return "No suitable drones found"

        drone = drones.iloc[0]
        drone_id = drone["drone_id"]

        # Find best conflict-free pilot
        for _, pilot in pilots.iterrows():

            pilot_id = pilot["pilot_id"]

            conflict_result = detect_conflicts(
                project_id,
                pilot_id,
                drone_id
            )

            if conflict_result == "No conflicts detected":

                # Assign pilot
                update_pilot_status(pilot_id, "Assigned")

                logging.info(
                    f"Pilot {pilot_id} assigned to project {project_id}"
                )

                return (
                    f"Pilot {pilot['name']} ({pilot_id}) successfully "
                    f"assigned to project {project_id}"
                )

        logging.warning("All pilots have conflicts")

        return "No conflict-free pilot available"

    except Exception as e:

        logging.error(f"Reassignment failed: {e}")

        return "Reassignment failed"
