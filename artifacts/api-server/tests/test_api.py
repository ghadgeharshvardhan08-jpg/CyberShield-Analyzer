from cybershield_api.security import hash_password, verify_password


def register(client, email="learner@example.com"):
    return client.post(
        "/api/auth/register",
        json={
            "email": email,
            "displayName": "Security Learner",
            "password": "correct-horse-battery-staple",
        },
    )


def test_registration_hashes_password_and_login_errors_are_safe(client):
    response = register(client)
    assert response.status_code == 201
    assert response.json()["authenticated"] is True
    assert response.headers["set-cookie"].startswith("cybershield_session=")
    assert "password" not in response.json()["user"]

    encoded = hash_password("correct-horse-battery-staple")
    assert encoded.startswith("$argon2id$")
    assert encoded != "correct-horse-battery-staple"
    assert verify_password("correct-horse-battery-staple", encoded)
    assert not verify_password("incorrect", encoded)

    client.post("/api/auth/logout")
    wrong_password = client.post(
        "/api/auth/login",
        json={"email": "learner@example.com", "password": "not-the-password"},
    )
    assert wrong_password.status_code == 401
    assert wrong_password.json() == {"detail": "Email or password was not recognized."}
    correct_password = client.post(
        "/api/auth/login",
        json={"email": "learner@example.com", "password": "correct-horse-battery-staple"},
    )
    assert correct_password.status_code == 200


def test_scan_requires_auth_and_private_history_isolation(client):
    assert client.post("/api/analyses", json={"url": "example.com"}).status_code == 401

    assert register(client, "first@example.com").status_code == 201
    scanned = client.post("/api/analyses", json={"url": "http://192.0.2.1/login"})
    assert scanned.status_code == 201
    analysis_id = scanned.json()["id"]
    assert client.get("/api/analyses").json()[0]["id"] == analysis_id
    report = client.get(f"/api/analyses/{analysis_id}/report")
    assert report.headers["content-type"] == "application/pdf"
    assert report.content.startswith(b"%PDF")

    client.post("/api/auth/logout")
    assert register(client, "second@example.com").status_code == 201
    assert client.get("/api/analyses").json() == []
    assert client.get(f"/api/analyses/{analysis_id}").status_code == 404
    assert client.get(f"/api/analyses/{analysis_id}/report").status_code == 404


def test_sensitive_url_values_are_not_persisted_and_validation_is_generic(client):
    assert register(client).status_code == 201
    sensitive_value = "very-private-access-token"
    response = client.post(
        "/api/analyses",
        json={
            "url": f"https://example.test/login?access_token={sensitive_value}&email=person%40example.com"
        },
    )
    assert response.status_code == 201
    assert sensitive_value not in response.text
    assert "person@example.com" not in response.text

    bad = client.post("/api/analyses", json={"url": "javascript:alert(1)"})
    assert bad.status_code == 400
    assert sensitive_value not in bad.text


def test_learning_quiz_scores_and_progress_are_persisted(client):
    assert register(client).status_code == 201
    lesson = client.get("/api/learning/modules/phishing")
    assert lesson.status_code == 200
    assert "correct" not in lesson.json()["questions"][0]

    result = client.post(
        "/api/learning/modules/phishing/quiz",
        json={
            "answers": [
                {"questionId": "p1", "selectedOption": 1},
                {"questionId": "p2", "selectedOption": 2},
                {"questionId": "p3", "selectedOption": 0},
            ]
        },
    )
    assert result.status_code == 200
    assert result.json()["score"] == 100
    assert result.json()["passed"] is True
    assert client.get("/api/learning/progress").json()["completedLessons"] == 1
    refreshed = client.get("/api/learning/modules/phishing").json()
    assert refreshed["completed"] is True
    assert refreshed["bestScore"] == 100


def test_safe_request_limits_and_account_deletion(client):
    oversized = client.post(
        "/api/auth/register",
        content=b"{}",
        headers={"Content-Length": "20000", "Content-Type": "application/json"},
    )
    assert oversized.status_code == 413

    assert register(client).status_code == 201
    assert client.post("/api/analyses", json={"url": "example.test"}).status_code == 201
    deleted = client.delete("/api/auth/account")
    assert deleted.status_code == 200
    assert deleted.json()["message"] == "Account and associated data deleted."
    assert client.get("/api/auth/session").json()["authenticated"] is False


def test_rejects_foreign_origin_for_state_changing_requests(client):
    response = register_with_origin(client, "https://attacker.example")
    assert response.status_code == 403
    assert response.json() == {"detail": "Request origin was not allowed."}


def test_allows_a_browser_same_origin_request_through_a_host_rewriting_proxy(client):
    response = client.post(
        "/api/auth/register",
        headers={
            "Origin": "https://cybershield-preview.example",
            "Sec-Fetch-Site": "same-origin",
        },
        json={
            "email": "proxy-test@example.com",
            "displayName": "Proxy Test",
            "password": "correct-horse-battery-staple",
        },
    )
    assert response.status_code == 201


def register_with_origin(client, origin):
    return client.post(
        "/api/auth/register",
        headers={"Origin": origin},
        json={
            "email": "origin-test@example.com",
            "displayName": "Origin Test",
            "password": "correct-horse-battery-staple",
        },
    )
