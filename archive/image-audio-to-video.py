import os
import re
import subprocess
import platform
from pathlib import Path

# Configuration
IMAGE_DIR_ORIG = r"C:\Balaji\temp\img"
AUDIO_DIR_ORIG = r"C:\Balaji\temp\aud"
VIDEO_DIR_ORIG = r"C:\Balaji\temp\vid"
IMAGE_FILENAME_TEMPLATE = "<<AUDIONUM>>.png"
PATH_SEP_BATCH = os.sep

# Set default values
img_dir = Path(IMAGE_DIR_ORIG)
aud_dir = Path(AUDIO_DIR_ORIG)
vid_dir = Path(VIDEO_DIR_ORIG)

img_dir_batch = img_dir
aud_dir_batch = aud_dir
vid_dir_batch = vid_dir

batch_file = "batch-run-ffmpeg.sh"
run_batch_cmd = f"bash {batch_file}"

# Detect platform
ostype = platform.system().lower()

if "windows" in ostype:
    print("Detected Platform: Windows")
    batch_file = "batch-run-ffmpeg.bat"
    run_batch_cmd = f"cmd /c {batch_file}"
    PATH_SEP_BATCH = "\\"

elif "darwin" in ostype:
    print("Detected Platform: Mac OS")
    run_batch_cmd = f"sh {batch_file}"

else:
    print("Detected Platform: Linux")

def print_args_and_vars(*args):
    for arg in args:
        print(f"{arg}={globals()[arg]}")

print_args_and_vars("img_dir", "aud_dir", "vid_dir")

vid_dir.mkdir(parents=True, exist_ok=True)

print("### Generating ffmpeg batch")

with open(batch_file, "w") as f:
    total_valid_audios = 0

    for audio_file in aud_dir.glob("*.mp3"):
        audio_filename = audio_file.name
        video_filename = f"{audio_filename}.mp4"
        
        print(f"Audio file: {audio_filename}")
        
        audio_filename_no_ext = audio_filename[:-4]
        audioNum = re.search(r'\d+', audio_filename_no_ext)
        if audioNum:
            audioNum = audioNum.group().lstrip('0') or '0'
            print(f"Audio Number: \"{audioNum}\"")

            checkNat = int(audioNum)
            if checkNat <= 0:
                print(f"Skipping. Invalid audio number; is \"{audioNum}\"; should be > 0.")
            else:
                image_filename = IMAGE_FILENAME_TEMPLATE.replace("<<AUDIONUM>>", audioNum)
                print(f"Image file: {image_filename}")

                ffmpeg_command = f'ffmpeg -y -r 0.1 -loop 1 -i "{img_dir_batch}{PATH_SEP_BATCH}{image_filename}" ' \
                                 f'-i "{aud_dir_batch}{PATH_SEP_BATCH}{audio_filename}" ' \
                                 f'-c:v mpeg4 -c:a copy -r 0.1 -shortest "{vid_dir_batch}{PATH_SEP_BATCH}{video_filename}"'
                f.write(ffmpeg_command + "\n")

                total_valid_audios += 1
        print("------")

print(f"\nTotal number of audio files that will be processed: {total_valid_audios}\n")

print("### Running ffmpeg batch\n")
subprocess.run(run_batch_cmd, shell=True)
print("### ffmpeg batch complete")
