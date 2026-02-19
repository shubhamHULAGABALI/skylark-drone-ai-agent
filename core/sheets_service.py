import gspread
import json
import os
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from functools import lru_cache
import logging


# ================================
# Logging setup
# ================================
logging.basicConfig(
    filename="agent.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ================================
# Google Sheets config
# ================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/148iSDjZ_EBBCHBfDucSyQFVP8lKg8yHqINGKfqCAv18/edit"

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]


# ================================
# Load credentials securely from Render environment variable
# ================================
try:

    creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])

    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        creds_dict,
        scope
    )

    client = gspread.authorize(creds)

    spreadsheet = client.open_by_url(SHEET_URL)

    logging.info("Google Sheets connection successful")

except Exception as e:

    logging.error(f"Google Sheets connection failed: {e}")

    spreadsheet = None


# ===============================
# PILOTS
# ===============================

@lru_cache(maxsize=1)
def get_pilots_cached():

    try:

        sheet = spreadsheet.worksheet("pilot_roster")

        data = sheet.get_all_records()

        logging.info("Pilot roster fetched")

        return pd.DataFrame(data)

    except Exception as e:

        logging.error(f"Pilot fetch error: {e}")

        return pd.DataFrame()


def get_pilots():

    return get_pilots_cached().copy()


# ===============================
# DRONES
# ===============================

@lru_cache(maxsize=1)
def get_drones_cached():

    try:

        sheet = spreadsheet.worksheet("drone_fleet")

        data = sheet.get_all_records()

        logging.info("Drone fleet fetched")

        return pd.DataFrame(data)

    except Exception as e:

        logging.error(f"Drone fetch error: {e}")

        return pd.DataFrame()


def get_drones():

    return get_drones_cached().copy()


# ===============================
# MISSIONS
# ===============================

@lru_cache(maxsize=1)
def get_missions_cached():

    try:

        sheet = spreadsheet.worksheet("missions")

        data = sheet.get_all_records()

        logging.info("Mission data fetched")

        return pd.DataFrame(data)

    except Exception as e:

        logging.error(f"Mission fetch error: {e}")

        return pd.DataFrame()


def get_missions():

    return get_missions_cached().copy()


# ===============================
# UPDATE PILOT STATUS
# ===============================

def update_pilot_status(pilot_id, new_status):

    try:

        sheet = spreadsheet.worksheet("pilot_roster")

        data = sheet.get_all_records()

        headers = sheet.row_values(1)

        status_col = headers.index("status") + 1

        for i, row in enumerate(data):

            if row["pilot_id"] == pilot_id:

                sheet.update_cell(i + 2, status_col, new_status)

                logging.info(f"Pilot {pilot_id} updated to {new_status}")

                # Clear cache properly
                get_pilots_cached.cache_clear()

                return f"Pilot {pilot_id} status updated to {new_status}"

        return "Pilot not found"

    except Exception as e:

        logging.error(f"Pilot update error: {e}")

        return "Error updating pilot"
