import sys
import os
import pyaudio
import wave
from vosk import Model, KaldiRecognizer
from websockets.sync.client import connect

# WebSocket Server URL
ws_url = "ws://localhost:8080"
ws = connect(ws_url)
print(f"Connected to {ws_url}")

def send_message_to_server(message):
    ws.send(message)
    print(f"Sent: {message}")
    response = ws.recv()
    print(f"Received from Server: {response}")


# Load Vosk model
model_path = './vosk-model-small-en-us-0.15'  # Replace with your model path
if not os.path.exists(model_path):
    print(f"Model not found at {model_path}")
    sys.exit(1)

model = Model(model_path)

# Initialize PyAudio
mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16,
                  channels=1,
                  rate=16000,
                  input=True,
                  frames_per_buffer=8000)
stream.start_stream()

recognizer = KaldiRecognizer(model, 16000)

print("Listening...")

while True:
    data = stream.read(4000, exception_on_overflow=False)
    if recognizer.AcceptWaveform(data):
        result = recognizer.Result()
        if 'stop' in result:
            print("Detected: STOP")
            send_message_to_server("red")
            break  # Exit the loop when "stop" is detected

print("Exiting...")
stream.stop_stream()
stream.close()
mic.terminate()
ws.close()
print("Connection closed")
