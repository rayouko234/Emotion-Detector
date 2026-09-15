"""
Emotion detection using the IBM Watson NLP Emotion Predict service.

This module exposes the :func:`emotion_detector` helper used by the
Emotion Detector Flask application. The helper sends the text to be
analysed to the Watson NLP service, reads the scores returned for the
five emotions recognised by the model and reports the dominant emotion.
"""

import requests

# Endpoint of the Watson NLP Emotion Predict service hosted by the
# Skills Network course environment.
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


def emotion_detector(text_to_analyse):
    """
    Detect the emotions expressed in a piece of text.

    The text is sent to the IBM Watson NLP Emotion Predict service and
    the dominant emotion is computed from the scores that the service
    returns.

    Args:
        text_to_analyse:
            The text to analyse. Empty, whitespace-only or non-string
            input is rejected without contacting the service.

    Returns:
        dict: A dictionary mapping each of the five emotions to its
            score together with the ``dominant_emotion``, or ``None``
            when the input is invalid, the service could not be reached
            or the service returned an error.
    """
    if not _is_valid_input(text_to_analyse):
        return None

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
    except (requests.RequestException, ValueError, KeyError):
        # The request failed, the service returned an error status
        # (for example HTTP 400) or the payload could not be parsed.
        # Signal the failure instead of raising an exception.
        return None


def _is_valid_input(text_to_analyse):
    """Return True when the text is a non-blank string."""
    return isinstance(text_to_analyse, str) and bool(text_to_analyse.strip())


def _format_response(payload):
    """
    Extract the emotion scores from a successful service response.

    Args:
        payload: The JSON payload returned by the Watson NLP service.

    Returns:
        dict: The emotion scores rounded to four decimal places plus the
            dominant emotion.

    Raises:
        KeyError: When the payload does not contain the expected
            ``emotion.document.emotion`` structure.
    """
    raw_scores = payload["emotion"]["document"]["emotion"]
    dominant_emotion = max(EMOTIONS, key=raw_scores.get)
    result = {emotion: round(raw_scores[emotion], 4) for emotion in EMOTIONS}
    result["dominant_emotion"] = dominant_emotion
    return result
