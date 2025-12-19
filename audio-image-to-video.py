import os
import re
import json
import argparse
from pathlib import Path
import ffmpeg


def default_int(s, default = 0):
    try:
        return int(s)
    except ValueError:
        return default
    

def load_config(config_path):
    with open(config_path, 'r') as config_file:
        return json.loads(config_file.read())


def process_video(img_path, aud_path, vid_path):
    try:
        # Input image stream
        input_image = ffmpeg.input(str(img_path), loop=1, r=0.1)
        
        # Input audio stream
        input_audio = ffmpeg.input(str(aud_path))
        
        # Combine streams and output
        output = ffmpeg.output(input_image, input_audio, str(vid_path),
                               vcodec='mpeg4', acodec='copy', r=0.1,
                               shortest=None)
        
        # Run ffmpeg command
        ffmpeg.run(output, quiet=True, overwrite_output=True)
        print(f"Successfully created video: {vid_path}")
        return True
    except ffmpeg.Error as e:
        print(f"An error occurred while processing {vid_path}: {e.stderr.decode()}")
        return False


def main(config):
    # Normalize paths based on the current operating system
    image_dir = Path(config['image_dir'])
    audio_dir = Path(config['audio_dir'])
    video_dir = Path(config['video_dir'])
    image_filename_template = config['image_filename_template']

    print(f"Processing audio files in {audio_dir}")
    print(f"Image files in {image_dir}")
    print(f"Output videos will be stored in {video_dir}")
    
    video_dir.mkdir(parents=True, exist_ok=True)

    total_processed_audios = 0
    processed_videos = 0

    # Use a list comprehension to combine glob patterns for MP3 and M4A files
    audio_files = [file for ext in ('*.mp3', '*.m4a', '*.wav') for file in audio_dir.glob(ext)]

    for audio_file in audio_files:
        print(f"Audio file: {audio_file.name}")
        
        # Extract the first positive integer from the filename
        match = re.search(r'\d+', audio_file.stem)
        if not match:
            print("Skipping. No valid number found in the filename.")
            continue
        
        audio_num = int(match.group())
        if audio_num <= 0:
            print(f"Skipping. Invalid audio number: {audio_num}")
            continue

        total_processed_audios += 1
        print(f"Audio Number: {audio_num}")

        imagenum_offset = int(config['imagenum_offset'])
        
        image_num = audio_num + imagenum_offset

        # Generate the image filename
        image_filename = image_filename_template.replace("<<<IMGNUM>>>", str(image_num))
        print(f"Image file: {image_filename}")

        img_path = image_dir / image_filename
        vid_path = video_dir / f"{audio_file.stem}.mp4"

        if process_video(img_path, audio_file, vid_path):
            processed_videos += 1

        
        print("------")

    print(f"Total number of audio files processed: {total_processed_audios}")
    print(f"Number of videos successfully created: {processed_videos}\n")

    if total_processed_audios == 0:
        print("No input audios found.")
    else:
        if total_processed_audios == processed_videos:
            print("All audio files have been successfully processed.")
        else:
            print("Some audio files have not been processed successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert audio and image to video using external config.")
    parser.add_argument('config', help='Path to the configuration JSON file')
    args = parser.parse_args()

    config = load_config(args.config)
    main(config)