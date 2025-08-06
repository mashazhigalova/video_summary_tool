from typing import Dict
import time
import ssl
import certifi
import urllib3

from pytubefix.cli import on_progress
from pytubefix import YouTube

# Disable SSL warnings for development/local issues
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_ssl_context():
    """Create SSL context with proper certificate verification."""
    try:
        # Create SSL context with certifi certificates
        context = ssl.create_default_context(cafile=certifi.where())
        return context
    except Exception:
        # Fallback to default context
        return ssl.create_default_context()

def get_video_info(url: str) -> Dict[str, str]:
    """
    Returns the title and length of the video.

    Args:
        url (str): The URL of the YouTube video.

    Returns:
        Dict[str, str]: A dictionary containing the video title and length in seconds.
    """
    try:
        # Configure SSL context globally for urllib
        ssl_context = create_ssl_context()
        # Apply SSL context to the default HTTPS context
        ssl._create_default_https_context = lambda: ssl_context
        
        yt = YouTube(url, on_progress_callback=on_progress)
        yt_length = time.strftime("%H:%M:%S", time.gmtime(yt.length))
        return {"title": yt.title, "length": yt_length}
    except ssl.SSLError as e:
        raise RuntimeError(f"SSL certificate error. Please check your internet connection and try again. Details: {str(e)}")
    except Exception as e:
        if "certificate verify failed" in str(e).lower():
            raise RuntimeError("SSL certificate verification failed. This is common on macOS. Please check your internet connection and try again.")
        elif "video unavailable" in str(e).lower():
            raise RuntimeError("Video is unavailable or private. Please check the YouTube URL and try again.")
        elif "regex" in str(e).lower():
            raise RuntimeError("Invalid YouTube URL format. Please check the URL and try again.")
        else:
            raise RuntimeError(f"Error fetching video information: {str(e)}")

def find_captions(url: str) -> Dict[str, str]:
    """
    Finds all available captions for the video and returns a dictionary of language codes and names.

    Args:
        url (str): The URL of the YouTube video.

    Returns:
        Dict[str, str]: A dictionary containing the language codes and names of the available captions.
    """
    try:
        # Configure SSL context globally for urllib
        ssl_context = create_ssl_context()
        ssl._create_default_https_context = lambda: ssl_context
        
        yt = YouTube(url, on_progress_callback=on_progress, use_oauth=False, allow_oauth_cache=False)
        if not yt.captions:
            return {}
        else:
            captions = {key: yt.captions[key].name for key in yt.captions.lang_code_index}
            return captions
    except ssl.SSLError as e:
        raise RuntimeError(f"SSL certificate error while fetching captions. Please check your internet connection and try again. Details: {str(e)}")
    except Exception as e:
        if "certificate verify failed" in str(e).lower():
            raise RuntimeError("SSL certificate verification failed while fetching captions. This is common on macOS. Please check your internet connection and try again.")
        else:
            raise RuntimeError(f"Error fetching captions: {str(e)}")

def retrieve_subtitles(url: str, selected_caption_language: str) -> str:
    """
    Retrieves the subtitles for the video in the preferred language.

    Args:
        url (str): The URL of the YouTube video.
        selected_caption_language (str): Preferred language code (e.g., 'en', 'ru').

    Returns:
        str: The subtitles text.
    """
    try:
        # Configure SSL context globally for urllib
        ssl_context = create_ssl_context()
        ssl._create_default_https_context = lambda: ssl_context
        
        yt = YouTube(url, on_progress_callback=on_progress, use_oauth=False, allow_oauth_cache=False)
        raw_captions = yt.captions
        
        # Check once again if there are any captions
        if not raw_captions:
            return ""
        
        captions = {key: yt.captions[key].name for key in yt.captions.lang_code_index}
        selected_code = [key for key, value in captions.items() if value == selected_caption_language][0]
        
        captions_text = raw_captions[selected_code].generate_txt_captions()
        
        return captions_text

    except ssl.SSLError as e:
        print(f"SSL certificate error retrieving subtitles: {e}")
        raise RuntimeError(f"SSL certificate error while retrieving subtitles. Please check your internet connection and try again. Details: {str(e)}")
    except Exception as e:
        if "certificate verify failed" in str(e).lower():
            print(f"SSL certificate verification failed: {e}")
            raise RuntimeError("SSL certificate verification failed while retrieving subtitles. This is common on macOS. Please check your internet connection and try again.")
        else:
            print(f"Error retrieving subtitles: {e}")
            return ""
