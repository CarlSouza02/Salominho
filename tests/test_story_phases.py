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

    def test_first_four_genesis_phases_load(self):
        self.assertEqual(len(self.phases), 4)
        self.assertEqual(
            set(self.phases),
            {"genesis_01", "genesis_02", "genesis_03", "genesis_04"},
        )
        self.assertEqual(GENESIS_PHASE_ANCHORS[1], "genesis_01")
        self.assertEqual(GENESIS_PHASE_ANCHORS[4], "genesis_02")
        self.assertEqual(GENESIS_PHASE_ANCHORS[6], "genesis_03")
        self.assertEqual(GENESIS_PHASE_ANCHORS[11], "genesis_04")

    def test_all_quizzes_have_valid_answers(self):
        for phase in self.phases.values():
            self.assertTrue(phase["narration"])
            self.assertTrue(phase["quiz"])
            for question in phase["quiz"]:
                self.assertTrue(question["options"])
                self.assertTrue(
                    0 <= question["correct_index"] < len(question["options"])
                )

    def test_story_progress_is_separate_from_bible_reading(self):
        with tempfile.TemporaryDirectory() as tmp:
            progress = Progress(Path(tmp) / "progress.json")
            result = progress.record_story_phase("genesis_01", 3, 3)

            self.assertTrue(result["completed"])
            self.assertTrue(result["mastered"])
            self.assertFalse(progress.chapter("genesis", 1)["read"])
            self.assertEqual(progress.phase("genesis_01")["best_score"], 3)


if __name__ == "__main__":
    unittest.main()
