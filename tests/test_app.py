from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


def test_get_activities_returns_activity_details():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert expected_activity in response_data
    assert {"description", "schedule", "max_participants", "participants"} <= set(
        response_data[expected_activity]
    )


def test_signup_adds_student_to_activity():
    # Arrange
    activity_name = "Soccer Team"
    email = "alex@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}


def test_signup_rejects_unknown_activity():
    # Arrange
    activity_name = "Robotics Club"
    email = "alex@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_rejects_duplicate_student():
    # Arrange
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]
    original_participants = activities[activity_name]["participants"].copy()

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"
    assert activities[activity_name]["participants"] == original_participants


def test_signup_requires_email():
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup")

    # Assert
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][-1] == "email"


def test_unregister_removes_student_from_activity():
    # Arrange
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]

    # Act
    response = client.request(
        "DELETE", f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}


def test_unregister_rejects_unknown_activity():
    # Arrange
    activity_name = "Robotics Club"
    email = "alex@mergington.edu"

    # Act
    response = client.request(
        "DELETE", f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_student_not_signed_up():
    # Arrange
    activity_name = "Chess Club"
    email = "alex@mergington.edu"

    # Act
    response = client.request(
        "DELETE", f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
