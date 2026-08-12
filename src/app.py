"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        "waitlist": []
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        "waitlist": []
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        "waitlist": []
    },
    "Basketball Team": {
        "description": "Competitive basketball practice and intramural games",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["james@mergington.edu"],
        "waitlist": []
    },
    "Soccer Club": {
        "description": "Soccer training and matches against other schools",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["alex@mergington.edu", "jordan@mergington.edu"],
        "waitlist": []
    },
    "Art Studio": {
        "description": "Painting, drawing, and visual arts creation",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["isabella@mergington.edu"],
        "waitlist": []
    },
    "Music Ensemble": {
        "description": "Perform in orchestral and chamber music ensembles",
        "schedule": "Mondays and Fridays, 4:00 PM - 5:00 PM",
        "max_participants": 25,
        "participants": ["lucas@mergington.edu", "grace@mergington.edu"],
        "waitlist": []
    },
    "Debate Team": {
        "description": "Develop argumentative and public speaking skills",
        "schedule": "Tuesdays and Thursdays, 4:30 PM - 5:30 PM",
        "max_participants": 10,
        "participants": ["sarah@mergington.edu"],
        "waitlist": []
    },
    "Science Club": {
        "description": "Explore scientific experiments and STEM projects",
        "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["marcus@mergington.edu", "avery@mergington.edu"],
        "waitlist": []
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


def activity_is_full(activity):
    return len(activity["participants"]) >= activity["max_participants"]


def add_to_waitlist(activity, email):
    activity["waitlist"].append(email)
    return len(activity["waitlist"])


def waitlisted_signup_response(activity_name, email, position):
    return {
        "message": f"Added {email} to the waitlist for {activity_name}",
        "status": "waitlisted",
        "position": position
    }


def add_to_activity(activity, email):
    activity["participants"].append(email)


def enrolled_signup_response(activity_name, email):
    return {
        "message": f"Signed up {email} for {activity_name}",
        "status": "enrolled"
    }


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"] or email in activity["waitlist"]:
        raise HTTPException(status_code=400, detail="Student already signed up")

    if activity_is_full(activity):
        position = add_to_waitlist(activity, email)
        return waitlisted_signup_response(activity_name, email, position)

    add_to_activity(activity, email)
    return enrolled_signup_response(activity_name, email)


@app.delete("/activities/{activity_name}/participants/{email}")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    if email in activity["waitlist"]:
        activity["waitlist"].remove(email)
        return {"message": f"Removed {email} from the waitlist for {activity_name}"}

    if email in activity["participants"]:
        activity["participants"].remove(email)
        promoted = None
        if activity["waitlist"]:
            promoted = activity["waitlist"].pop(0)
            activity["participants"].append(promoted)
        return {
            "message": f"Unregistered {email} from {activity_name}",
            "promoted": promoted
        }

    raise HTTPException(status_code=404, detail="Student is not signed up for this activity")
