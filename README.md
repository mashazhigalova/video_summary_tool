# Video Summary Tool 🎥

A Streamlit-based application that creates summaries and transcriptions of videos from YouTube URLs or local MP4 files using Google's Gemini AI.

## Features ✨

- Process videos from YouTube URLs or local MP4 files
- Process captions for Youtube videos with the possibility to choose a language
- Generate concise summaries of video content
- Create full transcriptions
- Support for multiple languages (English, Dutch, Russian)
- Copy summaries and transcripts to clipboard
- Download transcripts as text files
- Clean and modern UI with dark theme

## Requirements 📋

- Python 3.8+
- ffmpeg
- Gemini API key

## Installation 🚀

1. Clone the repository:
   ```bash
   git clone https://github.com/mashazhigalova/video_summary_tool.git
   cd video_summary_tool
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage 💡

1. Get your Gemini API key from [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key)

2. Start the application:
   ```bash
   streamlit run app.py
   ```

3. In the application:
   - Enter and validate your Gemini API key in the sidebar
   - Either paste a YouTube URL or upload an MP4 file
   - Opt for using captions for transcription
   - Choose language settings (original or translated)
   - Click "Get Video Content" to process the video
   - View and interact with the generated summary and transcript

## Features in Detail 🔍

### Input Options
- YouTube URL input
- Local MP4 file upload
- Mutual exclusivity between inputs (one active at a time)

### Language Settings
- Original language processing
- Translation options:
  - English
  - Dutch
  - Russian

### Output Options
- Video summary
- Full transcript
- Copy to clipboard functionality
- Transcript download as text file

### UI Features
- Dark theme with custom styling
- Progress indicators
- Expandable sections
- Clear error messages
- Reset functionality

## Notes 📝

- The application processes one video at a time
- Processing time depends on video length
- Internet connection required for YouTube videos
- Temporary files are automatically cleaned up

## Troubleshooting 🔧

If you encounter issues:
1. Ensure ffmpeg is properly installed
2. Verify your Gemini API key is valid
3. Check your internet connection for YouTube videos
4. Make sure uploaded MP4 files are not corrupted
