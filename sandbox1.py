# import os
# from typing import List
#
#
# def find_mp4_files(directory: str) -> List[str]:
#     """
#     Recursively searches through all directories and subdirectories for .mp4 files,
#     but includes an .mp4 file in the result list only if there is no corresponding .mpd file
#     in the "{mp4_basename}_output/dash" directory. Skips directories that end with "_output".
#
#     Args:
#         directory (str): The root directory to start the search.
#
#     Returns:
#         List[str]: A list of absolute paths of .mp4 files meeting the condition.
#     """
#     result = []
#
#     for root, dirs, files in os.walk(directory):
#         # Skip directories that end with "_output"
#         dirs[:] = [d for d in dirs if not d.endswith("_output")]
#
#         for file in files:
#             if not file.endswith(".mp4"):
#                 continue
#
#             mp4_path = os.path.abspath(os.path.join(root, file))
#             # Construct the potential path for the .mpd file
#             base_name = os.path.splitext(file)[0]
#             dash_dir = os.path.abspath(os.path.join(root, f"{base_name}_output", "dash"))
#
#             if os.path.isdir(dash_dir):
#                 mpd_file = os.path.join(dash_dir, f"{base_name}_dash.mpd")
#                 # print(mpd_file, os.path.exists(mpd_file))
#                 if os.path.exists(mpd_file):
#                     continue
#
#             result.append(mp4_path)
#
#     return result
#
#
# # Example usage:
# directory_path = "./"
# mp4_files = find_mp4_files(directory_path)
# [print(f) for f in mp4_files]
# # print(mp4_files)
#
# # /home/bulaya/PycharmProjects/video_manip/supreme-dualist-stickman-animation_output/dash/supreme-dualist-stickman-animation_dash.mpd
# # /home/bulaya/PycharmProjects/video_manip/supreme-dualist-stickman-animation_output/dash/supreme-dualist-stickman-animation.mpd False