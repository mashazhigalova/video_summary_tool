import torch
import whisper
from concurrent.futures import ProcessPoolExecutor
from src.media_processing import split_audio_ffmpeg, extract_audio

def transcribe_chunk(file_path: str) -> str:
    """Transcribes an audio chunk.

    Args:
        file_path (str): The path to the audio file to transcribe.

    Returns:
        str: The transcribed text from the audio.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model("base", device=device)  # Load Whisper model
    result = model.transcribe(file_path)
    return result["text"]

def transcribe_audio_parallel(chunks: list) -> str:
    """Transcribes multiple audio chunks in parallel.

    Args:
        chunks (list): A list of file paths to the audio chunks.

    Returns:
        str: The combined transcribed text from all chunks.
    """
    with ProcessPoolExecutor() as executor:
        transcripts = list(executor.map(transcribe_chunk, chunks))
    return " ".join(transcripts)  # Combine results

def transcribe(youtube = True, url = '', uploaded_file = None) -> str:

    if youtube:
        _, vidlength, audio_path = extract_audio(youtube=True, url=url)
    else:
        _, vidlength, audio_path = extract_audio(youtube=False, url=uploaded_file)

    transcribed_text = ''
    if vidlength > 1800:
        output_dir = "tmp/output_segments"
        chunks = split_audio_ffmpeg(audio_path, segment_duration=900, output_folder=output_dir)
        print(f"Transcribing {len(chunks)} chunks..")
        transcribed_text = transcribe_audio_parallel(chunks)
    else:
        print(f"Transcribing {audio_path}..")
        transcribed_text = transcribe_chunk(audio_path)
    
    print(f"Transcribing of {audio_path} complete!")
    
    return transcribed_text
