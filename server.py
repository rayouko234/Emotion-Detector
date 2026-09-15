"""
Flask web application exposing the Emotion Detector.

The application provides a single-page interface on the ``/`` route that
accepts both ``GET`` and ``POST`` requests. Text submitted by the user is
analysed with the Watson NLP emotion detector and the resulting emotion
scores plus the dominant emotion are rendered on the page.
"""

from flask import Flask, render_template_string, request

from EmotionDetection.emotion_detection import emotion_detector

app = Flask(__name__)

# The five emotions with the human friendly label used on the page.
EMOTION_LABELS = (
    ("Anger", "anger"),
    ("Disgust", "disgust"),
    ("Fear", "fear"),
    ("Joy", "joy"),
    ("Sadness", "sadness"),
)

BLANK_INPUT_MESSAGE = "Please enter some text to analyze."
ANALYSIS_FAILED_MESSAGE = (
    "Sorry, we could not analyse that text. The Watson NLP service is "
    "unavailable from this environment. Please run the app inside the "
    "Skills Network lab and try again."
)

INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Emotion Detector</title>
    <style>
        :root {
            --primary: #2d6cdf;
            --primary-dark: #1e4fa0;
            --bg: #f4f6fb;
            --card: #ffffff;
            --text: #1f2937;
            --muted: #6b7280;
            --error-bg: #fef2f2;
            --error-border: #fca5a5;
            --error-text: #b91c1c;
        }
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                         Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }
        .container { max-width: 720px; margin: 0 auto; padding: 1.5rem; }
        header { text-align: center; margin: 2rem 0 1.5rem; }
        h1 { margin: 0; font-size: 2rem; color: var(--primary-dark); }
        .tagline { margin: 0.25rem 0 0; color: var(--muted); }
        .card {
            background: var(--card);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        label { display: block; font-weight: 600; margin-bottom: 0.5rem; }
        .hint { margin: 0.25rem 0 0; color: var(--muted); font-size: 0.85rem; }
        textarea {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            font: inherit;
            resize: vertical;
        }
        textarea:focus,
        textarea:focus-visible {
            outline: 2px solid var(--primary);
            outline-offset: 1px;
        }
        button {
            display: block;
            width: 100%;
            margin-top: 1rem;
            padding: 0.8rem;
            background: var(--primary);
            color: #ffffff;
            border: none;
            border-radius: 8px;
            font: inherit;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.15s ease;
        }
        button:hover { background: var(--primary-dark); }
        .message {
            margin-top: 1rem;
            padding: 0.75rem 1rem;
            background: var(--error-bg);
            border: 1px solid var(--error-border);
            color: var(--error-text);
            border-radius: 8px;
        }
        .results { margin-top: 1.5rem; }
        .results h2 { margin: 0 0 1rem; font-size: 1.25rem; }
        .score-list {
            list-style: none;
            margin: 0 0 1.25rem;
            padding: 0;
            background: var(--card);
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        .score-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.65rem 1rem;
        }
        .score-item + .score-item { border-top: 1px solid #eef0f4; }
        .score-item span:first-child { font-weight: 500; }
        .score-value {
            color: var(--primary-dark);
            font-weight: 600;
            font-variant-numeric: tabular-nums;
        }
        .dominant {
            background: #e8f0fe;
            border: 1px solid #b9d0f5;
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
        }
.dominant h3 {
            margin: 0 0 0.25rem;
            color: var(--muted);
            font-size: 0.9rem;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }
        .dominant p {
            margin: 0;
            color: var(--primary-dark);
            font-size: 1.75rem;
            font-weight: 700;
            text-transform: capitalize;
        }
        footer {
            margin: 2rem 0 1rem;
            color: var(--muted);
            font-size: 0.85rem;
            text-align: center;
        }
        @media (max-width: 600px) {
            .container { padding: 1rem; }
            h1 { font-size: 1.6rem; }
            .card { padding: 1rem; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Emotion Detector</h1>
            <p class="tagline">AI-Powered Emotion Analysis</p>
        </header>

        <main>
            <section class="card" aria-label="Emotion analysis input">
                <form method="post" action="{{ url_for('index') }}">
                    <label for="text">Enter a sentence to analyze...</label>
                    <textarea
                        id="text"
                        name="text"
                        rows="6"
                        placeholder="Enter a sentence to analyze..."
                        aria-describedby="input-hint"
                    >{{ text_to_analyse }}</textarea>
                    <p class="hint" id="input-hint">
                        Powered by IBM Watson NLP.
                    </p>
                    <button type="submit">Analyze Emotion</button>
                </form>
            </section>

            {% if message %}
            <p class="message" role="alert">{{ message }}</p>
            {% endif %}

            {% if scores %}
            <section class="results" aria-label="Analysis results">
                <h2>Analysis Results</h2>
                <ul class="score-list">
                    {% for label, value in scores %}
                    <li class="score-item">
                        <span>{{ label }}</span>
                        <span class="score-value">{{ value }}</span>
                    </li>
                    {% endfor %}
                </ul>
                <div class="dominant">
                    <h3>Dominant Emotion</h3>
                    <p>{{ dominant_emotion }}</p>
                </div>
            </section>
            {% endif %}
        </main>

        <footer>
            <p>Emotion Detector &middot; Flask &middot; IBM Watson NLP</p>
        </footer>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    """Render the main page and process text submitted by the user."""
    message = None
    scores = None
    dominant_emotion = None
    text_to_analyse = ""

    if request.method == "POST":
        text_to_analyse = request.form.get("text", "")
        if not text_to_analyse.strip():
            message = BLANK_INPUT_MESSAGE
        else:
            result = emotion_detector(text_to_analyse)
            if result is None or result.get("dominant_emotion") is None:
                message = ANALYSIS_FAILED_MESSAGE
            else:
                scores = _format_scores(result)
                dominant_emotion = result["dominant_emotion"]

    return render_template_string(
        INDEX_TEMPLATE,
        text_to_analyse=text_to_analyse,
        message=message,
        scores=scores,
        dominant_emotion=dominant_emotion,
    )


def _format_scores(result):
    """Return the emotion scores as (label, value) pairs for display."""
    return [
        (label, f"{result[emotion]:.4f}")
        for label, emotion in EMOTION_LABELS
    ]


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
