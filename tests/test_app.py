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


def test_get_activity_analytics_returns_per_activity_metrics(client):
    # Act
    response = client.get("/activities/analytics")
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert payload["Chess Club"] == {
        "utilization_percentage": 16.67,
        "remaining_seats": 10,
        "total_participants": 2,
    }


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
    assert email not in activities_response[activity_name]["participants"]


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
