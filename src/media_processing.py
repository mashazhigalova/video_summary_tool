from typing import Tuple
from typing import Dict
import time
from uuid import uuid4

from pytubefix.cli import on_progress
from pytubefix import YouTube
from pathlib import Path

import subprocess
import os
import json

def download_audio_from_yt(
    url: str, download_path: str, show_log: bool = False
) -> Tuple[str, int]:
    """
    Downloads a video from YouTube and converts it to an audio file (m4a).

    Args:
        url (str): The URL of the YouTube video.
        download_path (str): The path where the audio file will be saved (as m4a).
        show_log (bool, optional): If True, log messages will be printed during the process. Defaults to False.

    Returns:
        Tuple[str, int]: A tuple containing:
            - The title of the video.
            - Duration of the video in seconds.
    """
    if show_log:
        print(f"Starting download from {url}")

    yt = YouTube(url, on_progress_callback=on_progress)
    ys = yt.streams.get_audio_only()
    ys.download(filename=download_path)

    if ys:
        if show_log:
            print(f"Audio downloaded successfully to {download_path}")
            return yt.title, yt.length
        else:
            return "Error: download not complete.", 0

    return "Error: download not complete.", 0

def get_video_info(url: str) -> Dict[str, str]:
    """
    Returns the title and length of the video.

    Args:
        url (str): The URL of the YouTube video.

    Returns:
        Dict[str, str]: A dictionary containing the video title and length in seconds.
    """
    try:
        yt = YouTube(url, on_progress_callback=on_progress)

        yt_length = time.strftime("%H:%M:%S", time.gmtime(yt.length))

        return {"title": yt.title, "length": yt_length}

    except Exception as e:
        raise RuntimeError(f"Error fetching the video title: {e}")

def split_audio_ffmpeg(input_file: str, segment_duration: int, output_folder: str = "runtimes/output_segments") -> list:
    """
    Splits an audio file into equal-length segments using FFmpeg.

    Args:
        input_file (str): The path of the audio file to split.
        segment_duration (int): The duration of each segment in seconds.
        output_folder (str, optional): The folder where the segments will be saved. Defaults to "runtimes/output_segments".

    Returns:
        list: A list of file paths for the generated audio segments.
    """
    os.makedirs(output_folder, exist_ok=True)

    original_file_path = Path(input_file)
    original_file_name = original_file_path.stem

    output_pattern = os.path.join(output_folder, f"{original_file_name}_%03d.m4a")

    command = [
        "ffmpeg", "-i", input_file, "-f", "segment", "-segment_time", str(segment_duration),
        "-c", "copy", output_pattern
    ]

    subprocess.run(command, check=True)

    # Get the list of generated segment files
    segment_files = sorted(Path(output_folder).glob(f"{original_file_name}_*.m4a"))

    return [str(f) for f in segment_files]  # Return list of file paths

def get_video_duration_ffmpeg(video_path: str) -> float:
    """
    Get video duration in seconds from the local video file.

    Args:
        video_path (str): The path of the local video file.

    Returns:
        float: The duration of the video in seconds.
    """
    try:
        command = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", video_path]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            raise Exception(f"ffprobe error: {result.stderr.strip()}")

        output = json.loads(result.stdout)
        duration = float(output["format"]["duration"])  # Use float for accuracy

        return duration  # Convert to int if needed
    except Exception as e:
        raise RuntimeError(f"Error fetching the video duration: {e}")

def extract_audio_from_local_video_ffmpeg(uploaded_file, audio_path: str) -> Tuple[str, int]:
    """
    Extracts audio from a local video file.

    Args:
        uploaded_file: The Streamlit file object representing the uploaded video.
        audio_path (str): The path where the extracted audio will be saved.

    Returns:
        Tuple[str, int]: A tuple containing the video title and its duration in seconds.
    """
    output_folder = "runtimes/video_uploads"
    os.makedirs(output_folder, exist_ok=True)

    video_path = os.path.join(output_folder, f"temp_{uploaded_file.name}")

    try:
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Run FFmpeg command to extract audio
        command = ["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        duration = get_video_duration_ffmpeg(video_path)
        return uploaded_file.name, duration

    except Exception as e:
        raise RuntimeError(f"Error processing the video: {e}")

def extract_audio(uploaded_file=None, youtube=True, url='') -> Tuple[str, int, str]:
    """
    Extracts audio from a YouTube video or a local video file.

    Args:
        uploaded_file: The Streamlit file object for the uploaded video (if any).
        youtube (bool): Flag indicating whether to extract audio from YouTube.
        url (str): The URL of the YouTube video (if applicable).

    Returns:
        Tuple[str, int, str]: A tuple containing the video title, its duration in seconds, and the path to the audio file.
    """
    # Download audio
    runtimes_folder = "runtimes"
    os.makedirs(runtimes_folder, exist_ok=True)
    runtime_id = str(uuid4())
    audio_path = f"{runtimes_folder}/{runtime_id}.m4a"

    vidtitle, vidlength = '', 0

    if youtube:
        vidtitle, vidlength = download_audio_from_yt(url, audio_path, show_log=True)
    else:
        vidtitle, vidlength = extract_audio_from_local_video_ffmpeg(uploaded_file, audio_path=audio_path)

    return vidtitle, vidlength, audio_path
