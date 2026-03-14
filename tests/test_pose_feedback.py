"""자세 평가 API 테스트"""
from unittest.mock import patch


SAMPLE_FEEDBACK_REQUEST = {
    "exercise_type": "squat",
    "total_score": 78,
    "criteria_scores": [
        {"name": "무릎 각도", "description": "무릎 각도 (바텀)", "score": 85.0, "weight": 0.3, "grade": "good"},
        {"name": "힙 힌지", "description": "힙 힌지 각도", "score": 72.0, "weight": 0.2, "grade": "warning"},
        {"name": "무릎-발끝 정렬", "description": "무릎-발끝 정렬", "score": 90.0, "weight": 0.2, "grade": "good"},
        {"name": "척추 각도", "description": "척추 각도", "score": 65.0, "weight": 0.15, "grade": "warning"},
        {"name": "좌우 대칭", "description": "좌우 대칭", "score": 70.0, "weight": 0.15, "grade": "warning"},
    ],
    "detected_issues": ["힙 힌지 각도: 주의 (72점)"],
}


@patch("routers.pose_feedback.generate_feedback", return_value="테스트 피드백입니다.")
def test_feedback_authenticated(mock_fb, client, auth_header):
    res = client.post("/api/pose/feedback", json=SAMPLE_FEEDBACK_REQUEST, headers=auth_header)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["feedback"] == "테스트 피드백입니다."
    assert data["session_id"] is not None  # 로그인 사용자는 DB에 저장


@patch("routers.pose_feedback.generate_feedback", return_value="게스트 피드백")
def test_feedback_guest(mock_fb, client):
    res = client.post("/api/pose/feedback", json=SAMPLE_FEEDBACK_REQUEST)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["session_id"] is None  # 게스트는 DB 미저장


@patch("routers.pose_feedback.generate_feedback", return_value="피드백")
def test_history_authenticated(mock_fb, client, auth_header):
    # 먼저 피드백 생성
    client.post("/api/pose/feedback", json=SAMPLE_FEEDBACK_REQUEST, headers=auth_header)

    # 히스토리 조회
    res = client.get("/api/pose/history", headers=auth_header)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["history"]) == 1
    assert data["history"][0]["exercise_type"] == "squat"
    assert data["history"][0]["total_score"] == 78


def test_history_no_auth(client):
    res = client.get("/api/pose/history")
    assert res.status_code in (401, 403)
