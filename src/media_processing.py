from typing import Tuple
from typing import Dict
import time
from uuid import uuid4

from pytubefix.cli import on_progress
from pytubefix import YouTube
from pathlib import Path
import ffmpeg
import os

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

    # Ensure the directory exists
    output_dir = os.path.dirname(download_path)
    os.makedirs(output_dir, exist_ok=True)

    # Extract just the filename from the path
    filename = os.path.basename(download_path)

    if show_log:
        print(f"Starting download from {url}..")

    yt = YouTube(url, on_progress_callback=on_progress)
    ys = yt.streams.get_audio_only()
    ys.download(output_path=output_dir, filename=filename)

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

def split_audio_ffmpeg(input_file: str, segment_duration: int, output_folder: str = "tmp/output_segments") -> list:
    """
    Splits an audio file into equal-length segments using FFmpeg.

    Args:
        input_file (str): The path of the audio file to split.
        segment_duration (int): The duration of each segment in seconds.
        output_folder (str, optional): The folder where the segments will be saved. Defaults to "tmp/output_segments".

    Returns:
        list: A list of file paths for the generated audio segments.
    """
    os.makedirs(output_folder, exist_ok=True)

    original_file_path = Path(input_file)
    original_file_name = original_file_path.stem
    output_pattern = os.path.join(output_folder, f"{original_file_name}_%03d.m4a")

    try:
        print(f"Splitting audio from {input_file} into segments of {segment_duration} seconds..")
        # Use ffmpeg-python to split the audio
        stream = ffmpeg.input(input_file)
        stream = ffmpeg.output(
            stream,
            output_pattern,
            segment_time=segment_duration,
            acodec='copy',
            f='segment'
        )
        print(f"Running ffmpeg command: {stream}")
        ffmpeg.run(stream, overwrite_output=True)

        # Get the list of generated segment files
        segment_files = sorted(Path(output_folder).glob(f"{original_file_name}_*.m4a"))
        print(f"Generated {len(segment_files)} segments")
        return [str(f) for f in segment_files]
    except ffmpeg.Error as e:
        raise RuntimeError(f"Error splitting audio: {e.stderr.decode() if e.stderr else str(e)}")

def get_video_duration_ffmpeg(video_path: str) -> float:
    """
    Get video duration in seconds from the local video file.

    Args:
        video_path (str): The path of the local video file.

    Returns:
        float: The duration of the video in seconds.
    """
    try:
        print(f"Fetching video duration from {video_path}")
        probe = ffmpeg.probe(video_path)
        duration = float(probe['format']['duration'])
        print(f"Video duration: {duration} seconds")
        return duration
    except ffmpeg.Error as e:
        raise RuntimeError(f"Error fetching the video duration: {e.stderr.decode() if e.stderr else str(e)}")

def extract_audio_from_local_video_ffmpeg(uploaded_file, audio_path: str) -> Tuple[str, int]:
    """
    Extracts audio from a local video file.

    Args:
        uploaded_file: The Streamlit file object representing the uploaded video.
        audio_path (str): The path where the extracted audio will be saved.

    Returns:
        Tuple[str, int]: A tuple containing the video title and its duration in seconds.
    """
    output_folder = "tmp/video_uploads"
    os.makedirs(output_folder, exist_ok=True)

    video_path = os.path.join(output_folder, f"temp_{uploaded_file.name}")

    try:
        print(f"Saving video to {video_path}..")
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        print(f"Running ffmpeg command to extract audio")
        # Use ffmpeg-python to extract audio
        stream = ffmpeg.input(video_path)
        stream = ffmpeg.output(
            stream,
            audio_path,
            acodec='aac',
            q=0
        )
        print(f"Running ffmpeg command: {stream}")
        ffmpeg.run(stream, overwrite_output=True)
        
        duration = get_video_duration_ffmpeg(video_path)
        print(f"Video duration: {duration} seconds")
        return uploaded_file.name, duration

    except ffmpeg.Error as e:
        raise RuntimeError(f"Error processing the video: {e.stderr.decode() if e.stderr else str(e)}")

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
    print("Starting audio extraction..")
    # Download audio
    runtimes_folder = "/tmp"
    os.makedirs(runtimes_folder, exist_ok=True)
    runtime_id = str(uuid4())
    # audio_path = f"{runtimes_folder}/{runtime_id}.m4a"
    audio_path = os.path.join(runtimes_folder, f"{runtime_id}.m4a")

    vidtitle, vidlength = '', 0

    if youtube:
        vidtitle, vidlength = download_audio_from_yt(url, audio_path, show_log=True)
    else:
        vidtitle, vidlength = extract_audio_from_local_video_ffmpeg(uploaded_file, audio_path=audio_path)

    print(f"Audio extraction complete: video title: {vidtitle}, video duration: {vidlength}, audio path: {audio_path}")
    return vidtitle, vidlength, audio_path
