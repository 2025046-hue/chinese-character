import os
import json
import requests
import traceback
import time
import random
from logging import DEBUG
from typing import Any, Dict, List
from datetime import datetime, timezone

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


def _aggregate_strokes(strokes: List[List[int]]) -> tuple[int, int, float]:
    stroke_count = 0
    total_points = 0

    for s in strokes:
        if not isinstance(s, list):
            continue

        pts = max(0, len(s) // 2)
        if pts > 0:
            stroke_count += 1
            total_points += pts

    avg_len = (total_points / stroke_count) if stroke_count > 0 else 0.0
    return stroke_count, total_points, avg_len


def _score_strokes(stroke_count: int, total_points: int, avg_len: float) -> tuple[int, list[str]]:
    feedback = []

    if stroke_count == 0 or total_points == 0:
        return 0, ["No valid strokes recorded."]

    score = min(100, int(total_points * 2))

    if stroke_count <= 1:
        score = int(score * 0.4)
        feedback.append("Only one stroke detected; character may be incomplete.")

    if avg_len < 6:
        score = int(score * 0.5)
        feedback.append("Strokes are very short; drawing may be too small or incomplete.")

    if total_points < 10:
        score = int(score * 0.6)
        feedback.append("Too few points detected for reliable recognition.")

    feedback.append(
        f"Recorded {total_points} points across {stroke_count} stroke(s)."
    )

    return max(0, min(100, score)), feedback


def _local_heuristic_eval(strokes: List[List[int]]) -> Dict[str, Any]:

    if not strokes or not isinstance(strokes, list):
        return {
            "correct_character": False,
            "correct_stroke_order_match": False,
            "correct_stroke_order": [],
            "score": 0,
            "feedback": "No valid stroke data provided.",
            "raw": {
                "evaluated_at": datetime.now(timezone.utc).isoformat(),
                "stroke_count": 0,
                "total_points": 0,
            },
        }

    stroke_count, total_points, avg_len = _aggregate_strokes(strokes)
    score, feedback = _score_strokes(stroke_count, total_points, avg_len)

    return {
        "correct_character": score >= 80,
        "correct_stroke_order_match": False,
        "correct_stroke_order": [],
        "score": score,
        "feedback": " ".join(feedback),
        "raw": {
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "stroke_count": stroke_count,
            "total_points": total_points,
        },
    }
    
    
def _build_openai_payload(character: str, strokes: List[List[int]]) -> Dict[str, Any]:
    prompt_system = (
        "You are a strict evaluator of Chinese character handwriting. "
        "You will be given a target character and a JSON array of strokes. "
        "Each stroke is a flat list of coordinates [x1,y1,x2,y2,...]. "
        "Respond ONLY with a single valid JSON object and nothing else. "
        "The JSON must have the following keys:\n"
        "- correct_character (boolean)\n"
        "- correct_stroke_order_match (boolean)\n"
        "- correct_stroke_order (array of real stroke components that combine to form the character)\n"
        "- score (integer 0-100)\n"
        "- feedback (string, MAXIMUM 150 CHARACTERS)\n\n"
        "Rules:\n"
        "- correct_stroke_order MUST be the actual written parts of the character, not symbols.\n"
        "- When combined in order, the parts MUST form the full character.\n"
        "- Be conservative: give a low score if uncertain.\n"
        "- Be strict about stroke order and shape accuracy.\n"
        "- Feedback MUST be short and under 150 characters."
    )

    prompt_user = json.dumps(
        {"character": character, "strokes": strokes},
        ensure_ascii=False
    )

    return {
        "model": "gpt-4o" if DEBUG else "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user},
        ],
        "temperature": 0.0,
    }


def _post_with_retry(url: str, headers: Dict[str, str], payload: Dict[str, Any], timeout: int) -> Dict[str, Any]:
    max_retries = 4
    base_delay = 1.0

    for attempt in range(max_retries):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
            resp.raise_for_status()
            return resp.json()

        except requests.exceptions.HTTPError:
            status = resp.status_code if resp is not None else None

            if status in (429, 500, 502, 503, 504) and attempt < max_retries - 1:
                sleep_t = base_delay * (2 ** attempt) + random.uniform(0, 0.5)
                time.sleep(sleep_t)
                continue

            raise

        except (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
            if attempt < max_retries - 1:
                sleep_t = base_delay * (2 ** attempt) + random.uniform(0, 0.5)
                time.sleep(sleep_t)
                continue

            raise

    raise RuntimeError("Max retries exceeded")


def _parse_llm_response(data: Dict[str, Any]) -> Dict[str, Any]:
    content = ""

    try:
        content = data["choices"][0]["message"]["content"]
    except Exception:
        content = json.dumps(data)

    try:
        parsed = json.loads(content)
    except Exception:
        import re
        m = re.search(r"\{.*\}", content, re.S)
        if m:
            parsed = json.loads(m.group(0))
        else:
            parsed = {
                "score": 0,
                "feedback": content,
                "correct_character": False,
                "correct_stroke_order": False,
                "correct_stroke_order_match": False,
            }

    return {
        "correct_character": bool(parsed.get("correct_character", False)),
        "correct_stroke_order_match": bool(parsed.get("correct_stroke_order_match", False)),
        "correct_stroke_order": parsed.get("correct_stroke_order", []),
        "score": int(parsed.get("score", 0)),
        "feedback": str(parsed.get("feedback", "")),
        "raw": data,
    }


def evaluate_character(character: str, strokes: List[List[int]], timeout: int = 10) -> Dict[str, Any]:
    try:
        if not OPENAI_API_KEY:
            return _local_heuristic_eval(strokes)

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = _build_openai_payload(character, strokes)

        try:
            data = _post_with_retry(url, headers, payload, timeout)
        except Exception:
            return _local_heuristic_eval(strokes)

        return _parse_llm_response(data)

    except Exception as e:
        traceback.print_exc()
        return {
            "correct_character": False,
            "correct_stroke_order": False,
            "correct_stroke_order_match": False,
            "score": 0,
            "feedback": f"Evaluation failed: {e}",
            "error": True,
        }
