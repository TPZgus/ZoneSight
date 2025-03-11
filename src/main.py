import whisper  # Import the open source whisper package
from pyannote.audio import Pipeline
import requests
import os
import sys
import argparse
import subprocess
import json
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from pydub import AudioSegment
from config import *
from colorama import init, Fore, Back, Style
from playsound import playsound
from pygame import mixer
from cleanup import cleanup_temp_files
import threading
from striprtf.striprtf import rtf_to_text
from datetime import datetime

# Initialize colorama
init(autoreset=True)

def print_colored(text, color=Fore.GREEN, style=Style.BRIGHT):
    print(f"{style}{color}{text}")
    playsound('coin.mp3')

def display_intro():
    intro = f"""
    {Fore.CYAN}███████╗{Fore.MAGENTA}██████╗ {Fore.YELLOW}███╗  ██╗{Fore.GREEN}███████╗{Fore.BLUE}███████╗{Fore.MAGENTA}██╗ ██████╗ {Fore.YELLOW}██╗  ██╗{Fore.CYAN}████████╗
    {Fore.CYAN}   ███╔╝{Fore.MAGENTA}██╔═══██╗{Fore.YELLOW}████╗ ██║{Fore.GREEN}██╔════╝{Fore.BLUE}██╔════╝{Fore.MAGENTA}██║██╔════╝ {Fore.YELLOW}██║  ██║{Fore.CYAN}╚══██╔══╝
    {Fore.CYAN}  ███╔╝ {Fore.MAGENTA}██║   ██║{Fore.YELLOW}██╔██╗██║{Fore.GREEN}█████╗  {Fore.BLUE}███████╗{Fore.MAGENTA}██║██║  ███╗{Fore.YELLOW}███████║{Fore.CYAN}   ██║   
    {Fore.CYAN} ███╔╝  {Fore.MAGENTA}██║   ██║{Fore.YELLOW}██║╚████║{Fore.GREEN}██╔══╝  {Fore.BLUE}╚════██║{Fore.MAGENTA}██║██║   ██║{Fore.YELLOW}██╔══██║{Fore.CYAN}   ██║   
    {Fore.CYAN}███████╗{Fore.MAGENTA}╚██████╔╝{Fore.YELLOW}██║ ╚███║{Fore.GREEN}███████╗{Fore.BLUE}███████║{Fore.MAGENTA}██║╚██████╔╝{Fore.YELLOW}██║  ██║{Fore.CYAN}   ██║   
    {Fore.CYAN}╚══════╝{Fore.MAGENTA} ╚═════╝ {Fore.YELLOW}╚═╝  ╚══╝{Fore.GREEN}╚══════╝{Fore.BLUE}╚══════╝{Fore.MAGENTA}╚═╝ ╚═════╝ {Fore.YELLOW}╚═╝  ╚═╝{Fore.CYAN}   ╚═╝   
                             
{Fore.YELLOW}ZoneSight - Competency Analysis Tool (Using Local Whisper){Style.RESET_ALL}
    """
    print(intro)

def play_background_music():
    mixer.init()
    mixer.music.load('In the Zone.mp3')
    mixer.music.play(-1)  # -1 means loop indefinitely

def stop_background_music():
    mixer.music.stop()

def convert_to_wav(input_file):
    if input_file.lower().endswith('.wav'):
        return input_file
    
    output_file = os.path.splitext(input_file)[0] + '.wav'
    try:
        subprocess.run(['ffmpeg', '-i', input_file, output_file], check=True)
        print_colored(f"Converted {input_file} to {output_file}", Fore.GREEN)
        return output_file
    except subprocess.CalledProcessError as e:
        print_colored(f"Error converting file to WAV: {e}", Fore.RED)
        return None

def split_audio(file_path, max_size_mb=24):
    audio = AudioSegment.from_wav(file_path)
    max_size_bytes = max_size_mb * 1024 * 1024
    duration_ms = len(audio)
    chunk_duration_ms = int((max_size_bytes / len(audio.raw_data)) * duration_ms)
    
    # Create temp directory if it doesn't exist
    temp_dir = "temp"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    chunks = []
    for i, chunk_start in enumerate(range(0, duration_ms, chunk_duration_ms)):
        chunk_end = min(chunk_start + chunk_duration_ms, duration_ms)
        chunk = audio[chunk_start:chunk_end]
        chunk_file = os.path.join(temp_dir, f"chunk_{i}.wav")
        chunk.export(chunk_file, format="wav")
        chunks.append(chunk_file)
        
        print_colored(f"Chunk {i}: Start={chunk_start}ms, End={chunk_end}ms, Duration={chunk_end-chunk_start}ms, Size={os.path.getsize(chunk_file)} bytes", Fore.YELLOW)
    
    return chunks

