from openai import OpenAI
from pyannote.audio import Pipeline
import requests
import os
import sys
import argparse
from config import *

def transcribe_audio(audio_file):
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        with open(audio_file, "rb") as audio:
            transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio, 
                response_format="text"
            )
        return transcription
    except Exception as e:
        print(f"Error in transcription: {e}")
        return None

def load_diarization_pipeline():
    try:
        return Pipeline.from_pretrained(DIARIZATION_MODEL)
    except Exception as e:
        print(f"Error loading diarization pipeline: {e}")
        sys.exit(1)

def transcribe_and_diarize(audio_file, perform_diarization=False):
    try:
        transcription = transcribe_audio(audio_file)
        if transcription is None:
            return None

        if not perform_diarization:
            return transcription

        diarization_pipeline = load_diarization_pipeline()

        # Perform speaker diarization
        diarization = diarization_pipeline(audio_file)

        # Combine transcription with speaker labels
        diarized_transcript = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segment_start = turn.start
            segment_end = turn.end
            segment_text = transcription[segment_start:segment_end]
            diarized_transcript.append(f"Speaker {speaker}: {segment_text}")

        return "\n".join(diarized_transcript)
    except Exception as e:
        print(f"Error in transcription and diarization: {e}")
        return None

def read_competency_definitions(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading competency definitions: {e}")
        return None

def extract_competency_insights(transcript, competency_definitions):
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": SITE_URL,
            "X-Title": SITE_NAME,
            "Content-Type": "application/json"
        }
        
        prompt = f"""
        Analyze the following transcript and extract insights about student competency development based on the provided competency definitions. Provide an analysis for EACH of the commpetencies in the competency definitions text.  From the transcript, focus on identifying evidence of competency development, areas for improvement, and specific examples from the transcript that demonstrate competency-related behaviors or knowledge.

        Competency Definitions:
        {competency_definitions}

        Transcript:
        {transcript}

        Please provide a structured analysis of competency development, including:
        1. Evidence of competency development for each defined competency
        2. Areas for improvement or further development
        3. Specific examples from the transcript that demonstrate competency-related behaviors or knowledge
        4. Overall assessment of the student's competency development

        Present your analysis in a clear, structured format.
        """
        
        data = {
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(OPENROUTER_URL, headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()

        return response_json['choices'][0]['message']['content']
    except requests.RequestException as e:
        print(f"Error in API request: {e}")
        return None
    except Exception as e:
        print(f"Error in competency insight extraction: {e}")
        return None

def create_html_report(transcript, competency_insights):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Competency Insights Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1, h2 {{
                color: #2c3e50;
            }}
            .section {{
                margin-bottom: 30px;
            }}
            .transcript {{
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                padding: 15px;
                border-radius: 5px;
                white-space: pre-wrap;
                word-wrap: break-word;
            }}
            .transcript p {{
                margin: 0 0 10px 0;
            }}
        </style>
    </head>
    <body>
        <h1>Competency Insights Report</h1>
        
        <div class="section">
            <h2>Transcript</h2>
            <div class="transcript">
                {transcript.replace('\\n', '<br>')}
            </div>
        </div>
        
        <div class="section">
            <h2>Competency Insights</h2>
            {competency_insights}
        </div>
    </body>
    </html>
    """
    return html_content

def main(perform_diarization):
    audio_file = input("Enter the name of the audio file: ")
    competency_file = input("Enter the name of the competencies file: ")

    if not os.path.exists(audio_file):
        print(f"Error: The audio file {audio_file} does not exist.")
        return

    if not os.path.exists(competency_file):
        print(f"Error: The competency definition file {competency_file} does not exist.")
        return

    print("Transcribing audio..." + (" and performing diarization" if perform_diarization else ""))
    transcript = transcribe_and_diarize(audio_file, perform_diarization)
    if transcript is None:
        return

    print("Reading competency definitions...")
    competency_definitions = read_competency_definitions(competency_file)
    if competency_definitions is None:
        return

    print("Extracting competency insights from transcript...")
    competency_insights = extract_competency_insights(transcript, competency_definitions)
    if competency_insights is None:
        return

    html_report = create_html_report(transcript, competency_insights)
    
    print("\nWriting output to report.html...")
    try:
        with open('report.html', 'w', encoding='utf-8') as report_file:
            report_file.write(html_report)
        print("Report successfully written to report.html")
    except Exception as e:
        print(f"Error writing to report.html: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process audio file for transcription, optional diarization, and competency insight extraction.")
    parser.add_argument("--diarize", action="store_true", help="Enable diarization (speaker identification)")
    args = parser.parse_args()

    main(args.diarize)