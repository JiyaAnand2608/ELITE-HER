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
                return Response(json.dumps({
                    "time": "Evening",
                    "location": "Near a park",
                    "person": "A stranger",
                    "sensory": "Smell of damp earth",
                    "follow_up": "What color was the sky then?"
                }))
            else:
                return Response("Structured Narrative Account\n\nThis is a mock structured narrative for demo purposes.\n\nTrauma Science Explainer\n\nTrauma memory is often fragmented due to amygdala activation.")
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
