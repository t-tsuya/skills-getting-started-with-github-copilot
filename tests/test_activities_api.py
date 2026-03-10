from src import app as app_module


def test_get_activities_returns_seed_data(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert expected_activity in payload
    assert payload[expected_activity]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_a_new_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up"}


def test_signup_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "Robotics Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_existing_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {activity_name}"
    }
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_returns_404_for_unknown_activity(client):
    # Arrange
    activity_name = "Robotics Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_returns_404_for_student_not_signed_up(client):
    # Arrange
    activity_name = "Chess Club"
    email = "not.registered@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student not signed up"}


def test_signup_rejects_invalid_email(client):
    # Arrange
    activity_name = "Chess Club"

    # Act & Assert – missing '@'
    response = client.post(f"/activities/{activity_name}/signup", params={"email": "not-an-email"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid email address"}


def test_unregister_rejects_invalid_email(client):
    # Arrange
    activity_name = "Chess Club"

    # Act & Assert
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": "bad-email"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid email address"}


def test_signup_normalizes_email(client):
    # Arrange
    activity_name = "Chess Club"
    email = "  New.Student@Mergington.EDU  "

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert – stored as lowercase and trimmed
    assert response.status_code == 200
    assert "new.student@mergington.edu" in app_module.activities[activity_name]["participants"]


def test_signup_rejects_when_activity_is_full(client):
    # Arrange – shrink Chess Club to current size (2 participants, max 2)
    app_module.activities["Chess Club"]["max_participants"] = 2

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "overflow@mergington.edu"},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Activity is full"}