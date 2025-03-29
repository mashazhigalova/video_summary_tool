import re

import streamlit as st
import pyperclip as pc

from src.media_processing import *
from src.transcribe import *
from src.llm_actions import *
from src.utils import *


# Set the page configuration (should be at the top)
st.set_page_config(page_title="Video Recap", layout='centered', page_icon=":material/media_link:")

# Background image https://unsplash.com/photos/blue-and-yellow-abstract-painting-1xZ0SqLPE4E
background_image = get_base64('src/background.jpg')  # Replace with your light theme image


st.markdown(style_css(background_image), unsafe_allow_html=True)

st.divider() 
# Initialize session state variables
if "summary" not in st.session_state:
    st.session_state.summary = None
if "raw_transcript" not in st.session_state:
    st.session_state.raw_transcript = None
if "video_title" not in st.session_state:
    st.session_state.video_title = None
if "full_transcript" not in st.session_state:
    st.session_state.full_transcript = None
if "previous_url" not in st.session_state:
    st.session_state.previous_url = None
if "previous_file" not in st.session_state:
    st.session_state.previous_file = None
if "disabled_button" not in st.session_state:
    st.session_state.disabled_button = False  # Default to not disabled
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = None
if "use_original_language" not in st.session_state:
    st.session_state.use_original_language = True  # Initialize language preference
if "language_settings_disabled" not in st.session_state:
    st.session_state.language_settings_disabled = False  # Initialize language settings disabled state

if "url_disabled" not in st.session_state:
    st.session_state.url_disabled = False
if "file_upload_disabled" not in st.session_state:
    st.session_state.file_upload_disabled = False

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 1
if "youtube_key" not in st.session_state:
    st.session_state.youtube_key = 1

if "uploader_expanded" not in st.session_state:
    st.session_state.uploader_expanded = False

if "condition_yt" not in st.session_state:
    st.session_state.condition_yt = False
if "condition_file" not in st.session_state:
    st.session_state.condition_file = False


def clear_outputs():
    st.session_state.summary = None
    st.session_state.raw_transcript = None
    # Deleting temp data 
    print("Clearing temp data..")
    clear_folders()
    print("Temp data cleared!")
    

