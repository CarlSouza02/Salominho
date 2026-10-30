import unittest
from unittest.mock import patch

from src.bible import get_bible_chapter, get_creation_passage, normalize_api_response
from src.levels import QUESTIONS, LEVELS


class BibleTests(unittest.TestCase):
    def test_normalize(self):
        sample = {
            "reference": "Genesis 1:1-2",
            "verses": [
                {"verse": 1, "text": " No princípio  criou ", "book_name": "Genesis"},
                {"verse": 2, "text": "a terra.", "book_name": "Genesis"},
            ],
        }
        result = normalize_api_response(sample)
        self.assertEqual(result["verses"][0]["text"], "No princípio criou")
        self.assertEqual(len(result["verses"]), 2)

    def test_questions_have_valid_answers(self):
        self.assertEqual(len(LEVELS), 10)
        for q in QUESTIONS:
            self.assertTrue(0 <= q["correct"] < len(q["choices"]))

    @patch("src.bible.requests.get")
    def test_offline_fallback_for_genesis_1(self, mock_get):
        import requests
        mock_get.side_effect = requests.ConnectionError("offline")
        result = get_creation_passage()
        self.assertTrue(result["offline"])
        self.assertTrue(result["verses"])

    @patch("src.bible.requests.get")
    def test_offline_fallback_for_other_chapter_is_non_fabricated(self, mock_get):
        import requests
        mock_get.side_effect = requests.ConnectionError("offline")
        result = get_bible_chapter("genesis", 2)
        self.assertTrue(result["offline"])
        self.assertEqual(result["verses"], [])
        self.assertEqual(result["reference"], "Gênesis 2")


if __name__ == "__main__":
    unittest.main()