def transcribe_audio(audio_file):
    try:
        # Load the Whisper model (using medium model for good balance of accuracy and speed)
        print_colored("Loading Whisper model...", Fore.CYAN)
        model = whisper.load_model("medium")
        
        # Transcribe the audio file
        print_colored("Transcribing audio...", Fore.CYAN)
        result = model.transcribe(audio_file)
        
        # Convert the result to match the expected format
        # Whisper's result includes timestamps, so we can use those
        segments = []
        for segment in result["segments"]:
            segments.append({
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"]
            })
        return segments
    except Exception as e:
        print_colored(f"Error in transcription: {e}", Fore.RED)
        return None

def load_diarization_pipeline():
    try:
        print_colored("Attempting to load the diarization pipeline...", Fore.CYAN)
        pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1",
                                            use_auth_token=HUGGING_FACE_TOKEN)
        print_colored("Diarization pipeline loaded successfully.", Fore.GREEN)
        return pipeline
    except Exception as e:
        print_colored(f"Error loading diarization pipeline: {e}", Fore.RED)
        print_colored("\nTroubleshooting steps:", Fore.YELLOW)
        print("1. Ensure you have an active internet connection.")
        print("2. Verify that you've accepted the user conditions at https://huggingface.co/pyannote/speaker-diarization-3.1")
        print("3. Check that your Hugging Face token is correct in the .env file.")
        print("4. Try running 'huggingface-cli login' in your terminal and enter your token when prompted.")
        print("5. If the issue persists, try clearing your Hugging Face cache:")
        print("   - On macOS/Linux: rm -rf ~/.cache/huggingface")
        print("   - On Windows: rmdir /s /q %USERPROFILE%\\.cache\\huggingface")
        print("6. Ensure that you have the latest version of pyannote.audio installed:")
        print("   pip install --upgrade pyannote.audio")
        sys.exit(1)

def transcribe_and_diarize(audio_file, perform_diarization=True):
    try:
        chunks = split_audio(audio_file)
        transcriptions = []
        
        for chunk in chunks:
            print_colored(f"Transcribing chunk: {chunk}", Fore.CYAN)
            transcription = transcribe_audio(chunk)
            if transcription is None:
                return None
            transcriptions.extend(transcription)
        
        # Save the transcription before diarization
        save_transcript(transcriptions, audio_file, "before_diarization")

        if not perform_diarization:
            return {"Speaker 1": " ".join([segment['text'] for segment in transcriptions])}

        diarization_pipeline = load_diarization_pipeline()

        print_colored("Performing speaker diarization...", Fore.MAGENTA)
        diarization = diarization_pipeline(audio_file)

        print_colored("Combining transcription with speaker labels...", Fore.BLUE)
        speaker_transcripts = {}
        
        for segment in transcriptions:
            start_time = segment['start']
            end_time = segment['end']
            text = segment['text']
            
            # Find the speaker for this segment
            speaker = None
            for turn, _, spk in diarization.itertracks(yield_label=True):
                if turn.start <= start_time < turn.end:
                    speaker = spk
                    break
            
            if speaker is None:
                speaker = "Unknown"
            
            if speaker not in speaker_transcripts:
                speaker_transcripts[speaker] = []
            speaker_transcripts[speaker].append(text)

        for speaker in speaker_transcripts:
            speaker_transcripts[speaker] = " ".join(speaker_transcripts[speaker])

        # Save the transcription after diarization
        save_transcript(speaker_transcripts, audio_file, "after_diarization")

        return speaker_transcripts
    except Exception as e:
        print_colored(f"Error in transcription and diarization: {e}", Fore.RED)
        return None

