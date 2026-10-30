import tempfile
import unittest
from pathlib import Path

from src.progress import Progress
from src.story_phases import GENESIS_PHASE_ANCHORS, load_genesis_story_phases


class StoryPhaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = Path(__file__).resolve().parents[1]
        cls.phases = load_genesis_story_phases(cls.base)

    def test_genesis_1_is_the_first_complete_phase(self):
        self.assertEqual(len(self.phases), 1)
        self.assertEqual(set(self.phases), {"genesis_001"})
        phase = self.phases["genesis_001"]
        self.assertEqual(phase["chapter"], 1)
        self.assertEqual(phase["bible_reference"], "Gênesis 1")
        self.assertEqual(GENESIS_PHASE_ANCHORS, {1: "genesis_001"})
        self.assertEqual(len(phase["narration"]), 6)
        self.assertEqual(len(phase["quiz"]), 5)

    def test_quiz_answers_are_valid(self):
        phase = self.phases["genesis_001"]
        for question in phase["quiz"]:
            self.assertTrue(question["options"])
            self.assertTrue(
                0 <= question["correct_index"] < len(question["options"])
            )

    def test_phase_progress_is_separate_from_reading_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            progress = Progress(Path(tmp) / "progress.json")
            result = progress.record_story_phase("genesis_001", 5, 5)

            self.assertTrue(result["completed"])
            self.assertTrue(result["mastered"])
            self.assertFalse(progress.chapter("genesis", 1)["read"])
            self.assertEqual(progress.phase("genesis_001")["best_score"], 5)


if __name__ == "__main__":
    unittest.main()
