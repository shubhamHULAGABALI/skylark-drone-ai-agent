import streamlit as st
import requests

API_URL = "https://skylark-drone-api.onrender.com"  # ← Updated for production

st.set_page_config(page_title="Skylark Drone AI Agent", layout="wide")

st.title("Skylark Drone Operations AI Coordinator")
st.info("""
Hello! I am your AI Drone Operations Coordinator.

I can help you with: \n
• Assign pilots and drones to missions  
• Handle urgent reassignment  
• Show pilot roster, drone fleet, and missions  
• Detect conflicts and optimize assignments  
""")



# ===============================
# SESSION STATE
# ===============================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ===============================
# DISPLAY CHAT HISTORY
# ===============================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ===============================
# COMMAND PROCESSOR
# ===============================

def process_command(command):

    command = command.strip()

    try:

        parts = command.split()

        if len(parts) == 0:
            return "Please enter a command."

        action = parts[0].lower()

        # ===============================
        # ASSIGN COMMAND
        # ===============================
        if action == "assign":

            if len(parts) < 2:
                return "Please provide a Project ID. Example: assign PRJ001"

            project_id = parts[1].upper()

            response = requests.get(
                f"{API_URL}/assign/{project_id}"
            )

            data = response.json()

            if data.get("status") == "success":

                return f"""
Assignment Successful

Pilot: {data['pilot_name']} ({data['pilot_id']})
Drone: {data['drone_model']} ({data['drone_id']})

Reason:
{data['explanation']}
"""

            elif data.get("status") == "error":

                return f"{data['message']}"

            else:
                return "Assignment failed"


        # ===============================
        # REASSIGN COMMAND
        # ===============================
        elif action == "reassign":

            if len(parts) < 2:
                return "Please provide a Project ID. Example: reassign PRJ002"

            project_id = parts[1].upper()

            response = requests.post(
                f"{API_URL}/reassign/{project_id}"
            )

            data = response.json()

            if "result" in data:
                return data["result"]

            if "message" in data:
                return data["message"]

            return "Reassignment failed"


        # ===============================
        # SHOW PILOTS
        # ===============================
        elif command.lower() == "show pilots":

            response = requests.get(f"{API_URL}/pilots")

            pilots = response.json()

            if not pilots:
                return "No pilots found."

            result = "### Pilot List\n\n"

            for p in pilots:
                result += f"- {p['pilot_id']} — {p['name']} — {p['status']}\n"

            return result


        # ===============================
        # SHOW DRONES
        # ===============================
        elif command.lower() == "show drones":

            response = requests.get(f"{API_URL}/drones")

            drones = response.json()

            if not drones:
                return "No drones found."

            result = "### Drone List\n\n"

            for d in drones:
                result += f"- {d['drone_id']} — {d['model']} — {d['status']}\n"

            return result


        # ===============================
        # SHOW MISSIONS
        # ===============================
        elif command.lower() == "show missions":

            response = requests.get(f"{API_URL}/missions")

            missions = response.json()

            if not missions:
                return "No missions found."

            result = "### Mission List\n\n"

            for m in missions:
                result += f"- {m['project_id']} — {m['location']}\n"

            return result


        # ===============================
        # UNKNOWN COMMAND
        # ===============================
        else:

            return """
I can help with these commands:

assign PRJ001  
reassign PRJ002  
show pilots  
show drones  
show missions  
"""


    except requests.exceptions.ConnectionError:

        return "❌ Cannot reach backend. Please check if the API server is running."

    except Exception as e:

        return f"Error: {str(e)}"


# ===============================
# USER INPUT
# ===============================

user_input = st.chat_input(
    "Ask the AI Drone Coordinator (e.g., assign PRJ001, reassign PRJ002, show pilots, show drones, show missions)"
)


# ===============================
# HANDLE CHAT FLOW
# ===============================

if user_input:

    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    response = process_command(user_input)

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )

    with st.chat_message("assistant"):
        st.markdown(response)
