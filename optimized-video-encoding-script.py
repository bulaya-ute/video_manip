import os
import subprocess
import logging
import json

# Configuration for resolutions and their corresponding parameters
RESOLUTION_CONFIG = [
    {"height": 720, "bitrate": 2500, "label": "720p"},
    {"height": 480, "bitrate": 1000, "label": "480p"},
    {"height": 360, "bitrate": 800, "label": "360p"}
]

def get_video_metadata(input_video):
    """
    Retrieve video metadata using FFprobe.
    
    Args:
        input_video (str): Path to input video file
    
    Returns:
        dict: Video metadata including width, height, and duration
    """
    try:
        cmd = [
            "ffprobe", 
            "-v", "quiet", 
            "-print_format", "json", 
            "-show_format", 
            "-show_streams", 
            input_video
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        metadata = json.loads(result.stdout)
        
        # Extract video stream information
        video_stream = next(
            (stream for stream in metadata.get('streams', []) 
             if stream.get('codec_type') == 'video'), 
            None
        )
        
        if not video_stream:
            raise ValueError("No video stream found")
        
        return {
            'width': int(video_stream.get('width', 0)),
            'height': int(video_stream.get('height', 0)),
            'duration': float(metadata.get('format', {}).get('duration', 0))
        }
    except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError) as e:
        logging.error(f"Error retrieving video metadata: {e}")
        raise

def calculate_scaled_dimensions(original_width, original_height, target_height):
    """
    Calculate scaled width maintaining aspect ratio.
    
    Args:
        original_width (int): Original video width
        original_height (int): Original video height
        target_height (int): Target height for scaling
    
    Returns:
        tuple: (scaled_width, scaled_height)
    """
    aspect_ratio = original_width / original_height
    scaled_width = int(target_height * aspect_ratio)
    
    # Ensure width is even (required by most video codecs)
    scaled_width = scaled_width if scaled_width % 2 == 0 else scaled_width + 1
    
    return (scaled_width, target_height)

def optimized_encode_and_package(input_video, output_dir=None, mp4_dir=None):
    """
    Optimized video encoding and DASH packaging in a single pass.
    
    Args:
        input_video (str): Path to input video file
        output_dir (str, optional): Directory for DASH output
        mp4_dir (str, optional): Directory for MP4 output
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Determine output directories
    base_name = os.path.splitext(os.path.basename(input_video))[0]
    output_dir = output_dir or f"{base_name}_dash_output"
    mp4_dir = mp4_dir or f"{base_name}_scaled_videos"
    
    # Create output directories
    os.makedirs(output_dir, exist_ok=True)
    if mp4_dir:
        os.makedirs(mp4_dir, exist_ok=True)
    
    # Get video metadata
    try:
        metadata = get_video_metadata(input_video)
    except Exception as e:
        logging.error(f"Could not process video metadata: {e}")
        return
    
    # Prepare FFmpeg command
    ffmpeg_cmd = [
        "ffmpeg", 
        "-i", input_video,
        "-filter_complex", ""  # Will be populated dynamically
    ]
    
    # Prepare filter complex and output mappings
    filter_parts = []
    input_mapping = "[0:v]split={}[{}]".format(
        len(RESOLUTION_CONFIG), 
        ']['.join(f'v{i}' for i in range(len(RESOLUTION_CONFIG)))
    )
    filter_parts.append(input_mapping)
    
    # Prepare DASH packaging components
    dash_inputs = []
    dash_maps = []
    mp4_outputs = []
    
    for i, config in enumerate(RESOLUTION_CONFIG):
        # Calculate scaled dimensions
        scaled_width, scaled_height = calculate_scaled_dimensions(
            metadata['width'], metadata['height'], config['height']
        )
        
        # Scale and encode part
        scale_part = f"[v{i}]scale={scaled_width}:{scaled_height},split=2[dash{i}][mp4{i}]"
        filter_parts.append(scale_part)
        
        # DASH stream preparation
        dash_inputs.append(f"[dash{i}]")
        dash_maps.append(f"-map", f"{len(dash_inputs)-1}")
        
        # MP4 output preparation if mp4_dir is specified
        if mp4_dir:
            mp4_path = os.path.join(mp4_dir, f"{base_name}_{config['label']}.mp4")
            mp4_outputs.extend([
                f"-map", f"[mp4{i}]",
                "-c:v", "libx264",
                "-b:v", f"{config['bitrate']}k",
                "-c:a", "aac",
                "-b:a", "128k",
                mp4_path
            ])
    
    # Combine filter complex
    ffmpeg_cmd.extend([
        "-filter_complex", "; ".join(filter_parts)
    ])
    
    # Add DASH packaging parameters
    dash_manifest = os.path.join(output_dir, f"{base_name}_dash.mpd")
    ffmpeg_cmd.extend([
        "-use_template", "1",
        "-use_timeline", "1",
        "-seg_duration", "4",
        "-init_seg_name", "init-stream$RepresentationID$.m4s",
        "-media_seg_name", "chunk-stream$RepresentationID$-$Number%05d$.m4s"
    ])
    
    # Combine all components
    ffmpeg_cmd.extend(dash_inputs)
    ffmpeg_cmd.extend(dash_maps)
    if mp4_dir:
        ffmpeg_cmd.extend(mp4_outputs)
    ffmpeg_cmd.extend([
        "-f", "dash",
        dash_manifest
    ])
    
    # Execute FFmpeg command
    try:
        logging.info("Starting optimized encoding and packaging...")
        subprocess.run(ffmpeg_cmd, check=True)
        logging.info("Encoding and packaging completed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error during encoding and packaging: {e}")

if __name__ == "__main__":
    input_video = "forest-of-skiers.mp4"
    
    # Example usage scenarios
    optimized_encode_and_package(input_video)  # Default output
    optimized_encode_and_package(input_video, output_dir="custom_dash_output")
    optimized_encode_and_package(input_video, mp4_dir="scaled_videos")
