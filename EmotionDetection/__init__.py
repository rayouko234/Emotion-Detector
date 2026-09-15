# pylint: disable=invalid-name
# The "EmotionDetection" package name is required by the course specification.
"""
Emotion Detection package.

Provides the Watson NLP based emotion detector used by the Emotion
Detector Flask application.
"""

from .emotion_detection import emotion_detector

__all__ = ["emotion_detector"]
