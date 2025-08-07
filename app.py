import re
import time

import streamlit as st

from src.media_processing import get_video_info, find_captions, retrieve_subtitles
# Removed: from src.transcribe import *
from src.llm_actions import *
from src.utils import *


# Set the page configuration (should be at the top)
st.set_page_config(page_title="YouTube Summarizer", layout='centered', page_icon=":material/subtitles:")

# Background image https://unsplash.com/photos/blue-and-yellow-abstract-painting-1xZ0SqLPE4E
background_image = get_base64('src/background.jpg')  # Replace with your light theme image

st.markdown(style_css(background_image), unsafe_allow_html=True)

st.divider() 

# Initialize session state variables
if "summary" not in st.session_state:
    st.session_state.summary = None
if "full_transcript" not in st.session_state:
    st.session_state.full_transcript = None
if "video_title" not in st.session_state:
    st.session_state.video_title = None
if "previous_url" not in st.session_state:
    st.session_state.previous_url = None
if "disabled_button" not in st.session_state:
    st.session_state.disabled_button = False  # Default to not disabled
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = None
if "use_original_language" not in st.session_state:
    st.session_state.use_original_language = True  # Initialize language preference
if "language_settings_disabled" not in st.session_state:
    st.session_state.language_settings_disabled = False  # Initialize language settings disabled state

if "youtube_key" not in st.session_state:
    st.session_state.youtube_key = 1

if "condition_yt" not in st.session_state:
    st.session_state.condition_yt = False

def clear_outputs():
    st.session_state.summary = None
    st.session_state.full_transcript = None
    

