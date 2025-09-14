import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import speech_recognition as sr
import pyaudio
import numpy as np
import time

# --- Configuration ---
# Audio settings
CHUNK = 1024  # Samples per frame
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 1  # Mono audio
RATE = 44100  # Sample rate (Hz)

# Analysis parameters
ENERGY_THRESHOLD = 1000  
PITCH_THRESHOLD_LOW = 85  
PITCH_THRESHOLD_HIGH = 255 
TONE_THRESHOLD_POSITIVE = 0.5 
TONE_THRESHOLD_NEGATIVE = -0.5 

# Coaching tips
COMPLIANCE_KEYWORDS = ["confirm", "verify", "policy", "secure"]
COACHING_TIPS = {
    "energy_low": "Agent's energy is low. Suggest speaking with more enthusiasm.",
    "pitch_high": "Agent's pitch is high, which might indicate stress. Suggest taking a deep breath.",
    "pitch_low": "Agent's pitch is low. Suggest speaking more clearly.",
    "tone_negative": "Agent's tone sounds negative. Suggest a more positive and empathetic approach.",
    "compliance_reminder": "Remind agent to mention compliance keywords like 'confirm', 'verify', 'policy', or 'secure'."
}

# --- UI Class ---
class CallAssistantUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Call Assistant")

        self.is_recording = False
        self.frames = []
        self.p = None
        self.stream = None
        self.audio_thread = None

        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Buttons
        self.start_button = ttk.Button(main_frame, text="Start Recording", command=self.start_recording)
        self.start_button.grid(row=0, column=0, padx=5, pady=5)

        self.stop_button = ttk.Button(main_frame, text="Stop and Analyze", command=self.stop_and_analyze_recording, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5, pady=5)

        # Metrics display
        metrics_frame = ttk.LabelFrame(main_frame, text="Analysis Results", padding="10")
        metrics_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        self.energy_var = tk.StringVar(value="Average Energy: --")
        self.pitch_var = tk.StringVar(value="Average Pitch: -- Hz")
        self.tone_var = tk.StringVar(value="Overall Tone: --")
        self.coaching_var = tk.StringVar(value="Coaching: --")

        ttk.Label(metrics_frame, textvariable=self.energy_var).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(metrics_frame, textvariable=self.pitch_var).grid(row=1, column=0, sticky=tk.W)
        ttk.Label(metrics_frame, textvariable=self.tone_var).grid(row=2, column=0, sticky=tk.W)
        ttk.Label(metrics_frame, textvariable=self.coaching_var, foreground="blue").grid(row=3, column=0, sticky=tk.W, pady=10)

        # Transcript display
        transcript_frame = ttk.LabelFrame(main_frame, text="Transcript", padding="10")
        transcript_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))

        self.transcript_text = scrolledtext.ScrolledText(transcript_frame, height=10, width=50, wrap=tk.WORD)
        self.transcript_text.grid(row=0, column=0)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def start_recording(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.is_recording = True
        self.frames = []

        # Clear previous results
        self.energy_var.set("Average Energy: --")
        self.pitch_var.set("Average Pitch: -- Hz")
        self.tone_var.set("Overall Tone: --")
        self.coaching_var.set("Coaching: --")
        self.transcript_text.delete("1.0", tk.END)

        self.audio_thread = threading.Thread(target=self.record_audio)
        self.audio_thread.start()

    def record_audio(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  frames_per_buffer=CHUNK)
        print("Recording...")
        while self.is_recording:
            data = self.stream.read(CHUNK)
            self.frames.append(data)
        print("Recording stopped.")
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def stop_and_analyze_recording(self):
        self.is_recording = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join()

        print("Analyzing...")
        analysis_thread = threading.Thread(target=self.analyze_full_recording)
        analysis_thread.start()

    def analyze_full_recording(self):
        if not self.frames:
            return

        recorded_audio_data = b''.join(self.frames)
        audio_np = np.frombuffer(recorded_audio_data, dtype=np.int16)

        # Transcript
        r = sr.Recognizer()
        audio_data_for_recognition = sr.AudioData(recorded_audio_data, RATE, 2)
        transcript = ""
        try:
            transcript = r.recognize_google(audio_data_for_recognition)
            self.root.after(0, lambda: self.transcript_text.insert("1.0", transcript))
        except sr.UnknownValueError:
            transcript = "Could not understand audio"
            self.root.after(0, lambda: self.transcript_text.insert("1.0", transcript))
        except sr.RequestError as e:
            transcript = f"Could not request results; {e}"
            self.root.after(0, lambda: self.transcript_text.insert("1.0", transcript))

        # Analysis
        energy = np.abs(audio_np).mean()
        
        zero_crossings = np.sum(np.diff(np.sign(audio_np)))
        pitch = (zero_crossings * RATE) / (2 * len(audio_np)) if len(audio_np) > 0 else 0

        tone = 0.0
        if energy > ENERGY_THRESHOLD:
            if pitch > PITCH_THRESHOLD_HIGH:
                tone = 0.6
            elif pitch < PITCH_THRESHOLD_LOW:
                tone = -0.6

        self.root.after(0, self.update_metrics, energy, pitch, tone)
        provide_coaching(energy, pitch, tone, transcript, self)

    def update_metrics(self, energy, pitch, tone):
        self.energy_var.set(f"Average Energy: {energy:.2f}")
        self.pitch_var.set(f"Average Pitch: {pitch:.2f} Hz")
        self.tone_var.set(f"Overall Tone: {tone:.2f}")

    def update_coaching(self, tip):
        self.coaching_var.set(f"Coaching: {tip}")

    def on_closing(self):
        self.is_recording = False
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join()
        self.root.destroy()

def provide_coaching(energy, pitch, tone, transcript, ui):
    """Provides real-time coaching tips based on audio analysis."""
    tip = "--"
    if energy < ENERGY_THRESHOLD:
        tip = COACHING_TIPS['energy_low']
    elif pitch > PITCH_THRESHOLD_HIGH:
        tip = COACHING_TIPS['pitch_high']
    elif pitch < PITCH_THRESHOLD_LOW and pitch > 0:
        tip = COACHING_TIPS['pitch_low']
    elif tone < TONE_THRESHOLD_NEGATIVE:
        tip = COACHING_TIPS['tone_negative']
    elif transcript and not any(keyword in transcript.lower() for keyword in COMPLIANCE_KEYWORDS):
        tip = COACHING_TIPS['compliance_reminder']
    
    ui.root.after(0, ui.update_coaching, tip)

def main():
    """Main function to create UI and run the application."""
    root = tk.Tk()
    app = CallAssistantUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
