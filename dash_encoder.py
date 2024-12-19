# import os
# import subprocess
# import logging
#
# # Bitrate lookup table for different resolutions
# bitrate_table = {
#     "2160p": 14000,
#     "1440p": 8000,
#     "1080p": 4500,
#     "720p": 2500,
#     "480p": 1000,
#     "360p": 800,
#     "240p": 500,
# }
#
#
# def calculate_bitrate(resolution):
#     return bitrate_table.get(resolution, 1000)  # Default to 1000k if resolution not found
#
#
# def encode_and_package(vid_filename, res, out_dir):
#     # Ensure output directory exists
#     os.makedirs(out_dir, exist_ok=True)
#
#     # Base name for output files
#     base_name = os.path.splitext(os.path.basename(vid_filename))[0]
#
#     # Configure logging
#     logging.basicConfig(filename=os.path.join(out_dir, 'encoding.log'), level=logging.INFO,
#                         format='%(asctime)s - %(levelname)s - %(message)s')
#
#     # Save the current working directory
#     original_cwd = os.getcwd()
#
#     # Change to the output directory
#     os.chdir(out_dir)
#
#     try:
#         # Encode video into specified resolutions
#         encoded_files = []
#         for resolution in res:
#             try:
#                 height = int(resolution.replace('p', ''))
#                 output_file = f"{base_name}_{resolution}.mp4"
#                 bitrate = calculate_bitrate(resolution)
#                 ffmpeg_cmd = [
#                     "ffmpeg",
#                     "-i", os.path.join(original_cwd, vid_filename),
#                     "-vf", f"scale=-2:{height}",
#                     "-c:v", "libx264",
#                     "-b:v", f"{bitrate}k",
#                     "-c:a", "aac",
#                     "-b:a", "128k",
#                     "-y", output_file
#                 ]
#                 subprocess.run(ffmpeg_cmd, check=True)
#                 encoded_files.append(output_file)
#                 logging.info(f"Successfully encoded {resolution}")
#             except subprocess.CalledProcessError as e:
#                 logging.error(f"An error occurred while encoding {resolution}: {e}")
#                 continue
#
#         # Package encoded videos into DASH
#         try:
#             dash_manifest = f"{base_name}_dash.mpd"
#             ffmpeg_cmd = ["ffmpeg"]
#             for encoded_file in encoded_files:
#                 ffmpeg_cmd += ["-i", encoded_file]
#             for i in range(len(encoded_files)):
#                 ffmpeg_cmd += ["-map", str(i)]
#             ffmpeg_cmd += [
#                 "-c", "copy",
#                 "-f", "dash",
#                 "-use_timeline", "1",
#                 "-use_template", "1",
#                 "-seg_duration", "2",
#                 "-init_seg_name", "init-stream$RepresentationID$.m4s",
#                 "-media_seg_name", "chunk-stream$RepresentationID$-$Number%05d$.m4s",
#                 dash_manifest
#             ]
#             subprocess.run(ffmpeg_cmd, check=True)
#             logging.info(f"DASH packaging complete: {dash_manifest}")
#         except subprocess.CalledProcessError as e:
#             logging.error(f"An error occurred during DASH packaging: {e}")
#
#     finally:
#         # Change back to the original working directory
#         os.chdir(original_cwd)
#
#
# if __name__ == "__main__":
#     input_video_filename = "forest-of-skiers.mp4"  # Replace with your video filename
#     resolutions = ["720p", "480p", "360p"]  # Replace with desired resolutions
#     output_dir = "output"  # Replace with desired output directory
#
#     if os.path.isfile(input_video_filename):
#         encode_and_package(input_video_filename, resolutions, output_dir)
#     else:
#         print(f"File {input_video_filename} not found.")
