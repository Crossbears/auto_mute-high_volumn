import sounddevice as sd
import numpy as np
import time
import subprocess

VOLUME_THRESHOLD = 2.5
MUTE_DURATION = 15
MONITOR_INTERVAL = 0.01
PRINT_INTERVAL = 60

devices = sd.query_devices()
blackhole_device = None
for idx, device in enumerate(devices):
    if 'BlackHole' in device['name']:
        blackhole_device = idx
        break

if blackhole_device is None:
    raise ValueError("BlackHole device not found")

PHYSICAL_OUTPUT_DEVICE = "Multi-Output Device"

is_muted = False
muted_until = 0
last_print_time = 0

def mute_physical_output():
    subprocess.run(["SwitchAudioSource", "-s", "BlackHole 2ch"])
    print("Switch to BlackHole，physical audio muted")

def unmute_physical_output():
    subprocess.run(["SwitchAudioSource", "-s", PHYSICAL_OUTPUT_DEVICE])
    print(f"Switch back to physical audio device：{PHYSICAL_OUTPUT_DEVICE}")

def audio_callback(indata, frames, callback_time, status):
    global is_muted, muted_until, last_print_time

    current_volume = np.linalg.norm(indata) * 10
    current_time = time.time()

    if current_time - last_print_time >= PRINT_INTERVAL:
        print(f"Current volumn: {current_volume}")
        last_print_time = current_time

    if is_muted and current_time < muted_until:
        return

    if is_muted and current_time >= muted_until:
        unmute_physical_output()
        is_muted = False

    if current_volume > VOLUME_THRESHOLD and not is_muted:
        print(f"Muted: {current_volume}")
        mute_physical_output()
        is_muted = True
        muted_until = current_time + MUTE_DURATION

def monitor_audio():
    try:
        with sd.InputStream(device=blackhole_device, callback=audio_callback, blocksize=1024, latency='low'):
            print("Starting monitor, press Ctrl + C to interupt...")
            while True:
                time.sleep(MONITOR_INTERVAL)
    except KeyboardInterrupt:
        print("Monitor stopped")
    finally:
        unmute_physical_output()
        print("Processing stoppted, switch back to Multi-Output Device")
if __name__ == "__main__":
    monitor_audio()