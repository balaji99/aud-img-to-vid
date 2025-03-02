#!/bin/bash

### BEGIN: Readme 

# Overview
## This script reads mp3 files from the AUIDO_ORIG_DIR folder, reads the first positive integer in the filename (without extension), locates the corresponding image file in IMAGE_DIR_ORIG and generates an ffmpeg command to generate a video file by combining the audio and image.
## The ffmpeg commands are appended to a batch file, and after all the commands are generated, the batch file is run. The path separator is important because the batch file can be run on multiple platforms, and different platforms support different path separators.

# Change the variables in the "Configure section below"
## Set IMAGE_DIR_ORIG to the location of the input image backgrounds
## Set AUDIO_DIR_ORIG to the location of the input audio backgrounds
## Set VIDEO_DIR_ORIG to the location where the output video files will be generated
## Set IMAGE_FILENAME_TEMPLATE to the format of the image filename.
### Format: <anytext><<AUDIONUM>><anytext2>, <<AUDIONUM>> will be replaced by the actual audio file numbers in sequence
## Set PATH_SEP_BATCH to the path separator character that will be used for pathnames in the generated batch file

### END: Readme 

#################### BEGIN: Configure before running
## Add path sep 
IMAGE_DIR_ORIG="C:\Balaji\Projects\aud-img-to-vid\img"
AUDIO_DIR_ORIG="C:\Balaji\Projects\aud-img-to-vid\aud"
VIDEO_DIR_ORIG="C:\Balaji\Projects\aud-img-to-vid\vid"
IMAGE_FILENAME_TEMPLATE="<<AUDIONUM>>.png" 
PATH_SEP_BATCH="/"
#################### END: Configure before running


# Set default values. These can be overridden by the OS/platform-specific values.
img_dir="$IMAGE_DIR_ORIG"
aud_dir="$AUDIO_DIR_ORIG"
vid_dir="$VIDEO_DIR_ORIG"

img_dir_batch="$img_dir"
aud_dir_batch="$aud_dir"
vid_dir_batch="$vid_dir"

batch_file="batch-run-ffmpeg.sh"
run_batch_cmd="bash ${batch_file}"


if [[ "$OSTYPE" == "" ]]; then
	echo "Unknown platform.... Attempting to detect"
	OSTYPE=$(uname)
fi

if [[ "$OSTYPE" == "Linux" || "$OSTYPE" == "linux-gnu" ]]; then
	echo "Detected Platform: Linux"

	detailOS=$(uname -a)

	echo "$detailOS" | grep "microsoft" | grep -iq "wsl"
	if [ $? = 0 ]; then
		# Windows subsystem on Linux
		
		img_dir=$(wslpath "$IMAGE_DIR_ORIG")
		aud_dir=$(wslpath "$AUDIO_DIR_ORIG")
		vid_dir=$(wslpath "$VIDEO_DIR_ORIG")		

		img_dir_batch="$img_dir"

		aud_dir_batch="$aud_dir"
		vid_dir_batch="$vid_dir"
	fi

elif [[ "$OSTYPE" == "cygwin" ]]; then
	echo "Detected Platform: Cygwin"
	
	img_dir=$(cygpath -u "$IMAGE_DIR_ORIG")
	aud_dir=$(cygpath -u "$AUDIO_DIR_ORIG")
	vid_dir=$(cygpath -u "$VIDEO_DIR_ORIG")

	batch_file="batch-run-ffmpeg.bat"
	run_batch_cmd="cmd /c ${batch_file}"
	PATH_SEP_BATCH="\\"
	
elif [[ "$OSTYPE" == "darwin"* ]]; then
	echo "Detected Platform: Mac OS"
fi


## Prints the string values of the arguments and the values of variables that have the same names as that of the arguments.
function print_args_and_vars() {

	for arg in "$@"; do
		# printf "%s\n" "$arg"
		if [[ -v "$arg" ]]; then
			printf "%s=%s\n" "$arg" "${!arg}"
		fi
	done
}

print_args_and_vars img_dir aud_dir vid_dir


pushd .

mkdir -p "$vid_dir"

echo "### Generating ffmpeg batch"

> "$batch_file"

shopt -s nocaseglob

total_valid_audios=0

for audio_file in "$aud_dir"/*.mp3
do
	audio_filename=$(basename "$audio_file")
	video_filename=${audio_filename}.mp4
	
	echo "Audio file: $audio_filename"
	
	# Remove the .mp3 extension (last 4 characters) from the filename 
	audio_filename_no_ext=${audio_filename::-4}

	# Extract the first positive integer present in the audio filename. Strip it of leading zeroes. 
	audioNum=$(echo "$audio_filename_no_ext" | grep -Eo '[0-9]+' | head -1 | sed -e 's!^0*!!')
	echo "Audio Number: \"$audioNum\""

	# Check if the audio number is a valid natural number
	checkNat=$((audioNum+0))
	if (( checkNat <= 0 )); then
		echo "Skipping. Invalid audio number; is \"${audioNum}\"; should be > 0."		
	else
		# Generate the image filename
		image_filename=$(echo "$IMAGE_FILENAME_TEMPLATE" | sed -e "s!<<AUDIONUM>>!$audioNum!")	
		echo "Image file: $image_filename"
	
		##
		# -y => Overwrite the output file, if it already exists
		# -r => frame rate
		# -loop => force loop over input file sequence. Helps to set the background image for the entire duration of the video.
		# -i => input file 
		# -c => codec to use for output
		#	-c:v => video codec to use for output
		#	-c:a => audio codec to use for output ("copy" means use "same as input")
		# -shortest => set duration of output to duration of shortest input
		#
		# may have to add "-strict -1" if the ffmpeg does not process the input audio stating that audio samples per second is not a standard value
		##
		echo ffmpeg -y -r 0.1 -loop 1 -i "\"${img_dir_batch}${PATH_SEP_BATCH}${image_filename}\"" -i "\"${aud_dir_batch}${PATH_SEP_BATCH}${audio_filename}\"" -c:v mpeg4 -c:a copy -r 0.1 -shortest "\"${vid_dir_batch}${PATH_SEP_BATCH}${video_filename}\"" >> "$batch_file"

		total_valid_audios=$((total_valid_audios + 1))
	fi
	
	echo "------"
done

echo
echo "Total number of audio files that will be processed: ${total_valid_audios}"
echo

shopt -u nocaseglob

echo "### Running ffmpeg batch"
echo
echo

$run_batch_cmd

echo "### ffmpeg batch complete"

popd 