def save_transcript(transcript, audio_file, stage):
    try:
        os.makedirs('results', exist_ok=True)
        base_filename = os.path.splitext(os.path.basename(audio_file))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/transcript_{base_filename}_{stage}_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as file:
            if isinstance(transcript, dict):
                for speaker, text in transcript.items():
                    file.write(f"{speaker}:\n{text}\n\n")
            elif isinstance(transcript, list):
                for segment in transcript:
                    file.write(f"{segment['start']:.2f} - {segment['end']:.2f}: {segment['text']}\n")
            else:
                file.write(str(transcript))
        
        print_colored(f"Saved {stage} transcript to {filename}", Fore.GREEN)
    except Exception as e:
        print_colored(f"Error saving {stage} transcript: {e}", Fore.RED)

def read_competency_definitions(file_path):
    try:
        _, file_extension = os.path.splitext(file_path)
        if file_extension.lower() == '.rtf':
            with open(file_path, 'r') as file:
                rtf_content = file.read()
            return rtf_to_text(rtf_content)
        else:  # Assume it's a .txt file or similar plain text format
            with open(file_path, 'r') as file:
                return file.read()
    except Exception as e:
        print_colored(f"Error reading competency definitions: {e}", Fore.RED)
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
        Analyze the following transcript and extract insights about student competency development based on the provided competency definitions and reporting dimensions. Generate a JSON object that includes an analysis for EACH of the competencies in the competency definitions text. Focus on identifying evidence of competency development across reporting dimensions, and specific examples from the transcript that demonstrate competency-related behaviors or knowledge.

        Competency Definitions:
        {competency_definitions}

        Transcript:
        {transcript}

        Please provide a structured JSON object with the following format for each competency:
        {{
            "competencies": [
                {{
                    "name": "Competency Name",
                    "rating": A numerical rating from 1-10 where:
                             - Emerging level behaviors rate 1-3
                             - Developing level behaviors rate 4-7
                             - Proficient level behaviors rate 8-10
                             Choose a specific number within these ranges based on the evidence,
                    "evidence": [
                        "Specific example or observation from the transcript",
                        "Another example or observation"
                    ],
                    "areas_for_improvement": [
                        "Suggestion for improvement",
                        "Another suggestion"
                    ],
                    "narrative": "A brief narrative explaining the rating and evidence"
                }},
                // ... repeat for all competencies
            ],
            "overall_assessment": "A brief overall assessment of the student's competency development"
        }}

        Important: 
        1. Provide only the JSON object, with no additional text before or after
        2. Ensure all ratings are numerical values between 1 and 10
        3. Base the numerical ratings on the evidence found in the transcript
        4. For each competency:
           - Ratings 1-3 indicate Emerging level behaviors
           - Ratings 4-7 indicate Developing level behaviors
           - Ratings 8-10 indicate Proficient level behaviors
        5. Choose specific numbers within these ranges based on the strength of evidence
        """
        
        data = {
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        print_colored("Extracting competency insights...", Fore.CYAN)
        response = requests.post(OPENROUTER_URL, headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()

        content = response_json['choices'][0]['message']['content'].strip()
        
        # Find the first { and last } to extract just the JSON object
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start == -1 or json_end == 0:
            print_colored("Error: No JSON object found in the response", Fore.RED)
            return {
                "competencies": [],
                "overall_assessment": "Error: No JSON object found in response."
            }
        
        json_content = content[json_start:json_end]
        
        try:
            parsed_data = json.loads(json_content)
        except json.JSONDecodeError as e:
            print_colored(f"Error parsing JSON: {e}", Fore.RED)
            print_colored("Content that failed to parse:", Fore.YELLOW)
            print(json_content[:500] + "..." if len(json_content) > 500 else json_content)
            return {
                "competencies": [],
                "overall_assessment": "Error analyzing competencies."
            }
        
        if 'competencies' not in parsed_data or 'overall_assessment' not in parsed_data:
            print_colored("Error: Parsed data does not have the expected structure", Fore.RED)
            return {
                "competencies": [],
                "overall_assessment": "Error: Missing required data structure."
            }

        # Ensure all ratings are numerical
        for competency in parsed_data['competencies']:
            if not isinstance(competency['rating'], (int, float)):
                try:
                    competency['rating'] = float(competency['rating'])
                except (ValueError, TypeError):
                    competency['rating'] = 5  # Default to middle value if conversion fails
            # Ensure rating is within bounds
            competency['rating'] = max(1, min(10, competency['rating']))

        print_colored("Competency insights extracted successfully.", Fore.GREEN)
        return parsed_data
    except requests.RequestException as e:
        print_colored(f"Error in API request: {e}", Fore.RED)
        return {
            "competencies": [],
            "overall_assessment": f"Error in API request: {str(e)}"
        }
    except Exception as e:
        print_colored(f"Error in competency insight extraction: {e}", Fore.RED)
        return {
            "competencies": [],
            "overall_assessment": f"Error in analysis: {str(e)}"
        }

def generate_structured_json(competency_data, audio_filename=None, person_id=1):
    """
    Generate a structured JSON output from the competency data.
    
    Args:
        competency_data: Dictionary containing competency analysis data
        audio_filename: Name of the source audio file
        person_id: Identifier for the person being analyzed
        
    Returns:
        JSON string representation of the structured data
    """
    # Initialize the result structure
    result = {
        "person_id": person_id,
        "source": audio_filename or "Unknown",
        "timestamp": datetime.now().isoformat(),
        "competencies": {}
    }
    
    # Handle both single and multiple speaker scenarios
    speakers = list(competency_data.keys())
    for speaker in speakers:
        data = competency_data[speaker]
        
        # For each competency, extract the relevant information
        for competency in data['competencies']:
            name = competency['name'].lower().replace(' ', '_')
            result["competencies"][name] = {
                "value": competency['rating'],
                "evidence": competency['narrative'],
                "areas_for_improvement": competency['areas_for_improvement'],
                "examples": competency['evidence']
            }
    
    return json.dumps(result, indent=2)

def generate_combined_report(competency_data, audio_filename=None):
    # First, let's download Plotly.js
    plotly_js_url = "https://cdn.plot.ly/plotly-latest.min.js"
    plotly_js_content = requests.get(plotly_js_url).text

    combined_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ZoneSight Competency Report</title>
        <script>{plotly_js_content}</script>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; }}
            h1, h2, h3 {{ color: #2c3e50; }}
            .file-info {{ background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 20px; border-left: 4px solid #2c3e50; }}
            .speaker-section {{ border: 1px solid #ddd; padding: 20px; margin-bottom: 20px; border-radius: 5px; }}
            .radar-chart {{ width: 100%; height: 500px; }}
            .competency-item {{ margin-bottom: 20px; }}
            .rating {{ font-weight: bold; }}
            .evidence, .areas-for-improvement {{ margin-left: 20px; }}
        </style>
    </head>
    <body>
        <h1>ZoneSight Competency Report</h1>
        
        <div class="file-info">
            <h3>Analysis Information</h3>
            <p><strong>Source File:</strong> {audio_filename or "Unknown"}</p>
            <p><strong>Analysis Date:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
        <p><strong>Note:</strong> If the radar chart is not visible, please ensure you're opening this file with a web browser and that JavaScript is enabled.</p>
    """

    # Handle both single and multiple speaker scenarios
    speakers = list(competency_data.keys())
    for speaker in speakers:
        data = competency_data[speaker]

        combined_html += f"""
        <div class="speaker-section">
            <h2>{speaker}</h2>
            <div id="radar-chart-{speaker}" class="radar-chart"></div>
        """
        
        for competency in data['competencies']:
            combined_html += f"""
                <div class="competency-item">
                    <h3>{competency['name']}</h3>
                    <p class="rating">Rating: {competency['rating']}</p>
                    <p>{competency['narrative']}</p>
                    <h4>Evidence:</h4>
                    <ul class="evidence">
                        {"".join(f"<li>{evidence}</li>" for evidence in competency['evidence'])}
                    </ul>
                    <h4>Areas for Improvement:</h4>
                    <ul class="areas-for-improvement">
                        {"".join(f"<li>{area}</li>" for area in competency['areas_for_improvement'])}
                    </ul>
                </div>
            """
        
        combined_html += f"""
            <h3>Overall Assessment</h3>
            <p>{data['overall_assessment']}</p>
            <script>
                (function() {{
                    try {{
                        console.log('Attempting to create chart for {speaker}');
                        var data = {json.dumps(data)};
                        Plotly.newPlot('radar-chart-{speaker}', [{{
                            type: 'scatterpolar',
                            r: data.competencies.map(comp => comp.rating),
                            theta: data.competencies.map(comp => comp.name),
                            fill: 'toself'
                        }}], {{
                            polar: {{ radialaxis: {{ visible: true, range: [0, 10] }} }},
                            showlegend: false,
                            title: 'Competency Radar Chart for {speaker}'
                        }}).then(function() {{
                            console.log('Chart for {speaker} created successfully');
                        }}).catch(function(err) {{
                            console.error('Error creating chart for {speaker}:', err);
                        }});
                    }} catch (error) {{
                        console.error('Error in chart creation for {speaker}:', error);
                    }}
                }})();
            </script>
        </div>
        """

    combined_html += """
    <script>
        console.log('All charts should be created now. If you don\'t see them, check the console for errors.');
    </script>
    </body>
    </html>
    """

    return combined_html

