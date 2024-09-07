![Competency Extractor](banner.jpg)

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
   - Without diarization (default for now, diarization doesn't work YET... coming soon):
     ```bash
     python src/main.py
     ```
   - With diarization (again, this DOES NOT work... YET):
     ```bash
     python src/main.py --diarize
     ```

3. When prompted, enter the names of your audio file and competencies file (you can start with the example files, see [Example Files] below).

4. The script will process the audio and generate a `report.html` file with the transcript and competency insights.

5. Open the `report.html` file in a web browser to view the formatted report.

## Example Files

This repository includes example files for testing:

- `test.mp3`: A short sample audio file of a student reflecting on their experience in general.
- `test.txt`: A sample competencies file
- `test_report.html`: An example of the HTML report generated from the test audio file
- `longer_test.mp3`: A longer sample audio file for more comprehensive testing.
- `longer_test_report.html`: An example of a longer HTML report generated from the longer test audio file.

To run the script with these example files:

1. Make sure you're in the project directory and your virtual environment is activated.
2. Run the script:
   ```bash
   python src/main.py
   ```
3. When prompted, enter:
   - For the audio file: `test.mp3` or `longer_test.mp3`
   - For the competencies file: `test.txt`

This will process the example audio file using the example competencies and generate a `report.html` file with the results.

You can also view the `test_report.html` file in your web browser to see an example of the formatted output without running the script. For a more comprehensive example, check out the `longer_test_report.html` file.

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

## Future Improvements Parking Lot

- Fix API integration for diarization of speakers.
- Add support for batch processing of multiple audio files.
- Develop a user-friendly GUI for easier interaction with the tool.

Other ideas?