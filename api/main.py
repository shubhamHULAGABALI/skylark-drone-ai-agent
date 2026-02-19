from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.sheets_service import get_pilots, get_drones, get_missions
from core.assignment_engine import match_resources
from core.conflict_detector import detect_conflicts
from core.reassignment_engine import urgent_reassign
from ai.decision_engine import decide_best_assignment

import logging


# ===============================
# CREATE FASTAPI APP
# ===============================

app = FastAPI(
    title="Skylark Drone Operations AI Agent",
    description="AI-powered drone fleet coordination system",
    version="1.0"
)


# ===============================
# ENABLE CORS (for UI integration)
# ===============================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===============================
# ROOT ENDPOINT
# ===============================

@app.get("/")
def root():

    return {
        "message": "Skylark Drone Operations AI Agent Running",
        "status": "online"
    }


# ===============================
# GET ALL PILOTS
# ===============================

@app.get("/pilots")
def get_all_pilots():

    try:

        pilots = get_pilots()

        return pilots.to_dict(orient="records")

    except Exception as e:

        logging.error(e)

        return {"error": "Failed to fetch pilots"}


# ===============================
# GET ALL DRONES
# ===============================

@app.get("/drones")
def get_all_drones():

    try:

        drones = get_drones()

        return drones.to_dict(orient="records")

    except Exception as e:

        logging.error(e)

        return {"error": "Failed to fetch drones"}


# ===============================
# GET ALL MISSIONS
# ===============================

@app.get("/missions")
def get_all_missions():

    try:

        missions = get_missions()

        return missions.to_dict(orient="records")

    except Exception as e:

        logging.error(e)

        return {"error": "Failed to fetch missions"}


# ===============================
# MATCH RESOURCES
# ===============================

@app.get("/match/{project_id}")
def match(project_id: str):

    result = match_resources(project_id)

    if isinstance(result, str):

        return {"error": result}

    return {
        "pilots": result["pilots"].to_dict(orient="records"),
        "drones": result["drones"].to_dict(orient="records")
    }


# ===============================
# AI DECISION ASSIGNMENT
# ===============================

@app.get("/assign/{project_id}")
def assign(project_id: str):

    result = decide_best_assignment(project_id)

    return result


# ===============================
# CONFLICT DETECTION
# ===============================

@app.get("/conflicts/{project_id}/{pilot_id}/{drone_id}")
def conflicts(project_id: str, pilot_id: str, drone_id: str):

    result = detect_conflicts(project_id, pilot_id, drone_id)

    return {"result": result}


# ===============================
# URGENT REASSIGNMENT
# ===============================

@app.post("/reassign/{project_id}")
def reassign(project_id: str):

    result = urgent_reassign(project_id)

    return {"result": result}
