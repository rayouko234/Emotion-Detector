# Emotion Detector

## Project title

**Emotion Detector**

## Description

**Emotion Detector** is a Python/Flask application that uses **IBM Watson NLP**
to identify the emotions expressed in a piece of text.

The user enters a sentence and the application sends it to the Watson NLP
**Emotion Predict** service. The service returns scores for five emotions —
anger, disgust, fear, joy and sadness — and the application reports them
together with the dominant emotion, which is the emotion with the highest
score.

## Features

* **Watson NLP emotion detection** — text is analysed by the real Watson NLP
  Emotion Predict service (no local or hard-coded results).
* **Five-emotion analysis** — returns a score for anger, disgust, fear, joy
  and sadness.
* **Dominant emotion detection** — the emotion with the highest score is
  identified and highlighted.
* **Flask web interface** — a clean, responsive single-page interface that
  works on desktop and mobile.
* **Blank-input validation** — empty or whitespace-only input is rejected with
  a friendly message before the service is called.
* **Error handling** — empty/invalid input, HTTP `400` responses, network
  failures and unexpected API payloads are handled gracefully without showing
  a Python traceback.
* **Unit testing** — `unittest` based tests that exercise the real detector.
* **Static code analysis** — the project is clean under `pylint`.

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd Emotion-Detector
   ```

2. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

3. Activate it:

   ```bash
   # Linux / macOS
   source .venv/bin/activate

   # Windows
   .venv\Scripts\activate
   ```

4. Install the requirements:

   ```bash
   pip install -r requirements.txt
   ```

> **Note:** the emotion endpoint (`sn-watson-emotion.labs.skills.network`)
> only resolves inside the Skills Network lab network. See
> [Troubleshooting](#troubleshooting) if requests fail on your own machine.

## Running the application

Start the Flask development server:

```bash
python server.py
```

Then open <http://localhost:5000> in a browser. Type a sentence, click
**Analyze Emotion**, and the emotion scores plus the dominant emotion are
displayed below the form.

## Testing

Run the unit tests with the standard `unittest` module:

```bash
python -m unittest -v
```

or, since the test file has a `__main__` block:

```bash
python test_emotion_detection.py
```

The five emotion tests call the real Watson NLP service and therefore require
access to the Skills Network endpoint. The input-validation and error-handling
tests run offline.

## Troubleshooting

### `emotion_detector` returns `None` values / "No route to host"

The Watson NLP hostname `sn-watson-emotion.labs.skills.network` resolves to
private IBM addresses (e.g. `10.241.x.x`) that are **only reachable from
inside the Skills Network lab environment**. On a normal machine the call
fails and `emotion_detector` returns the error dictionary with every value
set to `None`:

```python
{
    "anger": None, "disgust": None, "fear": None,
    "joy": None, "sadness": None, "dominant_emotion": None,
}
```

This is the expected error representation and not a crash. To get real
results, run the application and the unit tests from the Skills Network
Cloud IDE lab session — the endpoint needs no API key, but it cannot be
reached from the public internet.

## Static analysis

Run `pylint` on the project:

```bash
pylint EmotionDetection test_emotion_detection.py server.py
```

## Project structure

```text
Emotion-Detector/
├── EmotionDetection/
│   ├── __init__.py             # Package initialisation, exposes emotion_detector
│   └── emotion_detection.py    # Watson NLP emotion detector implementation
├── test_emotion_detection.py   # Unit tests for the emotion detector
├── server.py                   # Flask web application
├── requirements.txt            # Project dependencies
├── README.md                   # This file
└── .gitignore                  # Files excluded from version control
```

### Main files

* **`EmotionDetection/emotion_detection.py`** — implements
  `emotion_detector(text_to_analyse)`, which calls the Watson NLP Emotion
  Predict service, reads the five emotion scores from the actual response
  (under `emotionPredictions[0].emotion`), computes the dominant emotion and
  returns a dictionary of the form
  `{"anger": ..., "disgust": ..., "fear": ..., "joy": ..., "sadness": ...,
  "dominant_emotion": "..."}`. When the input is invalid or the service
  cannot be reached / returns an error, it returns the same dictionary with
  every value set to `None`.
* **`EmotionDetection/__init__.py`** — makes `EmotionDetection` an importable
  package and exposes `emotion_detector`.
* **`test_emotion_detection.py`** — unit tests covering all five emotions,
  the result structure, input validation and error handling.
* **`server.py`** — a Flask application with a single `GET`/`POST` route on
  `/` that renders the interface, validates the input, calls the detector and
  displays the results.
