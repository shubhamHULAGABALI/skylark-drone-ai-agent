from ai.decision_engine import decide_best_assignment
from core.reassignment_engine import urgent_reassign
import logging


# ===============================
# AGENT CONTROLLER
# ===============================

class DroneOpsAgent:


    def assign_mission(self, project_id):

        result = decide_best_assignment(project_id)

        if result["status"] == "success":

            return f"""
Assignment Successful

Pilot: {result['pilot_name']} ({result['pilot_id']})
Drone: {result['drone_model']} ({result['drone_id']})

Reason:
{result['explanation']}
"""

        return f"Assignment Failed: {result['message']}"


    def reassign_mission(self, project_id):

        result = urgent_reassign(project_id)

        logging.info(f"Reassignment attempted for {project_id}")

        return result


    def process_command(self, command):

        parts = command.lower().split()

        if parts[0] == "assign":

            project_id = parts[1].upper()

            return self.assign_mission(project_id)

        elif parts[0] == "reassign":

            project_id = parts[1].upper()

            return self.reassign_mission(project_id)

        else:

            return "Unknown command"