def main():
    display_intro()
    
    # Start playing background music
    background_music_thread = threading.Thread(target=play_background_music)
    background_music_thread.start()

    audio_file = input(f"{Fore.YELLOW}Enter the name of the audio file: {Style.RESET_ALL}")
    competency_file = input(f"{Fore.YELLOW}Enter the name of the competencies file (TXT or RTF): {Style.RESET_ALL}")
    
    # Ask user if they want to perform diarization
    perform_diarization = input(f"{Fore.YELLOW}Do you want to perform diarization? (yes/no): {Style.RESET_ALL}").lower() == 'yes'

    if not os.path.exists(audio_file):
        print_colored(f"Error: The audio file {audio_file} does not exist.", Fore.RED)
        return
    if not os.path.exists(competency_file):
        print_colored(f"Error: The competency definition file {competency_file} does not exist.", Fore.RED)
        return
    if not os.path.exists('sound.mp3'):
        print_colored(f"Error: The sound file sound.mp3 does not exist.", Fore.RED)
        return
    if not os.path.exists('coin.mp3'):
        print_colored(f"Error: The sound file coin.mp3 does not exist.", Fore.RED)
        return
    if not os.path.exists('In the Zone.mp3'):
        print_colored(f"Error: The sound file In the Zone.mp3 does not exist.", Fore.RED)
        return

    wav_file = convert_to_wav(audio_file)
    if wav_file is None:
        return

    print_colored(f"{'[INIT]':=^40}", Fore.CYAN)
    print_colored("Transcribing audio..." + (" and performing diarization..." if perform_diarization else ""), Fore.CYAN)
    print_colored(f"{'[PROCESSING]':=^40}", Fore.CYAN)
    
    speaker_transcripts = transcribe_and_diarize(wav_file, perform_diarization)
    if speaker_transcripts is None:
        stop_background_music()
        return

    print_colored("Reading competency definitions...", Fore.CYAN)
    competency_definitions = read_competency_definitions(competency_file)
    if competency_definitions is None:
        stop_background_music()
        return

    competency_data = {}

    # Handle both single and multiple speaker scenarios
    if len(speaker_transcripts) == 1 and "Speaker 1" in speaker_transcripts:
        speaker = "Single Speaker"
        transcript = speaker_transcripts["Speaker 1"]
        print_colored(f"Extracting competency insights for {speaker}...", Fore.CYAN)
        competency_data[speaker] = extract_competency_insights(transcript, competency_definitions)
    else:
        for speaker, transcript in speaker_transcripts.items():
            print_colored(f"Extracting competency insights for {speaker}...", Fore.CYAN)
            competency_data[speaker] = extract_competency_insights(transcript, competency_definitions)

    print_colored("Generating combined report...", Fore.CYAN)
    combined_report = generate_combined_report(competency_data)

    print_colored("\nWriting output to results folder...", Fore.CYAN)
    try:
        # Create the results directory if it doesn't exist
        os.makedirs('results', exist_ok=True)
        
        # Generate filename with audio file name and timestamp
        base_filename = os.path.splitext(os.path.basename(audio_file))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"results/combined_report_{base_filename}_{timestamp}.html"
        
        with open(output_filename, 'w', encoding='utf-8') as report_file:
            report_file.write(combined_report)
        print_colored(f"Combined report successfully written to {output_filename}", Fore.GREEN)
        print_colored(f"To view the report with radar charts, please open the HTML file in a web browser.", Fore.YELLOW)

        print_colored(f"{'[COMPLETE]':=^40}", Fore.GREEN)
        
        # Stop background music and play completion sound
        stop_background_music()
        playsound('sound.mp3')
        print_colored("Played completion sound", Fore.GREEN)

        # Clean up temporary files
        cleanup_temp_files()
        print_colored("Temporary files cleaned up", Fore.GREEN)
    except Exception as e:
        print_colored(f"Error writing output: {e}", Fore.RED)
        stop_background_music()

if __name__ == "__main__":
    main()
