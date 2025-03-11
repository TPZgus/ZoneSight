![CompExtractor Banner](banner.jpeg)

# CompExtractor - Competency Analysis Tool

A powerful tool that combines audio analysis and portfolio assessment to extract competency insights across multiple dimensions, combining local processing with cloud services.

## Table of Contents
- [Overview](#overview)
- [Components](#components)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [GUI Version](#gui-version)
    - [Audio Reflection Interface](#audio-reflection-interface)
    - [Portfolio Interface](#portfolio-interface)
  - [Command Line Version](#command-line-version)
- [Output](#output)
  - [Audio Analysis Output](#audio-analysis-output)
  - [Portfolio Analysis Output](#portfolio-analysis-output)
  - [Directory Structure](#directory-structure)
- [LLM Provider](#llm-provider)
- [System Requirements](#system-requirements)
- [Troubleshooting](#troubleshooting)

## Overview

CompExtractor analyzes both audio recordings and portfolios to extract competency insights, providing detailed reports on key competency dimensions. The tool combines local processing with cloud services:

- For audio analysis: Local transcription with cloud-based speaker diarization and competency analysis
- For portfolio analysis: Web page conversion to PDF and cloud-based competency analysis

## Components

### Local Processing
- **Transcription**: Uses OpenAI's Whisper locally (no API key needed)
  - Runs completely offline
  - Uses local GPU/CPU for processing
  - Supports multiple languages
  - Downloads model files on first use (~1.5GB for medium model)

### Cloud Services Required
1. **Speaker Diarization**: Uses pyannote.audio (requires Hugging Face token)
   - Requires accepting model terms of use at huggingface.co
   - Needs HUGGING_FACE_TOKEN in .env

2. **HTML-to-PDF Conversion**: Uses an external service for portfolio analysis
   - Converts Google Sites pages to PDF for analysis
   - Needs PDF_HOST in .env (defaults to https://html2pdf-u707.onrender.com)

3. **Competency Analysis**: Uses OpenRouter API (requires API key)
   - Analyzes transcripts and portfolio content against competency framework
   - Generates ratings and insights
   - Needs OPENROUTER_API_KEY and related settings in .env

## Features

Analyzes key competencies across three levels:
- Emerging (1-3)
- Developing (4-7)
- Proficient (8-10)

The competency framework is customizable through RTF files, allowing you to define your own competency dimensions and criteria.

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Required environment variables (.env):
   ```
   # For Competency Analysis (OpenRouter)
   OPENROUTER_API_KEY=your_key_here
   OPENROUTER_URL=https://openrouter.ai/api/v1/chat/completions
   OPENROUTER_MODEL=anthropic/claude-3.7-sonnet

   # For Speaker Diarization (Hugging Face)
   HUGGING_FACE_TOKEN=your_token_here
   
   # For Portfolio Analysis (HTML-to-PDF)
   PDF_HOST=https://html2pdf-u707.onrender.com
   ```

4. Required sound files (in root directory):
   - sound.mp3 (completion sound)
   - coin.mp3 (progress indicator)

## Usage

### GUI Version
```bash
python src/compextractor_gui.py
```

The GUI provides a landing page with three options:
- **Audio Reflection** - For analyzing audio recordings
- **Portfolio** - For analyzing portfolios
- **Video Performance of Learning** - Placeholder for future implementation

#### Audio Reflection Interface
- Simplified audio file selection showing file count and names
- Competency file selection (RTF/TXT)
- Optional speaker diarization
- Output format selection:
  - Full Report (HTML with narrative and ratings)
  - Structured JSON (machine-readable format)
  - Both (generates both formats)
- Progress tracking
- Automatic report generation for each audio file

#### Portfolio Interface
- Direct portfolio URL input for single portfolio analysis
- CSV file upload option for batch processing multiple portfolios
- Portfolio section selection:
  - Beginner, Intermediate, Advanced skill levels
  - Business and Resume sections
- Output format selection (same options as Audio Reflection)
- Progress tracking
- Automatic report generation for each portfolio

### Command Line Version
```bash
python src/main.py
```

## Output

The tool generates different outputs depending on the analysis type:

### Audio Analysis Output
1. Transcription files (before and after diarization)
2. HTML report with:
   - Competency ratings (1-10 scale)
   - Evidence for each rating
   - Interactive radar charts for competency visualization
   - Separate sections for each speaker (if diarization enabled)
3. Optional structured JSON output

### Portfolio Analysis Output
1. HTML report with:
   - Competency ratings (1-10 scale)
   - Evidence for each rating
   - Areas for improvement
   - Interactive radar charts for competency visualization
   - Examples from the portfolio
2. Optional structured JSON output

### Directory Structure
- `results/` - Contains all output files
  - `transcript_*_before_diarization_*.txt` - Raw transcripts
  - `transcript_*_after_diarization_*.txt` - Speaker-labeled transcripts
  - `combined_report_*.html` - Audio analysis reports
  - `portfolio_report_*.html` - Portfolio analysis reports
  - `structured_data_*.json` - Audio analysis JSON data
  - `portfolio_data_*.json` - Portfolio analysis JSON data
- `temp/` - Temporary audio chunks (auto-cleaned after processing)

## LLM Provider

CompExtractor currently uses OpenRouter as the LLM provider for competency analysis. The default model is `anthropic/claude-3.7-sonnet`, but this can be changed in your .env file.

### Using Alternative LLM Providers

The code can be modified to use other LLM providers by:

1. Updating the `extract_competency_insights` function in `src/main.py`
2. Modifying the API endpoint, headers, and request format to match your preferred provider
3. Updating the environment variables accordingly

For example, to use Amazon Bedrock directly instead of OpenRouter, you would need to:
- Change the API endpoint to Amazon Bedrock's endpoint
- Update the authentication method to use AWS credentials
- Adjust the request format to match Amazon Bedrock's API requirements
- Configure the appropriate region and service settings

## System Requirements

- Python 3.11+ (tested on 3.11.11)
- FFmpeg (for audio processing)
- Internet connection (for diarization and competency analysis)

## Troubleshooting

### Speaker Diarization Issues
- Ensure you've accepted the model terms at huggingface.co
- Verify your Hugging Face token is correct in the .env file
- Try running `huggingface-cli login` in your terminal

### Transcription Issues
- Check that FFmpeg is installed and accessible in your PATH
- Ensure audio files are in a supported format
- For large files, the system will automatically split them into chunks

### Portfolio Analysis Issues
- Ensure the PDF_HOST environment variable is set correctly
- Verify that the portfolio URL is accessible and publicly viewable
- For CSV batch processing, ensure the CSV file has the correct column headers
- If the HTML-to-PDF service is down, consider setting up a local service

### GUI Issues
- Ensure all required sound files are in the root directory
- Check that the banner.jpeg file exists for the GUI header
- If the GUI appears cut off, try resizing the window

## Author

Created by Gus Halwani ([@fizt656](https://github.com/fizt656))
