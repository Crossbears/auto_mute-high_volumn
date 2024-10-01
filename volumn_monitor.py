import sounddevice as sd
import numpy as np
import subprocess
import time

VOLUME_THRESHOLD = 3
current_volume_norm = 0

def mute_volume():
    subprocess.run(["osascript", "-e", "set volume with output muted"])

def unmute_volume():
    subprocess.run(["osascript", "-e", "set volume without output muted"])

def audio_callback(indata, frames, time, status):
    global current_volume_norm
    current_volume_norm = np.linalg.norm(indata) * 5
def monitor_audio():
    try:
        with sd.InputStream(callback=audio_callback):
            print("Start monitor")
            is_muted = False
            muted_time = 0
            while True:
                # print(f"current volumn: {current_volume_norm}")
                if current_volume_norm > VOLUME_THRESHOLD and not is_muted:
                    mute_volume()
                    is_muted = True
                    muted_time = time.time()
                elif is_muted and (time.time() - muted_time) > 17:
                    if current_volume_norm <= VOLUME_THRESHOLD:
                        print("unmuted.")
                        unmute_volume()
                        is_muted = False
                    else:
                        print("muting")

    except KeyboardInterrupt:
        print('Quit')

if __name__ == "__main__":
    monitor_audio()