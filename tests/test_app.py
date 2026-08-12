from src.app import activities


def test_get_activities_returns_all_activities(client):
    # Arrange
    expected_key = "Chess Club"

    # Act
    response = client.get("/activities")
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert expected_key in payload
    assert "participants" in payload[expected_key]
    assert "waitlist" in payload[expected_key]


def test_signup_for_activity_adds_participant(client):
    # Arrange
    activity_name = "Art Studio"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    payload = response.json()
    activities_response = client.get("/activities").json()

    # Assert
    assert response.status_code == 200
    assert payload["message"] == f"Signed up {email} for {activity_name}"
    assert payload["status"] == "enrolled"
    assert email in activities_response[activity_name]["participants"]


def test_signup_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    payload = response.json()

    # Assert
    assert response.status_code == 404
    assert payload["detail"] == "Activity not found"


def test_signup_returns_400_for_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    payload = response.json()

    # Assert
    assert response.status_code == 400
    assert payload["detail"] == "Student already signed up"


def test_signup_for_full_activity_adds_to_waitlist(client):
    # Arrange
    activity_name = "Art Studio"
    activity = client.get("/activities").json()[activity_name]
    activity["participants"] = [
        f"student{index}@mergington.edu"
        for index in range(activity["max_participants"])
    ]
    activity["waitlist"] = ["first.waitlisted@mergington.edu"]
    activities[activity_name] = activity
    email = "waitlisted.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert payload["status"] == "waitlisted"
    assert payload["position"] == 2
    assert activities[activity_name]["waitlist"] == [
        "first.waitlisted@mergington.edu",
        email,
    ]


def test_signup_returns_400_for_duplicate_waitlisted_student(client):
    # Arrange
    activity_name = "Chess Club"
    email = "waiting.student@mergington.edu"
    activities[activity_name]["waitlist"].append(email)

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_unregister_removes_participant(client):
    # Arrange
    activity_name = "Basketball Team"
    email = "james@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    payload = response.json()
    activities_response = client.get("/activities").json()

    # Assert
    assert response.status_code == 200
    assert payload["message"] == f"Unregistered {email} from {activity_name}"
    assert payload["promoted"] is None
    assert email not in activities_response[activity_name]["participants"]


def test_unregister_participant_promotes_first_waitlisted_student(client):
    # Arrange
    activity_name = "Basketball Team"
    email = "james@mergington.edu"
    first_waitlisted = "first.student@mergington.edu"
    second_waitlisted = "second.student@mergington.edu"
    activities[activity_name]["waitlist"] = [first_waitlisted, second_waitlisted]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["promoted"] == first_waitlisted
    assert first_waitlisted in activities[activity_name]["participants"]
    assert activities[activity_name]["waitlist"] == [second_waitlisted]


def test_unregister_waitlisted_student_does_not_promote(client):
    # Arrange
    activity_name = "Chess Club"
    email = "waiting.student@mergington.edu"
    original_participants = activities[activity_name]["participants"].copy()
    activities[activity_name]["waitlist"] = [email, "next.student@mergington.edu"]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == (
        f"Removed {email} from the waitlist for {activity_name}"
    )
    assert activities[activity_name]["participants"] == original_participants
    assert activities[activity_name]["waitlist"] == ["next.student@mergington.edu"]


def test_unregister_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "new.student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    payload = response.json()

    # Assert
    assert response.status_code == 404
    assert payload["detail"] == "Activity not found"


def test_unregister_returns_404_when_student_not_registered(client):
    # Arrange
    activity_name = "Programming Class"
    email = "missing.student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")
    payload = response.json()

    # Assert
    assert response.status_code == 404
    assert payload["detail"] == "Student is not signed up for this activity"
