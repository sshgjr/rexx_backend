import os
import traceback
from anthropic import Anthropic


def generate_feedback(
    exercise_type: str,
    total_score: int,
    criteria_scores: list,
    detected_issues: list,
) -> str:
    """Claude Haiku를 사용하여 운동 자세 피드백 생성"""

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("[HaikuService] ANTHROPIC_API_KEY가 설정되지 않음, 기본 피드백 반환")
        return _fallback_feedback(exercise_type, total_score, detected_issues)

    exercise_names = {
        "squat": "스쿼트",
        "bench_press": "벤치프레스",
        "deadlift": "데드리프트",
    }
    exercise_name = exercise_names.get(exercise_type, exercise_type)

    criteria_text = "\n".join(
        f"- {c['name']}: {c['score']:.0f}점 ({c['grade']})"
        for c in criteria_scores
    )

    issues_text = "\n".join(f"- {issue}" for issue in detected_issues) if detected_issues else "없음"

    user_message = f"""운동: {exercise_name}
총점: {total_score}/100

기준별 점수:
{criteria_text}

감지된 이슈:
{issues_text}"""

    try:
        client = Anthropic(api_key=api_key, timeout=25.0)

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            system="당신은 전문 스트렝스 코치입니다. 사용자의 운동 자세 평가 결과를 바탕으로 2-3문장의 한국어 피드백을 제공하세요.\n\n규칙:\n- 잘한 점 1개를 먼저 언급\n- 개선점 1-2개를 구체적 교정 방법과 함께 제시\n- 격려하는 톤 유지\n- 전문 용어는 쉽게 풀어서 설명",
            messages=[
                {"role": "user", "content": user_message}
            ],
        )

        return response.content[0].text

    except Exception as e:
        print(f"[HaikuService] Claude API 호출 실패: {e}")
        traceback.print_exc()
        return _fallback_feedback(exercise_type, total_score, detected_issues)


def _fallback_feedback(exercise_type: str, total_score: int, detected_issues: list) -> str:
    """API 실패 시 기본 피드백"""
    exercise_names = {
        "squat": "스쿼트",
        "bench_press": "벤치프레스",
        "deadlift": "데드리프트",
    }
    exercise_name = exercise_names.get(exercise_type, exercise_type)

    if detected_issues:
        return f"{exercise_name} 총점 {total_score}점입니다. {detected_issues[0]} 부분에서 개선이 필요합니다."
    return f"{exercise_name} 총점 {total_score}점입니다. 전반적으로 양호한 자세입니다."
