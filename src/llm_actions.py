from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langdetect import detect
from typing import Literal


def detect_language(text: str) -> str:
    """Detect the language of the input text.

    Args:
        text (str): The text to analyze for language detection.

    Returns:
        str: The detected language code (e.g., 'en' for English).
    """
    try:
        lang = detect(text)
    except Exception as e:
        lang = "English"
    return lang
    
def create_prompt(type: Literal["summary", "full_transcript"] = 'summary') -> str:
    """
    Build a structured prompt for a task.

    Args:
        type (Literal["summary", "full_transcript"], optional): The type of prompt to create. Defaults to 'summary'.

    Returns:
        str: The constructed prompt string.
    """
    if type == 'summary':
        prompt = """
            Act as an expert editor and writer specializing in content optimization. Your task is to take a given video transcript and transform it into a well-structured text. 
            The transcript is in {detected_language}; the output text should be written in {chosen_language}.
            Instructions:

            * Transformation the content: Begin by thoroughly reading the provided transcript. Understand the main ideas, key points, and the overall message conveyed.
            * Identify Key Points: Extract the main ideas, events, or arguments presented in the transcript.
            * Preserve Context: Maintain the original meaning while condensing the text.
            * Keep it Coherent: Ensure the summary flows naturally and is easy to understand.
            * Omit Redundancies: Remove filler words, repetitions, and irrelevant details. Keep it concise.
            * Use a Clear Structure: If possible, summarize in bullet points or short paragraphs for clarity. Use bold text or italics to highlight important concepts or words.

            Transcript:
            {input_text}
            """
    elif type == 'full_transcript':
        prompt = ("""You are an expert editor and writer. Your task is to transform a raw transcription of spoken text into a well-formatted, natural, and structured text.

                Instructions:
                * Use the same language as the original transcription.
                * Ensure smooth readability by correcting grammar, punctuation, and sentence structure.
                * Remove filler words, hesitations, and redundancies while preserving the speaker's intent, tone, and meaning.
                * Do not add or invent new content beyond minor adjustments for clarity.
                Raw Transcription:
                {input_text}
                Output:
                Return the cleaned and formatted text in its original language, without additional commentary.""")

    return prompt


def summarize_text(input_text: str, chosen_language: str, gemini_key:str) -> str:
    """
    Summarizes the given text using Gemini API.

    Args:
        input_text (str): The text to summarize.
        chosen_language (str): The language in which the summary should be written.
        gemini_key (str): Gemini API key.

    Returns:
        str: The generated summary.
    """
    system_template = create_prompt()

    # Detect the language of the input text
    detected_language = detect_language(input_text)
    # Set chosen language to detected if selected to work with original language
    if chosen_language == "":
        chosen_language = detected_language

    try:
        print(f"Summarizing text in {chosen_language}..")
        prompt_template = ChatPromptTemplate.from_messages(
            [("system", system_template), ("user", "{input_text}")]
        )
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-001", google_api_key=gemini_key)

        prompt = prompt_template.invoke({"detected_language": detected_language, "chosen_language": chosen_language, "input_text": input_text})

        response = llm.invoke(prompt)
        print(f"Summarization complete!")
        return response.content

    except Exception as e:
        raise RuntimeError(f"Error during summarization: {str(e)}")


def get_full_transcription(input_text: str, gemini_key:str) -> str:
    """
    Creates a full, well-formatted transcription of the input text.

    Args:
        input_text (str): The raw transcription text to format.
        gemini_key (str): Gemini API key.
        
    Returns:
        str: The cleaned and formatted transcription.
    """
    system_template = create_prompt(type='full_transcript')

    try:
        print(f"Creating full transcript..")
        prompt_template = ChatPromptTemplate.from_messages(
            [("system", system_template), ("user", "{input_text}")]
        )
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-001", google_api_key=gemini_key)

        prompt = prompt_template.invoke({"input_text": input_text})
        response = llm.invoke(prompt)

        print(f"Full transcript created!")
        return response.content

    except Exception as e:
        raise RuntimeError(f"Error during creating full transcript: {str(e)}")
