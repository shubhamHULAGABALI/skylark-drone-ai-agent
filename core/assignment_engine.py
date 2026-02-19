from core.sheets_service import get_pilots, get_drones, get_missions
from datetime import datetime
import logging


# ===============================
# COST CALCULATION
# ===============================

def calculate_pilot_cost(pilot_row, mission_row):

    try:

        start = datetime.strptime(mission_row["start_date"], "%Y-%m-%d")
        end = datetime.strptime(mission_row["end_date"], "%Y-%m-%d")

        days = (end - start).days + 1

        daily_rate = pilot_row["daily_rate_inr"]

        return days * daily_rate

    except Exception as e:

        logging.error(f"Cost calculation error: {e}")

        return float("inf")


# ===============================
# PILOT SCORING SYSTEM
# ===============================

def score_pilot(pilot_row, mission_row):

    score = 0

    try:

        # Skill match
        if mission_row["required_skills"].lower() in str(pilot_row["skills"]).lower():
            score += 50

        # Location match
        if pilot_row["location"] == mission_row["location"]:
            score += 30

        # Availability bonus
        if pilot_row["status"] == "Available":
            score += 20

        # Cost penalty (lower cost preferred)
        cost = calculate_pilot_cost(pilot_row, mission_row)

        score -= cost / 1000

    except Exception as e:

        logging.error(f"Pilot scoring error: {e}")

    return score


# ===============================
# FIND BEST PILOTS
# ===============================

def find_best_pilots(mission_row):

    try:

        pilots = get_pilots()

        if pilots.empty:

            logging.warning("Pilot database empty")

            return pilots

        # STRICT FILTER: available pilots
        filtered = pilots[
            (pilots["status"] == "Available") &
            (pilots["skills"].str.contains(
                mission_row["required_skills"],
                case=False,
                na=False
            )) &
            (pilots["location"] == mission_row["location"])
        ]

        # FALLBACK: suggest best unavailable pilots
        if filtered.empty:

            logging.warning("No available pilots. Using fallback suggestion.")

            fallback = pilots[
                (pilots["skills"].str.contains(
                    mission_row["required_skills"],
                    case=False,
                    na=False
                )) &
                (pilots["location"] == mission_row["location"])
            ]

            if fallback.empty:

                logging.warning("No fallback pilots found")

                return fallback

            fallback = fallback.copy()

            fallback["score"] = fallback.apply(
                lambda pilot: score_pilot(pilot, mission_row),
                axis=1
            )

            fallback = fallback.sort_values(
                by="score",
                ascending=False
            )

            return fallback

        # NORMAL SCORING
        filtered = filtered.copy()

        filtered["score"] = filtered.apply(
            lambda pilot: score_pilot(pilot, mission_row),
            axis=1
        )

        filtered = filtered.sort_values(
            by="score",
            ascending=False
        )

        logging.info("Available pilots ranked successfully")

        return filtered

    except Exception as e:

        logging.error(f"Pilot ranking error: {e}")

        return get_pilots().iloc[0:0]


# ===============================
# FIND AVAILABLE DRONES
# ===============================

def find_available_drones(location, weather):

    try:

        drones = get_drones()

        if drones.empty:

            logging.warning("Drone database empty")

            return drones

        filtered = drones[
            (drones["status"] == "Available") &
            (drones["location"] == location)
        ]

        if weather.lower() == "rainy":

            filtered = filtered[
                filtered["weather_resistance"].str.contains(
                    "IP43",
                    na=False
                )
            ]

        logging.info("Drone filtering complete")

        return filtered

    except Exception as e:

        logging.error(f"Drone filtering error: {e}")

        return get_drones().iloc[0:0]


# ===============================
# MAIN MATCHING FUNCTION
# ===============================

def match_resources(project_id):

    try:

        missions = get_missions()

        if missions.empty:

            logging.error("Mission database empty")

            return "Mission database empty"

        mission = missions[missions["project_id"] == project_id]

        if mission.empty:

            logging.error(f"Mission {project_id} not found")

            return "Mission not found"

        mission = mission.iloc[0]

        pilots = find_best_pilots(mission)

        drones = find_available_drones(
            mission["location"],
            mission["weather_forecast"]
        )

        logging.info(f"Resource matching completed for {project_id}")

        return {
            "pilots": pilots,
            "drones": drones
        }

    except Exception as e:

        logging.error(f"Resource matching error: {e}")

        return {
            "pilots": [],
            "drones": []
        }