def main():
    # Callback functions to update state and rerun UI
    def on_youtube_input():
        # Check if valid YouTube URL is provided
        youtube_pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
        condition_yt = st.session_state[f"yt_{st.session_state.youtube_key}"] != '' and re.match(youtube_pattern, st.session_state[f"yt_{st.session_state.youtube_key}"]) is not None  
    
        st.session_state.condition_yt = condition_yt

    with st.sidebar:
        st.markdown('<div class="area-title">Input your Gemini API key</div>', unsafe_allow_html=True)
        
        # Create a container for the API key input and validation
        api_container = st.container()
        
        # Initialize validation state if not exists
        if "api_key_validated" not in st.session_state:
            st.session_state.api_key_validated = False
        
        # Create the text input
        new_key = api_container.text_input("Gemini API Key", type="password", key="gemini_api_key")

        if st.button("Validate API Key"):
            try:
                llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-001", google_api_key=new_key)
                response = llm.invoke("Test connection")
                st.session_state.api_key_validated = True
                st.success("API key is validated and ready to use")
            except Exception:
                st.session_state.api_key_validated = False
                st.error("Invalid API key. Please check and try again.")
            

        "[Get a Gemini API key](https://ai.google.dev/gemini-api/docs/api-key)"

    # YouTube URL input
    st.text_input(
        "YouTube Link:",
        placeholder="Enter a YouTube video link",
        key=f"yt_{st.session_state.youtube_key}",
        on_change=on_youtube_input
    )

    # Display video if valid URL is provided
    if st.session_state.condition_yt:
        # VIDEO section
        st.markdown('<div class="area-title">Your Video</div>', unsafe_allow_html=True)
        emb_youtube_url = convert_youtube_url(st.session_state[f"yt_{st.session_state.youtube_key}"])
        st.markdown(f'<iframe width="100%" height="450" src="{emb_youtube_url}" frameBorder="0" allow="clipboard-write; autoplay" webkitAllowFullScreen mozallowfullscreen allowFullScreen></iframe>', unsafe_allow_html=True)
        
        vid_info = get_video_info(st.session_state[f"yt_{st.session_state.youtube_key}"])
        title = vid_info["title"]
        st.session_state.video_title = title
        length = vid_info["length"]
        
        st.markdown(f'''
            <p style="font-size: 14px; font-weight: bold; color: #1DB954; margin-bottom: 5px;">Video Details</p>
            <div class="small-text"><p style="font-size: 16px; line-height: 1.3; margin-top: 0; margin-bottom: 25px; color: #ffffff;">{title}</p></div>
            <p style="font-size: 14px; font-weight: bold; color: #1DB954; display: inline;">Length: </p>
            <p style="font-size: 14px; color: #ffffff; font-weight: normal; display: inline;">{length}</p>
            <p style="margin-bottom: 30px;"></p>
        ''', unsafe_allow_html=True)

    # Check if previous URL changed to clear outputs
    if st.session_state.summary is not None:
        if (st.session_state.condition_yt and st.session_state.previous_url != st.session_state[f"yt_{st.session_state.youtube_key}"]):
            clear_outputs()
            st.session_state.disabled_button = False

    if st.session_state.condition_yt:
        # Section for captions
        with st.expander("Subtitle Settings", expanded=True):
            captions = find_captions(st.session_state[f"yt_{st.session_state.youtube_key}"])
            lang_list = list(captions.values())
            
            if not lang_list:
                st.error("No subtitles available for this video. Please try a different video.")
                captions_lang = None
            else:
                st.success(f"Found {len(lang_list)} subtitle language(s)")
                captions_lang = st.selectbox(
                    "Available subtitle languages:",
                    lang_list,
                    index=0
                )

        # Language settings
        with st.expander("Summary language settings"):
            col1, col2 = st.columns([1,1])
            with col1:
                st.session_state.use_original_language = st.toggle(
                    "Use original language", 
                    value=st.session_state.use_original_language,
                    disabled=st.session_state.language_settings_disabled
                )
            with col2:
                lang_option = st.selectbox(
                    "What language do you prefer?",
                    ("English", "Dutch", "Russian"),
                    disabled=st.session_state.use_original_language or st.session_state.language_settings_disabled,
                )
        if st.session_state.use_original_language:
            lang_option = ""
        
        st.markdown('<p style="margin-bottom: 30px;"></p>', unsafe_allow_html=True)

        # Callback function to disable the button and language settings
        def disable():
            st.session_state.disabled_button = True
            st.session_state.language_settings_disabled = True

        # Check if API key is entered and subtitles are available
        if not st.session_state.api_key_validated:
            st.error("Please enter and validate your Gemini API key in the sidebar")
        elif not lang_list:
            st.error("Cannot process video without subtitles. Please choose a video with available subtitles.")
        else:
            # Button to analyze subtitle content
            generate_content_button = st.button("Get Subtitle Summary", 
                    type='primary', 
                    use_container_width=True, 
                    on_click=disable,  # Pass function reference, NOT a call
                    disabled=st.session_state.disabled_button)  # Disable if already clicked

            if generate_content_button:
                start_time = time.time()
                # Check API key first
                st.session_state.disabled_button = True
                with st.spinner("Processing subtitles..."):

                    try:
                        # Get subtitles
                        if captions_lang is None:
                            st.error("No subtitle language selected.")
                            st.session_state.disabled_button = False
                            return
                            
                        subtitles_text = retrieve_subtitles(st.session_state[f"yt_{st.session_state.youtube_key}"], captions_lang)
                        
                        if not subtitles_text.strip():
                            st.error("Could not retrieve subtitles. Please try a different video.")
                            st.session_state.disabled_button = False
                            return
                        
                        st.info(f"Using subtitles in {captions_lang}", icon=":material/closed_caption:")
                        
                        # Process subtitles
                        summary = summarize_text(subtitles_text, chosen_language=lang_option, gemini_key=st.session_state.gemini_api_key)
                        full_transcript = get_full_transcription(subtitles_text, gemini_key=st.session_state.gemini_api_key)
                        
                        st.session_state.summary = summary
                        st.session_state.full_transcript = full_transcript
                        st.session_state.previous_url = st.session_state[f"yt_{st.session_state.youtube_key}"]

                        end_time = time.time()  # End timer
                        elapsed_time = end_time - start_time  # Calculate duration
                        st.info(f"Time taken: {elapsed_time:.2f} seconds", icon=":material/timer:")
                        
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                        st.session_state.disabled_button = False

    if st.session_state.summary:
        tab1, tab2 = st.tabs(["Summary", "Full Transcript"])
        with tab1:
            col1, col2 = st.columns([2,1])
            with col1:
                if st.button("Re-generate Summary", type='secondary'):
                    if not st.session_state.gemini_api_key:
                        st.error("Please enter your Gemini API key in the sidebar")
                        return
                    # Re-get subtitles and regenerate summary
                    captions = find_captions(st.session_state[f"yt_{st.session_state.youtube_key}"])
                    lang_list = list(captions.values())
                    if lang_list:
                        subtitles_text = retrieve_subtitles(st.session_state[f"yt_{st.session_state.youtube_key}"], lang_list[0])
                        summary = summarize_text(subtitles_text, chosen_language=lang_option, gemini_key=st.session_state.gemini_api_key)
                        st.session_state.summary = summary

            st.markdown(f'''
                <div style="margin-bottom: 15px;">
                    <p style="font-size: 16px; line-height: 1.5; color: #ffffff;">{st.session_state.summary}</p>
                </div>
            ''', unsafe_allow_html=True)

        with tab2:
            col1,col2,_ = st.columns([2,1,1])
            with col1:
                st.download_button(
                    label="Download Transcript",
                    data=st.session_state.full_transcript,
                    icon=":material/download:",
                    file_name=f"Transcript of {st.session_state.video_title}.txt",
                    mime="text/plain")

            st.markdown(f'''
                <div style="margin-bottom: 15px;">
                    <p style="font-size: 16px; line-height: 1.5; color: #ffffff;">{st.session_state.full_transcript}</p>
                </div>
            ''', unsafe_allow_html=True)
        
    st.divider() 

    if st.button("Start again", type='secondary', icon=':material/refresh:'): 
        st.session_state.disabled_button = False
        st.session_state.youtube_key += 1
        st.session_state.condition_yt = False
        st.session_state.use_original_language = True
        st.session_state.language_settings_disabled = False
        clear_outputs()
        st.rerun()
            
  
if __name__ == "__main__":
    main()
