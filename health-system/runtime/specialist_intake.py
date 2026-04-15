from __future__ import annotations

from typing import Any, Dict, List

SPECIALISTS = [
    "Dietitian",
    "Fitness Coach",
    "Consistency Coach",
    "Progress Analyst",
    "Personal Chef",
]

SPECIALIST_QUESTIONS = {
    "Dietitian": [
        "What does a normal workday of eating look like for you?",
        "Where do you most often lose control with food: work, evenings, weekends, stress, or something else?",
        "What foods keep you full and what foods usually make things worse?",
        "Do you want fat loss, performance, better energy, less overeating, or some mix of those?",
    ],
    "Fitness Coach": [
        "What training are you doing now, if any?",
        "How many real training sessions per week are realistic for you?",
        "What injuries, pain, fatigue, or recovery limits matter right now?",
        "What kind of movement do you actually enjoy or tolerate?",
    ],
    "Consistency Coach": [
        "What usually breaks the plan: low energy, stress, boredom, schedule chaos, emotions, or perfectionism?",
        "What kind of prompting helps you and what kind annoys you?",
        "When you start slipping, what does the first warning sign usually look like?",
        "Do you respond better to gentle prompts, direct prompts, or reset-style prompts?",
    ],
    "Progress Analyst": [
        "How do you define a good week?",
        "Which metrics matter to you most: weight, waist, training completion, energy, food consistency, or something else?",
        "Which metrics tend to mess with your head or make you overreact?",
        "What progress would feel meaningful over the next 4-8 weeks?",
    ],
    "Personal Chef": [
        "How much time and effort are you realistically willing to spend cooking on weekdays?",
        "What easy meals do you genuinely like and repeat without getting annoyed?",
        "What foods or meal types do you avoid, dislike, or cannot use?",
        "What does your office-day food situation look like?",
    ],
}

KEYWORD_TO_SPECIALIST = {
    "eat": ["Dietitian", "Personal Chef"],
    "food": ["Dietitian", "Personal Chef"],
    "hungry": ["Dietitian"],
    "office": ["Dietitian", "Personal Chef"],
    "workout": ["Fitness Coach"],
    "train": ["Fitness Coach"],
    "injury": ["Fitness Coach"],
    "motivation": ["Consistency Coach"],
    "annoy": ["Consistency Coach"],
    "prompt": ["Consistency Coach"],
    "progress": ["Progress Analyst"],
    "metric": ["Progress Analyst"],
    "cook": ["Personal Chef"],
    "meal": ["Dietitian", "Personal Chef"],
}


def build_combined_intro_questionnaire() -> Dict[str, Any]:
    return {
        "mode": "specialist_intake",
        "specialists": [
            {
                "specialist": specialist,
                "intro": f"{specialist} wants a quick baseline so future advice fits you better.",
                "questions": SPECIALIST_QUESTIONS[specialist],
            }
            for specialist in SPECIALISTS
        ],
    }


def render_combined_intro_questionnaire() -> str:
    payload = build_combined_intro_questionnaire()
    lines: List[str] = [
        "Good. Let’s do one specialist intake round so the system understands you properly.",
        "",
        "Answer briefly. Bullet points are fine.",
    ]
    for block in payload["specialists"]:
        lines.append("")
        lines.append(f"{block['specialist']}")
        for idx, question in enumerate(block["questions"], start=1):
            lines.append(f"{idx}. {question}")
    return "\n".join(lines)


def parse_intake_answers(message: str, message_id: str, timestamp: str) -> Dict[str, Any]:
    lowered = message.lower()
    proposals: List[Dict[str, Any]] = []
    routing: List[str] = []
    extracted: Dict[str, Any] = {}

    def add(field: str, value: Any, event_type: str, target_area: str = "pattern_notes", confidence: str = "medium") -> None:
        proposals.append({
            "target_area": target_area,
            "field": field,
            "value": value,
            "confidence": confidence,
            "write_type": "pattern_note" if target_area == "pattern_notes" else "canonical_append",
            "safe_to_write": True,
            "rationale": f"user provided specialist intake answer for {field}",
            "write_scope": "canonical",
            "event_id": f"ev_{message_id}_{field}",
            "event_type": event_type,
            "timestamp": timestamp,
            "source_message_id": message_id,
        })
        extracted[field] = value

    if any(word in lowered for word in ["office", "workday", "weekday"]):
        add("office_day_food_context", True, "intake_food_context")
        routing.extend(["Dietitian", "Personal Chef"])
    if any(word in lowered for word in ["overeat", "overeating", "junk", "snack", "sweets"]):
        add("trigger_food_pattern", "overeating_risk", "intake_trigger_food_pattern")
        routing.extend(["Dietitian", "Consistency Coach"])
    if any(word in lowered for word in ["injury", "pain", "recovery", "fatigue", "tired"]):
        add("training_constraints", "recovery_or_pain_limit", "intake_training_constraint")
        routing.append("Fitness Coach")
    if any(word in lowered for word in ["annoy", "gentle", "direct", "reset", "prompt"]):
        tone = "gentle" if "gentle" in lowered else ("direct" if "direct" in lowered else ("reset" if "reset" in lowered else "unspecified"))
        add("prompt_style_preference", tone, "intake_prompt_style")
        routing.append("Consistency Coach")
    if any(word in lowered for word in ["weight", "metric", "progress", "good week"]):
        add("progress_definition_signal", True, "intake_progress_definition")
        routing.append("Progress Analyst")
    if any(word in lowered for word in ["cook", "cooking", "meal", "food", "eat"]):
        add("meal_execution_preferences", True, "intake_meal_preference")
        routing.extend(["Dietitian", "Personal Chef"])

    for keyword, specialists in KEYWORD_TO_SPECIALIST.items():
        if keyword in lowered:
            routing.extend(specialists)

    routing = list(dict.fromkeys(routing))
    needs_followup = len(extracted) < 2
    return {
        "mode": "specialist_intake_answers",
        "INTENTS": ["specialist_intake_answers"],
        "EXTRACTIONS": extracted,
        "MEMORY_UPDATE_PROPOSALS": proposals,
        "ROUTING_HINTS": routing or ["Health Director"],
        "FOLLOWUP_NEEDED": "yes" if needs_followup else "no",
    }


def build_followup_questions(parsed_intake: Dict[str, Any]) -> Dict[str, Any]:
    routing = parsed_intake.get("ROUTING_HINTS", []) or []
    extracted = parsed_intake.get("EXTRACTIONS", {}) or {}
    followups: List[Dict[str, Any]] = []

    if "Dietitian" in routing and "trigger_food_pattern" not in extracted:
        followups.append({"specialist": "Dietitian", "question": "When food goes off track, what usually starts it?"})
    if "Fitness Coach" in routing and "training_constraints" not in extracted:
        followups.append({"specialist": "Fitness Coach", "question": "Any injury, pain, or recovery limit I should treat as real constraint?"})
    if "Consistency Coach" in routing and "prompt_style_preference" not in extracted:
        followups.append({"specialist": "Consistency Coach", "question": "Do you want me more gentle, more direct, or more reset-oriented when you drift?"})
    if "Progress Analyst" in routing and "progress_definition_signal" not in extracted:
        followups.append({"specialist": "Progress Analyst", "question": "What would make you call next week a good week?"})
    if "Personal Chef" in routing and "meal_execution_preferences" not in extracted:
        followups.append({"specialist": "Personal Chef", "question": "How much weekday cooking effort is actually realistic for you?"})

    return {
        "mode": "specialist_intake_followup",
        "followups": followups,
        "needs_followup": bool(followups),
    }
