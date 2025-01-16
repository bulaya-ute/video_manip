import os
import subprocess
from typing import List
import requests
from tqdm import tqdm


def generate_file_urls(_url: str, segment_limit=159) -> List[str]:
    files = []
    basename = _url.split("/")[-2]
    for i in range(segment_limit + 1):
        file = f"{_url}{basename}_{i}.m4a"
        files.append(file)
    return files


def download_file(_url: str, destination: str) -> None:
    """
    Downloads a file from the given URL and saves it to the specified destination.

    Parameters:
    url (str): The URL of the file to download.
    destination (str): The path where the downloaded file should be saved.
    """
    try:
        with requests.get(_url, stream=True) as response:
            # If a directory is provided, save to that directory
            if destination.endswith("/"):
                basename = _url.split("/")[-1]
                destination = f"{destination}{basename}"

            # Check if the file already exists
            if os.path.exists(destination):
                # print(f"File already exists: {destination}. Skipping download.")
                return

            response.raise_for_status()  # Check for HTTP request errors
            with open(destination, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

        # print(f"File downloaded successfully: {destination}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download the file: {e}")


folder_urls = [
    "https://dash.akamaized.net/akamai/bbb_30fps/bbb_a64k/",

    # "https://dash.akamaized.net/akamai/bbb_30fps/bbb_30fps_320x180_200k/",
    # "https://dash.akamaized.net/akamai/bbb_30fps/bbb_30fps_640x360_800k/",
    # "https://dash.akamaized.net/akamai/bbb_30fps/bbb_30fps_768x432_1500k/",
    # "https://dash.akamaized.net/akamai/bbb_30fps/bbb_30fps_1024x576_2500k/",
    # "https://dash.akamaized.net/akamai/bbb_30fps/bbb_30fps_1280x720_4000k/",
    # "https://dash.akamaized.net/akamai/bbb_30fps/bbb_30fps_480x270_600k/",
    # "https://dash.akamaized.net/akamai/bbb_30fps/bbb_30fps_320x180_400k/",
    # "https://dash.akamaized.net/akamai/bbb_30fps/bbb_30fps_640x360_1000k/",
    # "https://dash.akamaized.net/akamai/bbb_30fps/bbb_30fps_3840x2160_12000k/",
    # "https://dash.akamaized.net/akamai/bbb_30fps/bbb_30fps_1920x1080_8000k/",
]

for base_url in folder_urls:
    file_urls = generate_file_urls(base_url)

    download_dir = "downloads/" + base_url[34:]

    # Ensure the target directory exists
    os.makedirs(download_dir, exist_ok=True)

    # Initialize the tqdm progress bar
    for file_url in tqdm(file_urls, desc=f"Downloading {base_url}", unit="files"):
        # print(file_url)
        # exit(-1)
        download_file(file_url, download_dir)

print("Download process completed.")
