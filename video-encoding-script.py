import os
import subprocess
import logging

# Bitrate lookup table for different resolutions
bitrate_table = {
    "2160p": 14000,
    "1440p": 8000,
    "1080p": 4500,
    "720p": 2500,
    "480p": 1000,
    "360p": 800,
    "240p": 500,
}


def calculate_bitrate(resolution):
    return bitrate_table.get(resolution, 1000)  # Default to 1000k if resolution not found


def encode_and_package(vid_filename, res, output_dir: str = None, dash_dir: str = None, mp4_dir: str = None):
    # If no output directory is specified, create one based on input filename
    if output_dir is None:
        output_dir = os.path.splitext(os.path.basename(vid_filename))[0] + "_output"

    # If no dash directory is specified, create one within the output directory
    if dash_dir is None:
        dash_dir = f"{output_dir}/dash"

    # If no mp4 directory is specified, create one within the output directory
    if mp4_dir is None:
        mp4_dir = f"{output_dir}/mp4"

    # Ensure output directory exists
    os.makedirs(dash_dir, exist_ok=True)
    os.makedirs(mp4_dir, exist_ok=True)

    # Base name for output files
    base_name = os.path.splitext(os.path.basename(vid_filename))[0]

    # Configure logging
    logging.basicConfig(filename=os.path.join(dash_dir, 'encoding.log'), level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    # Save the current working directory
    original_cwd = os.getcwd()

    # # Change to the output directory
    # print(f"CWD: {os.getcwd()}")
    # print(f"Output dir: {output_dir}")
    # os.chdir(mp4_dir)

    # Encode video into specified resolutions in MP4
    encoded_files = []
    for resolution in res:
        height = int(resolution.replace('p', ''))
        output_file = f"{mp4_dir}/{base_name}_{resolution}.mp4"
        os.makedirs(mp4_dir, exist_ok=True)

        bitrate = calculate_bitrate(resolution)
        ffmpeg_cmd = [
            "ffmpeg",
            "-i", vid_filename,
            "-vf", f"scale=-2:{height}",
            "-c:v", "libx264",
            "-b:v", f"{bitrate}k",
            "-c:a", "aac",
            "-b:a", "128k",
            "-y", output_file
        ]
        subprocess.run(ffmpeg_cmd, check=True)
        encoded_files.append(os.path.abspath(output_file))
        print(f"Encoded video: {output_file}")
        logging.info(f"Successfully encoded {resolution}")

    # Package encoded videos into DASH
    # Change to the DASH directory
    os.chdir(dash_dir)

    dash_manifest_filename = f"{base_name}_dash.mpd"
    ffmpeg_cmd = ["ffmpeg"]
    for encoded_file in encoded_files:
        ffmpeg_cmd += ["-i", encoded_file]
    for i in range(len(encoded_files)):
        ffmpeg_cmd += ["-map", str(i)]
    ffmpeg_cmd += [
        "-c", "copy",
        "-f", "dash",
        "-use_timeline", "1",
        "-use_template", "1",
        "-seg_duration", "2",
        "-init_seg_name", "init-stream$RepresentationID$.m4s",
        "-media_seg_name", "chunk-stream$RepresentationID$-$Number%05d$.m4s",
        dash_manifest_filename
    ]
    subprocess.run(ffmpeg_cmd, check=True)
    logging.info(f"DASH packaging complete: {dash_manifest_filename}")

    os.chdir(original_cwd)


if __name__ == "__main__":
    input_video_filename = "forest-of-skiers.mp4"  # Replace with your video filename
    resolutions = ["480p", "360p", "144p"]  # Replace with desired resolutions

    # Example usages:
    # 1. Use default output directory based on input filename
    encode_and_package(input_video_filename, resolutions)

    # 2. Specify a custom output directory for DASH
    # encode_and_package(input_video_filename, resolutions, out_dir="custom_dash_output")

    # 3. Specify a separate directory for MP4 files
    # encode_and_package(input_video_filename, resolutions, mp4_dir="scaled_videos")
