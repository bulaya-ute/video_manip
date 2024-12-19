import subprocess
import json


def get_video_dimensions(video_path):
    try:
        # Run ffprobe command to get video information
        command = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "json",
            video_path
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Parse the JSON output
        video_info = json.loads(result.stdout)
        width = video_info['streams'][0]['width']
        height = video_info['streams'][0]['height']

        return width, height
    except Exception as e:
        print(f"Error: {e}")
        return None, None


# Example usage
video_path = "forest-of-skiers.mp4"
width, height = get_video_dimensions(video_path)
print(f"Width: {width}, Height: {height}")
