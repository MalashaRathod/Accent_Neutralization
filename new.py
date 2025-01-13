from flask import Flask, jsonify, render_template_string
import azure.cognitiveservices.speech as speechsdk
import langid

app = Flask(__name__)

# Set up the Azure Speech API credentials
api_key = "9CTd2qVrUkZkvTC9AB44vqrsSYFponfJm8Fi6KCZCxoZuuOK96KBJQQJ99BAACYeBjFXJ3w3AAAEACOGH83l"
region = "eastus"

# Create a speech configuration instance
speech_config = speechsdk.SpeechConfig(subscription=api_key, region=region)

# Configure speech synthesis settings
speech_config.speech_synthesis_voice_name = "en-US-GuyNeural"  # Choose a voice

# Create a speech synthesizer instance
synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

# Create a speech recognizer instance
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

@app.route('/recognize_speech', methods=['GET'])
def recognize_speech():
    # Recognize speech from the microphone
    result = speech_recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        # Detect language of the recognized text
        detected_language, _ = langid.classify(result.text)
        accent = map_accent(detected_language)
        neutralized_text = neutralize_accent(result.text, accent)

        response_message = f"Recognized Speech: {result.text}\nDetected Language: {accent}\nNeutralized Speech: {neutralized_text}"
        
        # Synthesize the neutralized audio (for illustration purposes only)
        synthesizer.speak_text_async(neutralized_text).get()
    elif result.reason == speechsdk.ResultReason.NoMatch:
        response_message = "No speech could be recognized."
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        response_message = f"Speech Recognition canceled: {cancellation_details.reason}"
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            response_message += f"\nError details: {cancellation_details.error_details}"

    return jsonify({"message": response_message})

def map_accent(language_code):
    accent_mapping = {
        "en": "English (General)",
        "en-US": "American English",
        "en-GB": "British English",
        "en-IN": "Indian English",
        "en-AU": "Australian English",
        "en-CA": "Canadian English",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese"
    }
    return accent_mapping.get(language_code, "Unknown Accent")

def neutralize_accent(text, accent):
    return text

@app.route('/')
def index():
    html_content = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Speech Accent Neutralizer</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
                background-image: url('https://image.freepik.com/free-vector/long-voice-wave-colorful-modern-style-bright-voice-dark-gradient-background_172933-317.jpg');
                background-size: cover;
                background-position: center;
                color: white;
            }
            button {
                padding: 10px 20px;
                font-size: 16px;
                cursor: pointer;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            button:hover {
                background-color: #45a049;
            }
            #output {
                margin-top: 20px;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 0.6);
                padding: 15px;
                border-radius: 10px;
                display: inline-block;
            }
        </style>
    </head>
    <body>
        <h1>Speech Accent Neutralizer</h1>
        <button id="startButton" onclick="startRecognition()">🎤 Start Speaking</button>
        <button id="stopButton" onclick="stopRecognition()" style="display: none;">🛑 Stop Speaking</button>
        <div id="output"></div>

        <script>
            let recognitionActive = false;

            function startRecognition() {
                document.getElementById('startButton').style.display = 'none';
                document.getElementById('stopButton').style.display = 'inline';
                recognitionActive = true;

                fetch('/recognize_speech')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('output').innerText = data.message;
                        document.getElementById('stopButton').style.display = 'none';
                        document.getElementById('startButton').style.display = 'inline';
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        document.getElementById('output').innerText = 'An error occurred. Please try again.';
                        document.getElementById('stopButton').style.display = 'none';
                        document.getElementById('startButton').style.display = 'inline';
                    });
            }

            function stopRecognition() {
                recognitionActive = false;
                document.getElementById('stopButton').style.display = 'none';
                document.getElementById('startButton').style.display = 'inline';
                document.getElementById('output').innerText = 'Processing Please wait.....';
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_content)

if __name__ == '__main__':
    app.run(debug=True)
