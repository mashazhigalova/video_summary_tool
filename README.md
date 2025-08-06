# YouTube Subtitle Summarizer 🎬

A Streamlit-based application that creates summaries and processed transcripts from YouTube video subtitles using Google's Gemini AI.

## Features ✨

- Process YouTube videos by extracting their subtitles/captions
- Generate concise summaries of video content from subtitles
- Create full processed transcriptions from subtitles
- Support for multiple subtitle languages available on YouTube
- Support for multiple output languages (English, Dutch, Russian)
- Copy summaries and transcripts to clipboard
- Download transcripts as text files
- Clean and modern UI with dark theme
- Video embedding for preview

## Requirements 📋

- Python 3.8+
- Gemini API key
- Internet connection for YouTube API access

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
   - Paste a YouTube video URL
   - Select from available subtitle languages
   - Choose output language settings (original or translated)
   - Click "Get Subtitle Summary" to process the video subtitles
   - View and interact with the generated summary and transcript

## Features in Detail 🔍

### Input Options
- YouTube URL input with automatic validation
- Support for various YouTube URL formats
- Automatic subtitle language detection

### Subtitle Processing
- Automatic detection of available subtitle languages
- Support for multiple subtitle languages per video
- Clean text extraction from YouTube captions
- Error handling for videos without subtitles

### Language Settings
- Original language processing
- Translation options:
  - English
  - Dutch
  - Russian

### Output Options
- Video summary from subtitles
- Full processed transcript
- Copy to clipboard functionality
- Transcript download as text file

### UI Features
- Dark theme with custom styling
- Video embedding for preview
- Progress indicators
- Expandable sections
- Clear error messages
- Reset functionality

## Limitations 📝

- **Subtitles Required**: Only works with YouTube videos that have subtitles/captions available
- **No Audio Processing**: Does not process audio directly - only uses existing subtitles
- **Internet Required**: Requires internet connection for YouTube API and Gemini API calls
- **YouTube Only**: Only supports YouTube videos, not other video platforms

## Troubleshooting 🔧

If you encounter issues:
1. Verify your Gemini API key is valid
2. Check your internet connection
3. Ensure the YouTube video has subtitles/captions available
4. Try a different video if subtitle extraction fails
5. Check if the YouTube URL is valid and accessible

## Supported YouTube URL Formats 🔗

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`

## Common Issues 🚨

- **"No subtitles available"**: Choose a video with closed captions or auto-generated subtitles
- **"Could not retrieve subtitles"**: The video may have restricted access or the subtitles may be corrupted
- **API errors**: Check your Gemini API key and internet connection
