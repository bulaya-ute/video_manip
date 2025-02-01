import os
import subprocess

bitrate_table = {
    "2160p": 14000,
    "1440p": 8000,
    "1080p": 4500,
    "720p": 2500,
    "480p": 1000,
    "360p": 800,
    "240p": 500,
}


def get_basename_directory_path(file_path: str) -> str:
    """
    Returns the path of a directory named after the basename of the file,
    in the same directory as the file, without checking or creating it.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The path to the directory named after the file's basename.
    """
    # Get the parent directory and file basename
    parent_dir = os.path.dirname(file_path)
    file_basename = os.path.splitext(os.path.basename(file_path))[0]

    # Construct and return the directory path
    return os.path.join(parent_dir, file_basename)


def filter_and_sort_qualities(qualities, video_height):
    """
    Filters and sorts the given list of qualities based on the video height.
    Ensures the filtered list is never empty by adding the lowest quality if needed.

    Args:
        qualities (list of str): List of qualities like ["480p", "360p"].
        video_height (int): The height of the input video.

    Returns:
        list of str: Filtered and sorted list of qualities.
    """
    # Convert quality strings to integers for comparison
    quality_heights = [int(q[:-1]) for q in qualities]

    # Filter out qualities higher than the video height
    filtered = [q for q, h in zip(qualities, quality_heights) if h <= video_height]

    # Ensure the list is not empty; add the lowest quality if empty
    if not filtered:
        lowest_quality = min(qualities, key=lambda q: int(q[:-1]))
        filtered.append(lowest_quality)

    # Sort the filtered list in descending order of resolution
    filtered.sort(key=lambda q: int(q[:-1]), reverse=True)

    return filtered


def calculate_bitrate(resolution):
    return bitrate_table.get(resolution, 1000)  # Default to 1000k if resolution not found


def scale_video(vid_filename, resolutions: list[str], output_dir: str = None) -> None:
    base_name = os.path.splitext(os.path.basename(vid_filename))[0]

    # If no output directory is specified, create one based on input filename
    if output_dir is None:
        output_dir = get_basename_directory_path(vid_filename)

    mp4_dir = output_dir
    for resolution in resolutions:
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
        subprocess.run(ffmpeg_cmd, capture_output=False, check=True)
        # print(f"Encoded video: {output_file}")


def split_video(input_file: str, output_dir: str) -> None:
    """
    Splits a video into segments not exceeding 3 seconds each.

    Parameters:
    input_file (str): Path to the input video file.
    output_dir (str): Directory where the segments will be saved.
    """
    os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists
    output_pattern = os.path.join(output_dir, "segment_%d.m4v")
    command = [
        "ffmpeg",
        "-i", input_file,
        "-c", "copy",
        "-map", "0",
        "-f", "segment", "-segment_time", "3", output_pattern
    ]
    try:
        subprocess.run(command, check=True)
        print(f"Video split into segments in: {output_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error splitting video: {e}")


def create_dash_manifest():
    raise NotImplementedError


if __name__ == "__main__":
    # scale_video("stickman-animation.mp4", ["240p", "480p", "720p", "1080p"],
    #             "dash_test/mp4")

    split_video("dash_test/mp4/stickman-animation_240p.mp4", "dash_test/dash/240p/")
    split_video("dash_test/mp4/stickman-animation_480p.mp4", "dash_test/dash/480p/")
    split_video("dash_test/mp4/stickman-animation_720p.mp4", "dash_test/dash/720p/")
    split_video("dash_test/mp4/stickman-animation_1080p.mp4", "dash_test/dash/1080p/")