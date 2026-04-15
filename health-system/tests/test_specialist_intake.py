from __future__ import annotations

import unittest

from runtime.specialist_intake import (
    build_combined_intro_questionnaire,
    render_combined_intro_questionnaire,
    parse_intake_answers,
    build_followup_questions,
)
from runtime.chat_flow import run_chat_turn


class SpecialistIntakeTests(unittest.TestCase):
    def test_questionnaire_contains_all_specialists(self):
        payload = build_combined_intro_questionnaire()
        names = [row["specialist"] for row in payload["specialists"]]
        self.assertEqual(names, ["Dietitian", "Fitness Coach", "Consistency Coach", "Progress Analyst", "Personal Chef"])
        text = render_combined_intro_questionnaire()
        self.assertIn("Dietitian", text)
        self.assertIn("Personal Chef", text)

    def test_parse_answers_creates_memory_proposals_and_routing(self):
        parsed = parse_intake_answers(
            "On office days I often overeat in the evening. Gentle prompts work best. Cooking effort must stay low.",
            "msg1",
            "2026-04-15T21:13:00+03:00",
        )
        self.assertEqual(parsed["mode"], "specialist_intake_answers")
        self.assertTrue(parsed["MEMORY_UPDATE_PROPOSALS"])
        self.assertIn("Dietitian", parsed["ROUTING_HINTS"])
        self.assertIn("Consistency Coach", parsed["ROUTING_HINTS"])
        self.assertIn("Personal Chef", parsed["ROUTING_HINTS"])

    def test_followup_questions_are_built_for_missing_domains(self):
        parsed = parse_intake_answers(
            "Office day food is hard and I overeat.",
            "msg2",
            "2026-04-15T21:13:00+03:00",
        )
        followup = build_followup_questions(parsed)
        self.assertTrue(followup["needs_followup"])
        self.assertTrue(any(row["specialist"] == "Consistency Coach" for row in followup["followups"]))

    def test_chat_flow_enters_specialist_intake_mode(self):
        result = run_chat_turn("I want to introduce myself to all specialists", "msg3", "2026-04-15T21:13:00+03:00")
        self.assertEqual(result["response_mode"], "specialist_intake")
        self.assertIn("Dietitian", result["message_text"])

    def test_chat_flow_processes_intake_answers(self):
        result = run_chat_turn(
            "Dietitian: office days are hardest. Consistency Coach: gentle prompts help. Personal Chef: I need very low effort cooking.",
            "msg4",
            "2026-04-15T21:14:00+03:00",
        )
        self.assertEqual(result["response_mode"], "specialist_intake_answers")
        self.assertTrue(result["events"]["appended"])
        self.assertIn("Dietitian", result["routing"])
        self.assertIn("Consistency Coach", result["routing"])


if __name__ == "__main__":
    unittest.main()
