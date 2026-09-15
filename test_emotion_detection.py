"""
Unit tests for the Emotion Detector.

The emotion tests exercise the real Watson NLP emotion detector, so they
require access to the Skills Network Watson NLP service. The remaining
tests verify the input validation and error handling without contacting
the service.
"""

import unittest
from unittest import mock

import requests

from EmotionDetection.emotion_detection import (
    EMOTIONS,
    emotion_detector,
)

# A short sentence whose dominant emotion should be the emotion under test.
TEST_SENTENCES = {
    "anger": "I am really angry about this",
    "disgust": "I feel disgusted just hearing about this",
    "fear": "I am really scared that this will happen",
    "joy": "I am glad this happened",
    "sadness": "I am so sad about this",
}


class TestEmotionDetector(unittest.TestCase):
    """Tests for the Watson NLP emotion detector."""

    def assert_detected_emotion(self, sentence, expected_emotion):
        """Assert that the detector reports the expected dominant emotion."""
        result = emotion_detector(sentence)
        self.assertIsNotNone(result)
        if result["dominant_emotion"] is None:
            self.skipTest(
                "Watson NLP service unavailable; run tests inside the "
                "Skills Network lab"
            )
        self.assertEqual(result["dominant_emotion"], expected_emotion)

    def assert_empty_result(self, result):
        """Assert that a failed analysis returns the all-None error dict."""
        for emotion in EMOTIONS:
            self.assertIsNone(result[emotion])
        self.assertIsNone(result["dominant_emotion"])

    def test_emotion_detector_joy(self):
        """A glad sentence should produce joy as the dominant emotion."""
        self.assert_detected_emotion(TEST_SENTENCES["joy"], "joy")

    def test_emotion_detector_anger(self):
        """An angry sentence should produce anger as the dominant emotion."""
        self.assert_detected_emotion(TEST_SENTENCES["anger"], "anger")

    def test_emotion_detector_disgust(self):
        """A disgusted sentence should produce disgust as the dominant emotion."""
        self.assert_detected_emotion(TEST_SENTENCES["disgust"], "disgust")

    def test_emotion_detector_fear(self):
        """A scared sentence should produce fear as the dominant emotion."""
        self.assert_detected_emotion(TEST_SENTENCES["fear"], "fear")

    def test_emotion_detector_sadness(self):
        """A sad sentence should produce sadness as the dominant emotion."""
        self.assert_detected_emotion(TEST_SENTENCES["sadness"], "sadness")

    def test_result_contains_all_emotions(self):
        """The result should contain a score for each required emotion."""
        result = emotion_detector(TEST_SENTENCES["joy"])
        self.assertIsNotNone(result)
        for emotion in EMOTIONS:
            self.assertIn(emotion, result)
        self.assertIn("dominant_emotion", result)

    def test_dominant_emotion_has_highest_score(self):
        """The dominant emotion should match the highest returned score."""
        result = emotion_detector(TEST_SENTENCES["sadness"])
        self.assertIsNotNone(result)
        if result["dominant_emotion"] is None:
            self.skipTest(
                "Watson NLP service unavailable; run tests inside the "
                "Skills Network lab"
            )
        scores = {emotion: result[emotion] for emotion in EMOTIONS}
        self.assertEqual(result["dominant_emotion"], max(scores, key=scores.get))

    def test_blank_input_is_rejected(self):
        """Empty and whitespace-only input should not contact the service."""
        self.assert_empty_result(emotion_detector(""))
        self.assert_empty_result(emotion_detector("   "))

    def test_invalid_input_is_rejected(self):
        """Non-string input should be rejected without crashing."""
        self.assert_empty_result(emotion_detector(None))
        self.assert_empty_result(emotion_detector(123))

    def test_service_error_returns_empty_result(self):
        """A network failure should be reported, not raised."""
        with mock.patch(
            "EmotionDetection.emotion_detection.requests.post"
        ) as mocked_post:
            mocked_post.side_effect = requests.exceptions.ConnectionError(
                "service unreachable"
            )
            result = emotion_detector(TEST_SENTENCES["joy"])
        self.assert_empty_result(result)
        mocked_post.assert_called_once()

    def test_http_400_returns_empty_result(self):
        """An HTTP 400 response should be handled gracefully."""
        response = requests.Response()
        response.status_code = 400
        response._content = b'{"error": "Bad request"}'  # pylint: disable=protected-access
        with mock.patch(
            "EmotionDetection.emotion_detection.requests.post",
            return_value=response,
        ):
            result = emotion_detector(TEST_SENTENCES["joy"])
        self.assert_empty_result(result)

    def test_unexpected_payload_returns_empty_result(self):
        """A response without emotion scores should be handled gracefully."""
        response = requests.Response()
        response.status_code = 200
        response._content = b'{"usage": {}}'  # pylint: disable=protected-access
        with mock.patch(
            "EmotionDetection.emotion_detection.requests.post",
            return_value=response,
        ):
            result = emotion_detector(TEST_SENTENCES["joy"])
        self.assert_empty_result(result)


if __name__ == "__main__":
    unittest.main()
