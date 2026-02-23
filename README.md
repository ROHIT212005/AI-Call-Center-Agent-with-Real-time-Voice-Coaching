# AI Call Center Agent with Real-time Voice Coaching

A desktop Python application that records a call agent’s voice, transcribes speech, analyzes simple vocal metrics, and provides live coaching tips.

## Features

- Start/stop voice recording from a Tkinter GUI
- Automatic speech transcription using Google Speech Recognition API via `speech_recognition`
- Basic voice analytics:
  - Average energy
  - Estimated pitch (from zero-crossing rate)
  - Simple tone score
- Coaching suggestions based on:
  - Energy/pitch/tone thresholds
  - Compliance keyword detection in transcript (`confirm`, `verify`, `policy`, `secure`)

## Tech Stack

- Python 3
- Tkinter (GUI)
- PyAudio (microphone capture)
- NumPy (signal processing)
- SpeechRecognition (speech-to-text)

## Project Structure

```text
AI-Call-Center-Agent-with-Real-time-Voice-Coaching/
├── app.py
└── README.md
```

## Requirements

- Python 3.9+ (recommended)
- Working microphone/audio input device
- Internet connection (for Google speech recognition in `recognize_google`)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/ROHIT212005/AI-Call-Center-Agent-with-Real-time-Voice-Coaching
   cd AI-Call-Center-Agent-with-Real-time-Voice-Coaching
   ```

2. Install dependencies:

   ```bash
   pip install numpy SpeechRecognition pyaudio
   ```

> Note: Installing `pyaudio` on Windows may require build tools or a prebuilt wheel depending on your Python version.

## Run the App

```bash
python app.py
```

## How It Works

1. Click **Start Recording**.
2. Speak into your microphone.
3. Click **Stop and Analyze**.
4. The app:
   - Transcribes your speech
   - Calculates energy/pitch/tone
   - Displays a coaching suggestion in the UI

## Configuration

You can adjust analysis behavior in `app.py` under the **Configuration** section:

- `ENERGY_THRESHOLD`
- `PITCH_THRESHOLD_LOW`
- `PITCH_THRESHOLD_HIGH`
- `TONE_THRESHOLD_POSITIVE`
- `TONE_THRESHOLD_NEGATIVE`
- `COMPLIANCE_KEYWORDS`

## Current Limitations

- Pitch and tone logic are heuristic (not production-grade emotion detection)
- Transcription depends on external Google service availability
- Processing happens after recording stops (not continuous streaming transcription)

## Troubleshooting

- **No audio recorded:** Check microphone permissions and default input device.
- **Speech recognition fails:** Verify internet connectivity.
- **PyAudio install issues on Windows:** Use a compatible Python version/wheel and ensure required C++ build tools are available.

## Future Improvements

- Real-time streaming analysis instead of post-recording analysis
- Better pitch estimation (FFT/autocorrelation)
- Model-based sentiment and compliance checks
- Export call reports and transcripts
