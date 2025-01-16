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


def scale_video(input_file: str, output_dir: str, heights: list[int]) -> None:
    """
    Scales a video to multiple heights and saves the output videos.

    Parameters:
    input_file (str): Path to the input video file.
    output_dir (str): Directory where the scaled videos will be saved.
    heights (list[int]): List of video heights to scale the input video.
    """
    os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists
    for height in heights:
        output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(input_file))[0]}_{height}.mp4")
        command = [
            "ffmpeg", "-i", input_file, "-vf", f"scale=-1:{height}",
            "-c:v", "libx264", "-preset", "slow", "-crf", "23", "-c:a", "copy", output_file
        ]
        try:
            subprocess.run(command, check=True)
            print(f"Scaled video saved to: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error scaling video to height {height}: {e}")


def scale_video2(vid_filename, resolutions: list[str], output_dir: str = None) -> None:
    base_name = os.path.splitext(os.path.basename(vid_filename))[0]

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


if __name__ == "__main__":
    scale_video2("stickman-animation.mp4", ["240p", "480p", "720p", "1080p"],
                 "dash_test/mp4")
