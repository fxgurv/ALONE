def topic(niche: str) -> str:
    info(f"Generating topic for YouTube video about: {niche}")
    completion = generate_response(f"Please generate a specific video idea that takes about the following topic: {niche}. Make it exactly one sentence. Only return the topic, nothing else.")

    if not completion:
        raise ValueError("Failed to generate Topic.")
    
    success(f"Generated topic: {completion}")
    info(f"Topic character count: {len(completion)}")
    return completion

def script(subject: str, language: str) -> str:
    info("Generating script for YouTube video")
    prompt = f"
    Generate a script for a video in 4 sentences, depending on the subject of the video.
    The script is to be returned as a string with the specified number of paragraphs.
    Here is an example of a string:
    "This is an example string."
    Do not under any circumstance reference this prompt in your response.
    Get straight to the point, don't start with unnecessary things like, "welcome to this video".
    Obviously, the script should be related to the subject of the video.
    
    YOU MUST NOT EXCEED THE 4 SENTENCES LIMIT. MAKE SURE THE 4 SENTENCES ARE SHORT.
    YOU MUST NOT INCLUDE ANY TYPE OF MARKDOWN OR FORMATTING IN THE SCRIPT, NEVER USE A TITLE.
    YOU MUST WRITE THE SCRIPT IN THE LANGUAGE SPECIFIED IN [LANGUAGE].
    ONLY RETURN THE RAW CONTENT OF THE SCRIPT. DO NOT INCLUDE "VOICEOVER", "NARRATOR" OR SIMILAR INDICATORS OF WHAT SHOULD BE SPOKEN AT THE BEGINNING OF EACH PARAGRAPH OR LINE. YOU MUST NOT MENTION THE PROMPT, OR ANYTHING ABOUT THE SCRIPT ITSELF. ALSO, NEVER TALK ABOUT THE AMOUNT OF PARAGRAPHS OR LINES. JUST WRITE THE SCRIPT
    
    Subject: {subject}
    Language: {language}
    " 

    
def metadata(subject: str, script: str) -> dict:
    info("Generating metadata for YouTube video")
    title = generate_response(f"Please generate a YouTube Video Title for the following subject, including hashtags: {subject}. Only return the title, nothing else. Limit the title under 100 characters.")

    if len(title) > 100:
        raise ValueError("Generated Title is too long.")

    description = generate_response(f"Please generate a YouTube Video Description for the following script: {script}. Only return the description, nothing else.")
    
    metadata = {
        "title": title,
        "description": description
    }


def prompts(script: str, subject: str) -> List[str]:
    info("Generating image prompts for YouTube video")
    n_prompts = 3
    info(f"Number of prompts requested: {n_prompts}")

    prompt = f"""
    Generate {n_prompts} Image Prompts for AI Image Generation,
    depending on the subject of a video.
    Subject: {subject}

    The image prompts are to be returned as
    a JSON-Array of strings.

    Each search term should consist of a full sentence,
    always add the main subject of the video.

    Be emotional and use interesting adjectives to make the
    Image Prompt as detailed as possible.
    
    YOU MUST ONLY RETURN THE JSON-ARRAY OF STRINGS.
    YOU MUST NOT RETURN ANYTHING ELSE. 
    YOU MUST NOT RETURN THE SCRIPT.
    
    The search terms must be related to the subject of the video.
    Here is an example of a JSON-Array of strings:
    ["image prompt 1", "image prompt 2", "image prompt 3"]

    For context, here is the full text:
    {script}
    """
