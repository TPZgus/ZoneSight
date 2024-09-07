![Competency Extractor](banner.jpg)

# Competency Extractor

This is a prototype tool for extracting student competency insights from audio recordings of student presentations or discussions.

## Prerequisites

- Python 3.7 or higher
- ffmpeg (for audio file conversion)

## Installation

1. Install ffmpeg:
   - On Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add it to your system PATH.
   - On macOS: Use Homebrew: `brew install ffmpeg`
   - On Linux: Use your package manager, e.g., `sudo apt-get install ffmpeg`

2. Clone this repository:
   ```bash
   git clone https://github.com/fizt656/compextractor.git
   cd compextractor
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

4. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```bash
     source venv/bin/activate
     ```

5. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

6. Copy the `.env.example` file to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file with your actual API keys.

7. Set up the Hugging Face token:
   - Go to [Hugging Face](https://huggingface.co/) and create an account if you don't have one.
   - Generate an access token in your account settings.
   - Add the token to your `.env` file:
     ```
     HUGGING_FACE_TOKEN=your_token_here
     ```
   - Run `huggingface-cli login` in your terminal and enter your token when prompted.

8. Accept the user conditions for the pyannote/speaker-diarization model:
   - Visit https://huggingface.co/pyannote/speaker-diarization
   - Click on "Access repository" and accept the terms.

## Usage

1. Prepare your audio file (supported formats include MP3, MP4, WAV) and competencies file (a text file with competency definitions).

2. Run the script:
   - Without diarization:
     ```bash
     python src/main.py
     ```
   - With diarization:
     ```bash
     python src/main.py --diarize
     ```

3. When prompted, enter the names of your audio file and competencies file (you can start with the example files, see [Example Files] below).

4. The script will automatically convert non-WAV audio files to WAV format for processing.

5. For large audio files, the script will automatically split them into smaller chunks to avoid API limitations.

6. The script will process the audio and generate a `report.html` file with the transcript and competency insights.

7. Open the `report.html` file in a web browser to view the formatted report.

## Example Files

This repository includes example files for testing:

- `test.mp3`: A short sample audio file of a student reflecting on their experience in general.
- `test.txt`: A sample competencies file
- `test_report.html`: An example of the HTML report generated from the test audio file
- `longer_test.mp3`: A longer sample audio file for more comprehensive testing.
- `longer_test_report.html`: An example of a longer HTML report generated from the longer test audio file.
- `multi-speaker-discussion.mp3`: A sample file for testing diarization (speaker identification) and large file handling.

To run the script with these example files:

1. Make sure you're in the project directory and your virtual environment is activated.
2. Run the script:
   ```bash
   python src/main.py
   ```
   or with diarization:
   ```bash
   python src/main.py --diarize
   ```
3. When prompted, enter:
   - For the audio file: `test.mp3`, `longer_test.mp3`, or `multi-speaker-discussion.mp3`
   - For the competencies file: `test.txt`

This will process the example audio file using the example competencies and generate a `report.html` file with the results.

You can also view the `test_report.html` or `longer_test_report.html` file in your web browser to see examples of the formatted output without running the script.

## Handling Large Audio Files

The script now automatically handles large audio files by splitting them into smaller chunks before processing. This allows for processing of files that would otherwise exceed the API's content size limit. The process is transparent to the user and doesn't require any additional steps.

## Longer Test Output

We've included a more comprehensive example output in the `longer_test_report.html` file. This report showcases a more detailed analysis of student competencies based on a longer audio sample. To view this report:

1. Open the `longer_test_report.html` file in your web browser.
2. You'll see a detailed transcript of the student's response, followed by in-depth insights into various competencies such as Growth Mindset, STEAM Interest, Creativity, Adaptability, Problem Solving, and more.
3. Each competency section includes:
   - Evidence of competency development
   - Areas for improvement
   - Specific examples from the transcript
4. The report concludes with an overall assessment of the student's competency development.

This longer test output demonstrates the tool's capability to provide nuanced and comprehensive insights into student competencies based on more extensive input.

## Notes and Recommendations

- Change the system prompt in main.py to suit different needs.  

- Try different ways of querying the competencies text file with respect to the transcript.

- You can change LLMs by editing config.py. As of 08/2024, Claude 3.5 Sonnet is recommended:

  ```
  anthropic/claude-3.5-sonnet
  ``` 

  or Cohere's Command R+: 
  ```
  cohere/command-r-plus-08-2024
  ```

OpenRouter provides access to all frontier models, closed and open-source, as well as smaller more specialized models.

Let's break it, and then make it better!

## Troubleshooting

If you encounter issues with the diarization pipeline, try the following steps:

1. Ensure you have an active internet connection.
2. Verify that you've accepted the user conditions at https://hf.co/pyannote/speaker-diarization
3. Check that your Hugging Face token is correct in the .env file.
4. Try running 'huggingface-cli login' in your terminal and enter your token when prompted.
5. If the issue persists, try clearing your Hugging Face cache:
   - On macOS/Linux: `rm -rf ~/.cache/huggingface`
   - On Windows: `rmdir /s /q %USERPROFILE%\.cache\huggingface`

If you're having trouble with large audio files:
1. The script now automatically handles large files by splitting them into smaller chunks.
2. If you still encounter issues, try manually splitting your audio file into smaller segments using audio editing software before processing.

## Future Improvements Parking Lot

- Add support for batch processing of multiple audio files.
- Develop a user-friendly GUI for easier interaction with the tool.
- Improve diarization accuracy and integration with the transcript.
- Optimize the handling of large audio files for better performance.

Other ideas? Feel free to contribute or suggest improvements!