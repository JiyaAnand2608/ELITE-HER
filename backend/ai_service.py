import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
IS_MOCK = not api_key or "YOUR_GEMINI_API_KEY" in api_key

if not IS_MOCK:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    print("WARNING: Using mock AI service because no GEMINI_API_KEY was found.")
    class MockModel:
        def generate_content(self, prompt):
            class Response:
                def __init__(self, text): self.text = text
            
            if "Extract the following details" in prompt:
                # Extract content from prompt
                content = prompt.split('"{content}"'.replace("{content}", ""))[0] # This is a bit hacky but let's just look at the prompt
                # Actually, the content is at the end of the prompt in the format "{content}"
                
                # Let's just use some logic based on the scenario
                time = "Evening"
                location = "Sector 17 Metro Station"
                person = "Unknown"
                sensory = "Visual/Sound"
                follow_up = "What else do you remember about that moment?"

                if "9:14" in prompt:
                    time = "9:14 PM"
                    sensory = "Audio: Metro Announcement"
                    follow_up = "The announcement played twice—did you notice if anyone else reacted to it?"
                elif "smell" in prompt or "concrete" in prompt:
                    sensory = "Smell: Wet concrete and diesel"
                    follow_up = "Was the smell stronger near the entrance or the stairs?"
                elif "Haryanvi" in prompt or "laughing" in prompt:
                    person = "Group near station"
                    sensory = "Sound: Haryanvi dialect"
                    follow_up = "Could you see how many people were laughing?"
                elif "yellow" in prompt:
                    person = "Person in yellow jacket"
                    sensory = "Color: Bright Yellow"
                    follow_up = "Did you see where that person went after you noticed the jacket?"

                return Response(json.dumps({
                    "time": time,
                    "location": location,
                    "person": person,
                    "sensory": sensory,
                    "follow_up": follow_up
                }))
            else:
                # Structure account
                return Response("""Structured Narrative Account

On the evening of the incident at Sector 17 Metro Station, the survivor (Priya) recalls arriving around 9:00 PM. 

A critical anchor point was established at 9:14 PM, confirmed by a repeated metro announcement due to a technical glitch. This specific fragment places the survivor at the station entrance during a precise 2-minute window. 

Sensory fragments include the smell of wet concrete and diesel, and the sound of a mocking Haryanvi dialect from a group nearby. A person in a bright yellow jacket was observed following closely.

Trauma Science Explainer

Priya's memory is stored as disconnected fragments (sensory 'islands') rather than a linear narrative. This is a biological result of the amygdala's over-activation during the threat, which inhibits the hippocampus from 'time-stamping' the event. The presence of the 9:14 PM announcement as a clear fragment is a 'hard anchor' that allows for precise temporal reconstruction despite the survivor's internal sense of time being distorted by trauma.""")
    model = MockModel()

TAG_PROMPT = """
You are a trauma-informed assistant helping analyze fragments of memory.
Analyze the following memory fragment:
"{content}"

Extract the following details if present:
1. Time (approximate or specific)
2. Location/Place
3. Person(s) involved
4. Sensory details (smell, sound, color, touch)

Also, generate ONE calm, non-leading follow-up question that helps the survivor remember more sensory details without inducing stress. For example, "Was it day or night when you noticed that?" or "Could you remember any specific sounds around you?".

Return the result STRICTLY as a JSON object with keys: "time", "location", "person", "sensory", "follow_up".
If a detail is missing, set the value to null.
"""

def analyze_fragment(content: str):
    try:
        response = model.generate_content(TAG_PROMPT.format(content=content))
        text = response.text.strip()
        
        # Clean up common AI markdown artifacts
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        return json.loads(text)
    except Exception as e:
        print(f"AI Service Error: {e}")
        # Fallback to reasonable defaults if JSON parsing fails
        return {
            "time": None,
            "location": None,
            "person": None,
            "sensory": None,
            "follow_up": "What else do you remember about this moment?"
        }

STRUCTURING_PROMPT = """
You are a legal assistant structuring a trauma-informed account.
Given the following fragments of memory, organize them into a semi-chronological narrative suitable for legal proceedings.
Acknowledge where memory is fragmented or lacks chronology (this is expected in trauma science).

Fragments:
{fragments}

Generate a structured narrative. Start with a header "Structured Narrative Account".
Followed by a separate section titled "Trauma Science Explainer" which explains why this person's memory is stored as fragments (amygdala vs. hippocampus) to help legal professionals understand the context.
"""

def structure_account(fragments: list):
    fragment_text = "\n".join([f"- {f}" for f in fragments])
    try:
        response = model.generate_content(STRUCTURING_PROMPT.format(fragments=fragment_text))
        return response.text
    except Exception as e:
        print(f"AI Service Error during structuring: {e}")
        return f"Error structuring account. Raw fragments recorded:\n{fragment_text}"
