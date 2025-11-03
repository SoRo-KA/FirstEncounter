import soundfile as sf
import numpy as np
import base64

# === Load WAV ===
data, samplerate = sf.read("New_File.wav")

# === Amplify safely ===
gain = 1.5  # 2× louder (change to 1.5, 3.0, etc.)
data = np.clip(data * gain, -1.0, 1.0)

# === Save louder WAV ===
sf.write("fichier_louder.wav", data, samplerate)

# === Encode to base64 ===
with open("fichier_louder.wav", "rb") as f:
    b64data = base64.b64encode(f.read()).decode("utf-8")

# === Write to Python file ===
with open("audio_data.py", "w") as out:
    out.write(f"audio_b64 = '''{b64data}'''")

print("✅ Louder WAV encoded and written to audio_data.py")
