# Competency Extractor

This is a prototype tool for extracting student competency insights from audio recordings of student presentations or discussions.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/fizt656/compextractor.git
   cd compextractor
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

5. Copy the `.env.example` file to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file with your actual API keys.

## Usage

1. Prepare your audio file (supported formats include MP3, MP4, WAV) and competencies file (a text file with competency definitions).

2. Run the script:
   - Without diarization (default):
     ```bash
     python src/main.py
     ```
   - With diarization:
     ```bash
     python src/main.py --diarize
     ```

3. When prompted, enter the names of your audio file and competencies file (you can start w the example files, see [Example Files] below).

4. The script will process the audio and generate a `report.txt` file with the transcript and competency insights.

## Example Files

This repository includes example files for testing:

- `test.mp3`: A short sample audio file of a student reflecting on their experience in general.
- `test.txt`: A sample competencies file

To run the script with these example files:

1. Make sure you're in the project directory and your virtual environment is activated.
2. Run the script:
   ```bash
   python src/main.py
   ```
3. When prompted, enter:
   - For the audio file: `test.mp3`
   - For the competencies file: `test.txt`

This will process the example audio file using the example competencies and generate a `report.txt` file with the results.

## Notes and Recommendations

- Change the system prompt in main.py to suit different needs.  

- Try different ways of querying the competencies text file re: the transcript.

- You can change LLMs by editing config.py.  As of 08/2024, Claude 3.5 Sonnet is recommended:

  ```
  anthropic/claude-3.5-sonnet
  ``` 

  or Cohere's Command R+: 
  ```
  cohere/command-r-plus-08-2024
  ```


OpenRouter provides access to all frontier models, closed and open-source, as well as smaller more specialized models.


- This is a clunky prototype from a script kid type.  Let's break it, and then make it better!