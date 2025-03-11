# Author: Gus Halwani (https://github.com/fizt656)
# Transcription module for CompExtractor

import whisper  # Import the open source whisper package
from pyannote.audio import Pipeline
import os
import sys
import subprocess
from pydub import AudioSegment
from colorama import Fore, Style
import time
from datetime import datetime
from config import HUGGING_FACE_TOKEN

def convert_to_wav(input_file):
    """Convert audio file to WAV format if needed"""
    if input_file.lower().endswith('.wav'):
        return input_file
    
    output_file = os.path.splitext(input_file)[0] + '.wav'
    try:
        subprocess.run(['ffmpeg', '-i', input_file, output_file], check=True)
        print(f"{Fore.GREEN}Converted {input_file} to {output_file}{Style.RESET_ALL}")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Error converting file to WAV: {e}{Style.RESET_ALL}")
        return None

def split_audio(file_path, max_size_mb=24):
    """Split audio file into chunks to avoid memory issues"""
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
        
        print(f"{Fore.YELLOW}Chunk {i}: Start={chunk_start}ms, End={chunk_end}ms, Duration={chunk_end-chunk_start}ms, Size={os.path.getsize(chunk_file)} bytes{Style.RESET_ALL}")
    
    return chunks

def transcribe_audio(audio_file):
    """Transcribe audio file using Whisper"""
    try:
        # Load the Whisper model (using medium model for good balance of accuracy and speed)
        print(f"{Fore.CYAN}Loading Whisper model...{Style.RESET_ALL}")
        model = whisper.load_model("medium")
        
        # Transcribe the audio file
        print(f"{Fore.CYAN}Transcribing audio...{Style.RESET_ALL}")
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
        print(f"{Fore.RED}Error in transcription: {e}{Style.RESET_ALL}")
        return None

def load_diarization_pipeline():
    """Load the speaker diarization pipeline"""
    try:
        print(f"{Fore.CYAN}Attempting to load the diarization pipeline...{Style.RESET_ALL}")
        pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1",
                                            use_auth_token=HUGGING_FACE_TOKEN)
        print(f"{Fore.GREEN}Diarization pipeline loaded successfully.{Style.RESET_ALL}")
        return pipeline
    except Exception as e:
        print(f"{Fore.RED}Error loading diarization pipeline: {e}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Troubleshooting steps:{Style.RESET_ALL}")
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
    """Transcribe audio and perform speaker diarization if requested"""
    try:
        # Convert to WAV if needed
        wav_file = convert_to_wav(audio_file)
        if wav_file is None:
            return None
            
        # Split audio into chunks
        chunks = split_audio(wav_file)
        transcriptions = []
        
        # Transcribe each chunk
        for chunk in chunks:
            print(f"{Fore.CYAN}Transcribing chunk: {chunk}{Style.RESET_ALL}")
            transcription = transcribe_audio(chunk)
            if transcription is None:
                return None
            transcriptions.extend(transcription)
        
        # Save the transcription before diarization
        save_transcript(transcriptions, audio_file, "before_diarization")

        # If diarization is not requested, return a single speaker transcript
        if not perform_diarization:
            return {"Speaker 1": " ".join([segment['text'] for segment in transcriptions])}

        # Load diarization pipeline and perform diarization
        diarization_pipeline = load_diarization_pipeline()

        print(f"{Fore.MAGENTA}Performing speaker diarization...{Style.RESET_ALL}")
        diarization = diarization_pipeline(wav_file)

        print(f"{Fore.BLUE}Combining transcription with speaker labels...{Style.RESET_ALL}")
        speaker_transcripts = {}
        
        # Assign each segment to a speaker
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

        # Join each speaker's segments into a single transcript
        for speaker in speaker_transcripts:
            speaker_transcripts[speaker] = " ".join(speaker_transcripts[speaker])

        # Save the transcription after diarization
        save_transcript(speaker_transcripts, audio_file, "after_diarization")

        return speaker_transcripts
    except Exception as e:
        print(f"{Fore.RED}Error in transcription and diarization: {e}{Style.RESET_ALL}")
        return None

def save_transcript(transcript, audio_file, stage):
    """Save transcript to a file"""
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
        
        print(f"{Fore.GREEN}Saved {stage} transcript to {filename}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error saving {stage} transcript: {e}{Style.RESET_ALL}")
