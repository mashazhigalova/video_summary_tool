import base64
import os
import shutil

def copy_to_clipboard(text):
    """
    A safe way to handle clipboard operations that works in both local and deployment environments.
    Returns a boolean indicating whether the text was copied successfully.
    """
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        return False

def get_base64(image_path):
    with open(image_path, "rb") as file:
        return base64.b64encode(file.read()).decode()

def convert_youtube_url(url):
    """
    Converts a standard YouTube video URL to an embeddable URL format.

    Standard YouTube URLs look like:
    'https://www.youtube.com/watch?v=<video_id>'
    or
    'https://youtu.be/<video_id>'

    To embed these videos, the URL should be in the format:
    'https://www.youtube.com/embed/<video_id>'

    Parameters:
        url (str): The original URL of the YouTube video.

    Returns:
        str: The embeddable URL for the YouTube video.
    """
    import re

    # Extract video ID using regex
    match = re.search(r"(?:v=|youtu\.be/|embed/)([a-zA-Z0-9_-]{11})", url)
    if not match:
        raise ValueError("Invalid YouTube URL")

    video_id = match.group(1)

    # Construct the embeddable URL
    embed_url = f"https://www.youtube.com/embed/{video_id}"

    return embed_url

def clear_folders():
    """Clears all files in the specified folders, without deleting directories.

    This function iterates through a predefined list of folders and removes all files within them.
    It does not delete any subdirectories, ensuring that the folder structure remains intact.

    Folders to be cleared:
        - runtimes
        - runtimes/output_segments
        - runtimes/video_uploads

    Returns:
        None: This function does not return any value. It performs file deletion as a side effect.
    """
    folders_to_clear = ["runtimes", "runtimes/output_segments", "runtimes/video_uploads"]  # Add any other folders as needed
    for folder in folders_to_clear:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path):  # Only remove files
                        os.unlink(file_path)  # Remove the file
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')

def style_css(background_image):
    return f"""
    <style>
        /* General styles */
        .small-text {{ font-size: 16px; color: #ffffff; margin-bottom: -10px;}}
         
        /* Header styling */
        header[data-testid="stHeader"] {{ background-color: rgba(0, 0, 0, 0.3); color: white; padding: 20px; }}
        /* Main content styling */
        .stApp {{
            background-image: url("data:image/jpg;base64,{background_image}");
            background-size: cover;
        }}
        /* Area styling */
        [data-testid="stExpander"] summary {{
            color: white !important;  /* Expander title */
        }}
        [data-testid="stSidebar"] {{
            background-color: rgba(0, 0, 0, 0.3) !important;
        }}
        [data-testid="stSidebar"] .stTextInput input::placeholder {{
            color: rgba(255, 255, 255, 0.5) !important;
        }}
        .area-title {{
            font-size: 24px;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 15px;
            margin-top: 30px;
            display: flex;
            align-items: center;
        }}
    </style>

    <p style="text-align:center; font-size:40px; color:#ffffff; font-weight: bold">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">Transcribe & Summarize Your Videos
    </p>
    <div class="small-text"><p style="text-align:center;">Get accurate transcriptions and intelligent summaries in minutes</p></div>
"""

