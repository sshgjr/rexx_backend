"""Haiku 서비스 유닛 테스트"""
from unittest.mock import patch, MagicMock
from services.haiku_service import generate_feedback, _fallback_feedback


def test_fallback_feedback_with_issues():
    result = _fallback_feedback("squat", 72, ["무릎 각도 부족"])
    assert "스쿼트" in result
    assert "72" in result
    assert "무릎 각도 부족" in result


def test_fallback_feedback_no_issues():
    result = _fallback_feedback("bench_press", 90, [])
    assert "벤치프레스" in result
    assert "90" in result
    assert "양호" in result


@patch.dict("os.environ", {"ANTHROPIC_API_KEY": ""}, clear=False)
def test_generate_feedback_no_api_key():
    """API 키 미설정 시 fallback 반환."""
    result = generate_feedback(
        exercise_type="deadlift",
        total_score=65,
        criteria_scores=[{"name": "테스트", "score": 65, "grade": "warning"}],
        detected_issues=["허리 각도"],
    )
    assert "데드리프트" in result


@patch("services.haiku_service.Anthropic")
@patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}, clear=False)
def test_generate_feedback_api_success(mock_anthropic_cls):
    """API 호출 성공 시 응답 텍스트 반환."""
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="AI 코칭 피드백입니다.")]
    mock_client.messages.create.return_value = mock_response

    result = generate_feedback(
        exercise_type="squat",
        total_score=85,
        criteria_scores=[{"name": "무릎 각도", "score": 85.0, "grade": "good"}],
        detected_issues=[],
    )
    assert result == "AI 코칭 피드백입니다."


@patch("services.haiku_service.Anthropic")
@patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}, clear=False)
def test_generate_feedback_api_failure(mock_anthropic_cls):
    """API 호출 실패 시 fallback 반환."""
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.side_effect = Exception("API 오류")

    result = generate_feedback(
        exercise_type="squat",
        total_score=70,
        criteria_scores=[{"name": "테스트", "score": 70, "grade": "warning"}],
        detected_issues=["이슈1"],
    )
    assert "스쿼트" in result
