from pyannote.audio import Pipeline
import os
from dotenv import load_dotenv
import time

load_dotenv()

HUGGING_FACE_TOKEN = os.getenv('HUGGING_FACE_TOKEN')

def test_diarization():
    try:
        print("Attempting to load the diarization pipeline...")
        start_time = time.time()
        pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1",
                                            use_auth_token=HUGGING_FACE_TOKEN)
        print(f"Diarization pipeline loaded successfully in {time.time() - start_time:.2f} seconds.")
        
        # Test with a small audio file
        audio_file = "test.mp3"
        if not os.path.exists(audio_file):
            print(f"Error: The audio file {audio_file} does not exist.")
            return
        
        print(f"Performing diarization on {audio_file}...")
        start_time = time.time()
        diarization = pipeline(audio_file)
        
        print("Diarization completed. Results:")
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")
        
        print(f"Diarization test completed successfully in {time.time() - start_time:.2f} seconds.")
    except Exception as e:
        print(f"Error in diarization test: {e}")
        print("\nTroubleshooting steps:")
        print("1. Ensure you have an active internet connection.")
        print("2. Verify that you've accepted the user conditions at https://hf.co/pyannote/speaker-diarization")
        print("3. Check that your Hugging Face token is correct in the .env file.")
        print("4. Try running 'huggingface-cli login' in your terminal and enter your token when prompted.")
        print("5. If the issue persists, try clearing your Hugging Face cache:")
        print("   - On macOS/Linux: rm -rf ~/.cache/huggingface")
        print("   - On Windows: rmdir /s /q %USERPROFILE%\\.cache\\huggingface")

if __name__ == "__main__":
    test_diarization()