def main():

    # Callback functions to update state and rerun UI
    def on_youtube_input():
        # Disable file uploader if a valid YouTube URL is provided
        youtube_pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
        condition_yt = st.session_state[f"yt_{st.session_state.youtube_key}"] != '' and re.match(youtube_pattern, st.session_state[f"yt_{st.session_state.youtube_key}"]) is not None  
    
        st.session_state.condition_yt = condition_yt
        if condition_yt:
            st.session_state.file_upload_disabled = True
            st.session_state.uploader_expanded = False

    def on_file_upload():
        st.session_state.condition_file = st.session_state[f"file_{st.session_state.uploader_key}"] is not None
        if st.session_state.condition_file:
            st.session_state.url_disabled = True

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
                st.error("❌ Invalid API key. Please check and try again.")
            

        "[Get a Gemini API key](https://ai.google.dev/gemini-api/docs/api-key)"


    st.text_input(
        "YouTube Link:",
        placeholder="Enter a YouTube video link",
        disabled=st.session_state.url_disabled,
        key=f"yt_{st.session_state.youtube_key}",
        on_change=on_youtube_input
    )

    # File upload section
    with st.expander('Upload Video from a local source', expanded=st.session_state.uploader_expanded):
        st.file_uploader(
            'choose_file', 
            type=["mp4"], 
            label_visibility="hidden", 
            disabled=st.session_state.file_upload_disabled,
            key=f"file_{st.session_state.uploader_key}",
            on_change=on_file_upload
        )

    if st.session_state[f"file_{st.session_state.uploader_key}"] is not None:

        st.video(st.session_state[f"file_{st.session_state.uploader_key}"] )
        st.session_state.video_title = st.session_state[f"file_{st.session_state.uploader_key}"].name
        st.markdown(f'''
            <p style="font-size: 14px; font-weight: bold; color: #1DB954; margin-bottom: 5px;">Video Details</p>
            <div class="small-text"><p style="font-size: 16px; line-height: 1.3; margin-top: 0; margin-bottom: 25px; color: #ffffff;">{st.session_state[f"file_{st.session_state.uploader_key}"].name}</p></div>
        ''', unsafe_allow_html=True)
    
    elif st.session_state.condition_yt:
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

    if st.session_state.summary is not None:
        if (st.session_state.condition_yt  and st.session_state.previous_url != st.session_state[f"yt_{st.session_state.youtube_key}"]):
            clear_outputs()
            st.session_state.disabled_button = False
        elif (st.session_state.condition_file and st.session_state[f"file_{st.session_state.uploader_key}"].name != st.session_state.previous_file):
            clear_outputs()
            st.session_state.disabled_button = False
    

    if st.session_state.condition_yt or st.session_state.condition_file:

        with st.expander("Language settings"):
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

        # Check if API key is enetered
        if not st.session_state.api_key_validated:
            st.error("Please enter and validate your Gemini API key in the sidebar")
            # return
        else:
            # Button to analyze video content
            generate_content_button = st.button("Get Video Content", 
                    type='primary', 
                    use_container_width=True, 
                    on_click=disable,  # Pass function reference, NOT a call
                    disabled=st.session_state.disabled_button)  # Disable if already clicked

            if generate_content_button:
                # Check API key first
                st.session_state.disabled_button = True
                with st.spinner("Processing video..."):
                    try:
                        if st.session_state.condition_yt:
                            # Download audio
                            vidtitle, vidlength, audio_path = extract_audio(youtube=True, url=st.session_state[f"yt_{st.session_state.youtube_key}"])
                            st.session_state.previous_url = st.session_state[f"yt_{st.session_state.youtube_key}"]
                        elif st.session_state[f"file_{st.session_state.uploader_key}"] is not None:
                            vidtitle, vidlength, audio_path = extract_audio(youtube=False, uploaded_file=st.session_state[f"file_{st.session_state.uploader_key}"])
                            st.session_state.previous_file = st.session_state[f"file_{st.session_state.uploader_key}"].name

                        # Transcribe audio
                        transcribed_text = transcribe(vidlength, audio_path)
                        
                        summary = summarize_text(transcribed_text, chosen_language=lang_option, gemini_key=st.session_state.gemini_api_key)
                        full_transcript = get_full_transcription(transcribed_text, gemini_key=st.session_state.gemini_api_key)
                        
                        st.session_state.summary = summary
                        st.session_state.full_transcript = full_transcript
                        st.session_state.raw_transcript = transcribed_text
                        
                        
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
            

    if st.session_state.summary:
        tab1, tab2 = st.tabs(["Summary", "Transcription"])
        with tab1:
            col1, col2 = st.columns([1,3])
            with col1:
                if st.button("Copy Summary", type='secondary', icon=":material/content_copy:"):
                    if copy_to_clipboard(st.session_state.summary):
                        st.success("Summary copied to clipboard!")
                    else:
                        st.info("Copy not available in deployment. Use the download option instead.")
            
            with col2:
                if st.button("Re-generate Summary", type='secondary'):
                    if not st.session_state.gemini_api_key:
                        st.error("Please enter your Gemini API key in the sidebar")
                        return
                    summary = summarize_text(st.session_state.raw_transcript, chosen_language=lang_option, gemini_key=st.session_state.gemini_api_key)
                    st.session_state.summary = summary

            st.markdown(f'''
                <div style="margin-bottom: 15px;">
                    <p style="font-size: 16px; line-height: 1.5; color: #ffffff;">{st.session_state.summary}</p>
                </div>
            ''', unsafe_allow_html=True)

        with tab2:
            col1,col2,_ = st.columns([1,2,1])
            with col1:
                if st.button("Copy Transcript", type='secondary', icon=":material/content_copy:"):
                    if copy_to_clipboard(st.session_state.full_transcript):
                        st.success("Transcript copied to clipboard!")
                    else:
                        st.info("Copy not available in deployment. Use the download option instead.")
            with col2:
                st.download_button(
                    label="Download Transcript",
                    data=st.session_state.full_transcript,
                    icon=":material/download:",
                    file_name=f"Full transcript of {st.session_state.video_title}.txt",
                    mime="text/plain")
            st.markdown(f'''
                <div style="margin-bottom: 15px;">
                    <p style="font-size: 16px; line-height: 1.5; color: #ffffff;">{st.session_state.full_transcript}</p>
                </div>
            ''', unsafe_allow_html=True)
        
    st.divider() 

    if st.button("Start again", type='secondary', icon=':material/refresh:'): 
        st.session_state.url_disabled = False
        st.session_state.file_upload_disabled = False
        st.session_state.disabled_button = False
        st.session_state.uploader_key += 1
        st.session_state.youtube_key +=1
        st.session_state.condition_yt = False
        st.session_state.condition_file = False
        st.session_state.use_original_language = True
        st.session_state.language_settings_disabled = False  # Reset language settings disabled state
        clear_outputs()
        st.rerun()
            
  
if __name__ == "__main__":
    clear_folders()
    main()
