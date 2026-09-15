"""
Emotion detection using the IBM Watson NLP Emotion Predict service.

This module exposes the :func:`emotion_detector` helper used by the Emotion
Detector Flask application. The helper sends the text to be analysed to the
Watson NLP service, reads the scores returned for the five emotions recognised
by the model and reports the dominant emotion.
"""

import logging

import requests

# Endpoint of the Watson NLP Emotion Predict service hosted by the Skills
# Network course environment (reachable from the lab network only).
EMOTION_PREDICT_URL = (
    "https://sn-watson-emotion.labs.skills.network/v1/"
    "watson.runtime.nlp.v1/NlpService/EmotionPredict"
)

# Headers required by the EmotionPredict workflow running on the service.
EMOTION_PREDICT_HEADERS = {
    "grpc-metadata-mm-model-id": "emotion_aggregated-workflow_lang_en_stock"
}

# The five emotions analysed by the model, in a stable order.
EMOTIONS = ("anger", "disgust", "fear", "joy", "sadness")

# How long to wait for a response from the Watson NLP service, in seconds.
REQUEST_TIMEOUT = 30

logger = logging.getLogger(__name__)
# A library logger must not emit output on its own: the NullHandler keeps
# failed-request warnings out of ad-hoc console usage, while still passing
# them to any logging configuration set up by the application.
logger.addHandler(logging.NullHandler())


def emotion_detector(text_to_analyse):
    """
    Detect the emotions expressed in a piece of text.

    The text is sent to the IBM Watson NLP Emotion Predict service and the
    dominant emotion is computed from the scores that the service returns.

    Args:
        text_to_analyse:
            The text to analyse. Empty, whitespace-only or non-string input is
            rejected without contacting the service.

    Returns:
        dict: A dictionary mapping each of the five emotions to its score
            together with the ``dominant_emotion``. When the input is invalid,
            the service cannot be reached or the service returns an error,
            every value in the dictionary is ``None``.
    """
    if not _is_valid_input(text_to_analyse):
        return _empty_result()

    payload = {"raw_document": {"text": text_to_analyse.strip()}}
    try:
        response = requests.post(
            EMOTION_PREDICT_URL,
            json=payload,
            headers=EMOTION_PREDICT_HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        return _format_response(response.json())
    except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
        # The request failed, the service returned an error status (for
        # example HTTP 400) or the payload could not be parsed.
        logger.warning("Watson NLP request failed: %s", exc)
        return _empty_result()


def _is_valid_input(text_to_analyse):
    """Return True when the text is a non-blank string."""
    return isinstance(text_to_analyse, str) and bool(text_to_analyse.strip())


def _empty_result():
    """Return the error representation used when analysis is impossible."""
    result = {emotion: None for emotion in EMOTIONS}
    result["dominant_emotion"] = None
    return result


def _format_response(payload):
    """
    Build the result dictionary from a successful service response.

    Args:
        payload: The JSON payload returned by the Watson NLP service.

    Returns:
        dict: The emotion scores rounded to four decimal places plus the
            dominant emotion.

    Raises:
        KeyError: When the payload does not contain any recognised emotion
            structure.
        TypeError: When the payload is not a mapping.
    """
    raw_scores = _extract_emotion_scores(payload)
    dominant_emotion = max(EMOTIONS, key=raw_scores.get)
    result = {emotion: round(raw_scores[emotion], 4) for emotion in EMOTIONS}
    result["dominant_emotion"] = dominant_emotion
    return result


def _extract_emotion_scores(payload):
    """
    Extract the emotion scores from the service response.

    The service currently returns the scores under
    ``emotionPredictions[0].emotion``; an older layout used
    ``emotion.document.emotion``, which is kept as a fallback.

    Raises:
        KeyError: When the payload contains neither recognised layout.
        TypeError: When the payload is not a mapping.
    """
    try:
        return payload["emotionPredictions"][0]["emotion"]
    except (KeyError, IndexError, TypeError):
        return payload["emotion"]["document"]["emotion"]
