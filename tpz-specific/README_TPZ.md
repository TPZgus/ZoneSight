# TPZ Competency Analyzer

A TPZ-specific adaptation (see author information below) that combines ZoneSight and Portfolio Analyzer to extract competency insights across 14 key TPZ dimensions, combining local processing with cloud services.

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

ZoneSight analyzes both audio recordings and student portfolios to extract competency insights, providing detailed reports on 14 key competency dimensions. The tool combines local processing with cloud services:

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

Analyzes 14 key competencies (see full definitions and RDs in test_full.rtf in working folder, or consult TPZ documentation):
1. Sense of Belonging - Feeling connected to a learning community
2. Growth Mindset - Belief that abilities can grow with effort
3. STEAM Interest - Exploration of identity through STEAM
4. Creativity - Ability to generate and adapt ideas
5. Communication - Clear exchange of information
6. Teamwork - Cooperative work with diverse peers
7. Adaptability - Adjusting to change and uncertainty
8. Problem-Solving - Identifying and solving challenges
9. STEAM Agency - Capability with STEAM tools
10. Self-Efficacy - Confidence in ability to succeed
11. Persistence - Sustaining effort through challenges
12. Opportunity Recognition - Identifying learning opportunities
13. Continuous Learning - Ongoing skill development
14. Social Capital - Building and leveraging connections

Each competency is evaluated on a 1-10 scale across three levels:
- Emerging (1-3)
- Developing (4-7)
- Proficient (8-10)

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
   - In the Zone.mp3 (background music)
   - banner.jpeg (for GUI header)

## Usage

### GUI Version
```bash
python src/zonesight_gui.py
```

The GUI provides a landing page with three options:
- **Audio Reflection** - For analyzing audio recordings
- **Portfolio** - For analyzing student portfolios
- **Video Performance of Learning** - Placeholder for future implementation

#### Audio Reflection Interface
- Simplified audio file selection showing file count and names
- Competency file selection (RTF/TXT)
- Optional speaker diarization
- Background music toggle (disabled by default)
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
- Background music toggle (disabled by default)
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

ZoneSight currently uses OpenRouter as the LLM provider for competency analysis. The default model is `anthropic/claude-3.7-sonnet`, but this can be changed in your .env file.

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
- Tested on M4 Mac
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

## Authors and Credits

This project combines and adapts two separate tools for TPZ-specific use:

- **Audio Reflection Module and Overall Architecture**: Adapted from CompExtractor by Gus Halwani ([@fizt656](https://github.com/fizt656/compextractor)
- **Portfolio Analysis Module**: Created by Miles Baird ([@kilometers](https://github.com/kilometers/zs-portfolio))

The original competency extractor project is maintained separately by Gus Halwani and is available under its own licensing terms for deployment across a range of contexts. This TPZ-specific adaptation integrates both tools and adds TPZ competency-based learning frameworks and reporting dimensions.

# Placeholder -- Link to IEEE ---
