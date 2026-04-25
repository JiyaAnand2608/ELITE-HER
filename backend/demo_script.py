import requests
import json

BASE_URL = "http://localhost:8000"

def run_demo():
    print("--- Starting Live Backend Demo ---")
    
    # 1. Create Session
    response = requests.post(f"{BASE_URL}/sessions")
    session_id = response.json()["session_id"]
    print(f"1. Created Session: {session_id}")

    # 2. Add Fragments
    fragments = [
        "I remember the screeching of tires and a bright flash of red.",
        "It was cold, and the streetlights were just flickering on.",
        "A woman in a blue coat was screaming.",
        "I felt a sharp pain in my shoulder when the glass shattered."
    ]

    for i, content in enumerate(fragments, 1):
        print(f"2.{i} Adding Fragment: {content}")
        res = requests.post(
            f"{BASE_URL}/fragments",
            json={"session_id": session_id, "content": content}
        )
        data = res.json()
        print(f"   AI Tagged -> Time: {data.get('tagged_time')}, Location: {data.get('tagged_location')}")
        print(f"   Follow-up: {data.get('follow_up_question')}")

    # 3. Generate PDF
    print("3. Generating Legal Report...")
    res = requests.post(f"{BASE_URL}/sessions/{session_id}/generate-pdf")
    pdf_url = res.json()["pdf_url"]
    print(f"4. PDF Ready at: {BASE_URL}{pdf_url}")
    print("--- Demo Completed Successfully ---")

if __name__ == "__main__":
    run_demo()
