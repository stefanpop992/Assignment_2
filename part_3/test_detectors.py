"""Unit tests for the pure detection/util functions in main.py.

Run from the part_3 directory:
    python -m unittest test_detectors        # or: python test_detectors.py

These tests do not touch the network; importing main only constructs an
OpenAI client object (no request is made).
"""

import os
import unittest

# Provide safe fallbacks so the module imports even without a .env present.
os.environ.setdefault("HUB_URL", "http://example.invalid")
os.environ.setdefault("HUB_PASSWORD", "test")
os.environ.setdefault("AGENT_NAME", "stefan-code-disaster")
os.environ.setdefault("AGENT_ALIAS", "scd")
os.environ.setdefault("OPENAI_API_KEY", "test-key")

import main  # noqa: E402


class DirectedTests(unittest.TestCase):
    def test_alias_and_name_variants(self):
        for msg in ["@scd review this", "hey scd: help", "scd can you look",
                    "@ scd ping", "stefan-code-disaster please help",
                    "@stefan-code-disaster hi"]:
            self.assertTrue(main.is_directed_at_me(msg), msg)

    def test_no_false_positive_inside_words(self):
        for msg in ["please discard this", "the scoreboard is broken",
                    "i will install: deps", "describe the bug"]:
            self.assertFalse(main.is_directed_at_me(msg), msg)


class GroupBroadcastTests(unittest.TestCase):
    def test_broadcasts(self):
        for msg in ["@agents hello", "@all build app", "to all agents: ready?",
                    "all agents please report", "agents: status", "all: go"]:
            self.assertTrue(main.is_group_broadcast(msg), msg)

    def test_no_false_positive(self):
        for msg in ["i will install: numpy", "overall: good job",
                    "small task done", "callback handler"]:
            self.assertFalse(main.is_group_broadcast(msg), msg)


class ManagerElectionTests(unittest.TestCase):
    def test_real_election(self):
        for msg in ["@agents first one that answers becomes manager",
                    "to all agents: single agent acting as the head",
                    "@all we need to elect a manager"]:
            self.assertTrue(main.is_manager_election_message(msg), msg)

    def test_negation_is_not_election(self):
        self.assertFalse(main.is_manager_election_message(
            "@all build a snake game. No manager election. No single leader."))

    def test_requires_group_call(self):
        self.assertFalse(main.is_manager_election_message(
            "i think we need a manager here"))


class StatusAndWorkTests(unittest.TestCase):
    def test_group_status(self):
        self.assertTrue(main.is_group_status_request("to all agents: are you ready?"))
        self.assertTrue(main.is_group_status_request("@all report capabilities"))
        self.assertFalse(main.is_group_status_request("are you ready?"))  # not a broadcast

    def test_group_work(self):
        self.assertTrue(main.is_group_work_request("@agents build a todo app together"))
        self.assertFalse(main.is_group_work_request("build a todo app"))  # not a broadcast


class CoordinationAndSessionTests(unittest.TestCase):
    def test_coordination(self):
        self.assertTrue(main.is_coordination_message("[CLAIM] parsing"))
        self.assertTrue(main.is_coordination_message("[WORKING] here is code"))
        self.assertFalse(main.is_coordination_message("just chatting"))

    def test_session_end(self):
        self.assertTrue(main.is_session_end("[FINAL] done"))
        self.assertTrue(main.is_session_end("build complete, nice work"))
        self.assertFalse(main.is_session_end("still working on it"))


class ClaimRosterTests(unittest.TestCase):
    def test_claim_text(self):
        self.assertEqual(main.claim_text_from("[CLAIM] input handling"), "input handling")
        self.assertEqual(
            main.claim_text_from("[CLAIM]\nfood spawning logic\nmore"),
            "food spawning logic",
        )
        self.assertEqual(main.claim_text_from("no tag here"), "")

    def test_roster(self):
        msgs = [
            {"agent_name": "A", "content": "[CLAIM] parsing"},
            {"agent_name": "B", "content": "[CLAIM]\nstorage"},
            {"agent_name": "C", "content": "hello"},
        ]
        self.assertEqual(main.format_roster(main.extract_claimed_tasks(msgs)),
                         "A -> parsing; B -> storage")
        self.assertEqual(main.format_roster([]), "none yet")


class TruncateTests(unittest.TestCase):
    def test_short_unchanged(self):
        self.assertEqual(main.safe_truncate("hello", 100), "hello")

    def test_closes_open_fence(self):
        text = "before\n```python\n" + ("x" * 500)
        out = main.safe_truncate(text, 40)
        self.assertEqual(out.count("```") % 2, 0)
        self.assertTrue(out.rstrip().endswith("[truncated]"))


class GuaranteedPassTests(unittest.TestCase):
    def setUp(self):
        self._mc = main.MANAGER_CANDIDATE
        self._we = main.WORK_ENABLED

    def tearDown(self):
        main.MANAGER_CANDIDATE = self._mc
        main.WORK_ENABLED = self._we

    def test_non_candidate_election_is_pass(self):
        main.MANAGER_CANDIDATE = False
        self.assertTrue(main.is_guaranteed_pass(
            "@agents first one that answers becomes manager", work_mode=False))

    def test_candidate_election_not_guaranteed(self):
        main.MANAGER_CANDIDATE = True
        self.assertFalse(main.is_guaranteed_pass(
            "@agents first one that answers becomes manager", work_mode=False))

    def test_vague_broadcast_is_pass(self):
        main.WORK_ENABLED = False
        self.assertTrue(main.is_guaranteed_pass("@all good morning", work_mode=False))

    def test_directed_not_guaranteed(self):
        self.assertFalse(main.is_guaranteed_pass("@scd help me", work_mode=False))

    def test_status_broadcast_not_guaranteed(self):
        self.assertFalse(main.is_guaranteed_pass("@all report status", work_mode=False))

    def test_work_request_pass_when_work_disabled(self):
        main.WORK_ENABLED = False
        self.assertTrue(main.is_guaranteed_pass(
            "@agents build a snake game together", work_mode=False))

    def test_work_request_engages_when_work_enabled(self):
        main.WORK_ENABLED = True
        self.assertFalse(main.is_guaranteed_pass(
            "@agents build a snake game together", work_mode=False))


if __name__ == "__main__":
    unittest.main(verbosity=2)
