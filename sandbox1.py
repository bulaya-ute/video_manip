import os

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

# Example usage:
file_path = "/path/to/your/file.mp4"
directory_path = get_basename_directory_path(file_path)
print(f"The directory path is: {directory_path}")
