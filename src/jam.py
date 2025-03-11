#!/usr/bin/env python3
# JAM - Command-line interface for ZoneSight
# Author: Gus Halwani (https://github.com/fizt656)

import argparse
import os
import sys
import csv
from colorama import Fore, Style
from main import (
    transcribe_and_diarize,
    read_competency_definitions,
    extract_competency_insights,
    generate_combined_report,
    generate_structured_json,
    display_intro
)
from portfolio.portfolio import (
    get_portfolio_paths,
    analyze_portfolio,
    generate_portfolio_report,
    generate_structured_json as generate_portfolio_json
)
from datetime import datetime
from config import OPENROUTER_API_KEY, OPENROUTER_URL, OPENROUTER_MODEL

def print_data_jam_banner():
    """Print the TPZ Data Jam banner"""
    print(f"{Fore.CYAN}╔═══════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}🎵 TPZ Data Jam Session Starting... 🎵{Style.RESET_ALL}{' ' * 21}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.MAGENTA}Mixing insights from your audio reflections and portfolios{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════════╝{Style.RESET_ALL}")

def log_progress(message, color=Fore.GREEN):
    """Log progress with timestamp and color"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    print(f"{color}{formatted_message}{Style.RESET_ALL}")

def process_audio(args):
    """Process audio files"""
    log_progress("Starting audio analysis...", Fore.CYAN)
    
    # Read competency definitions
    competency_file = args.competency if args.competency else "test_full.rtf"
    log_progress(f"Reading competency definitions from {competency_file}...", Fore.CYAN)
    competency_definitions = read_competency_definitions(competency_file)
    if competency_definitions is None:
        log_progress("Failed to read competency definitions", Fore.RED)
        return False
    
    # Process each audio file
    all_reports = []
    for audio_file in args.input:
        if not os.path.exists(audio_file):
            log_progress(f"Audio file does not exist: {audio_file}", Fore.RED)
            continue
        
        log_progress(f"Processing {audio_file}...", Fore.CYAN)
        
        # Transcribe and diarize
        log_progress(f"Transcribing {audio_file}...", Fore.CYAN)
        speaker_transcripts = transcribe_and_diarize(
            audio_file, 
            args.diarization
        )
        
        if speaker_transcripts is None:
            log_progress(f"Failed to process {audio_file}, skipping to next file", Fore.RED)
            continue
        
        # Extract insights
        log_progress(f"Extracting competency insights for {audio_file}...", Fore.CYAN)
        competency_data = {}
        
        if len(speaker_transcripts) == 1 and "Speaker 1" in speaker_transcripts:
            speaker = "Single Speaker"
            transcript = speaker_transcripts["Speaker 1"]
            log_progress(f"Analyzing {speaker}...", Fore.CYAN)
            competency_data[speaker] = extract_competency_insights(transcript, competency_definitions)
        else:
            for speaker, transcript in speaker_transcripts.items():
                log_progress(f"Analyzing {speaker}...", Fore.CYAN)
                competency_data[speaker] = extract_competency_insights(transcript, competency_definitions)
        
        # Create results directory if it doesn't exist
        os.makedirs('results', exist_ok=True)
        base_filename = os.path.splitext(os.path.basename(audio_file))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_reports = []
        
        # Generate outputs based on selected format
        output_format = args.output.lower()
        
        # Generate HTML report if needed
        if output_format in ["html", "both"]:
            log_progress(f"Generating HTML report for {audio_file}...", Fore.CYAN)
            combined_report = generate_combined_report(competency_data, audio_file)
            
            html_filename = f"results/combined_report_{base_filename}_{timestamp}.html"
            with open(html_filename, 'w', encoding='utf-8') as report_file:
                report_file.write(combined_report)
            
            file_reports.append(html_filename)
            log_progress(f"HTML report saved to {html_filename}", Fore.GREEN)
        
        # Generate JSON output if needed
        if output_format in ["json", "both"]:
            log_progress(f"Generating JSON output for {audio_file}...", Fore.CYAN)
            json_data = generate_structured_json(competency_data, audio_file)
            
            json_filename = f"results/structured_data_{base_filename}_{timestamp}.json"
            with open(json_filename, 'w', encoding='utf-8') as json_file:
                json_file.write(json_data)
            
            file_reports.append(json_filename)
            log_progress(f"JSON data saved to {json_filename}", Fore.GREEN)
        
        # Add this file's reports to the overall list
        all_reports.extend(file_reports)
    
    # Summary
    if all_reports:
        log_progress(f"Audio analysis complete! Generated {len(all_reports)} files:", Fore.GREEN)
        for report in all_reports:
            print(f"  - {report}")
        return True
    else:
        log_progress("Audio analysis complete, but no files were generated.", Fore.YELLOW)
        return False

def process_portfolio(args):
    """Process portfolio URLs"""
    log_progress("Starting portfolio analysis...", Fore.CYAN)
    
    # Read competency definitions
    competency_file = args.competency if args.competency else "test_full.rtf"
    log_progress(f"Reading competency definitions from {competency_file}...", Fore.CYAN)
    competency_definitions = read_competency_definitions(competency_file)
    if competency_definitions is None:
        log_progress("Failed to read competency definitions", Fore.RED)
        return False
    
    # Process each portfolio URL
    all_reports = []
    for portfolio_url in args.input:
        log_progress(f"Processing portfolio: {portfolio_url}", Fore.CYAN)
        
        # Get portfolio paths (all sections for now)
        student_data = {
            'beginner': True,
            'intermediate': True,
            'advanced': True,
            'business': True,
            'resume': True
        }
        
        paths = get_portfolio_paths(student_data)
        
        # Analyze portfolio
        log_progress(f"Analyzing portfolio: {portfolio_url}", Fore.CYAN)
        analysis_data = analyze_portfolio(
            portfolio_url, 
            paths, 
            competency_definitions,
            OPENROUTER_API_KEY,
            OPENROUTER_URL,
            OPENROUTER_MODEL
        )
        
        if analysis_data is None:
            log_progress(f"Failed to analyze portfolio: {portfolio_url}", Fore.RED)
            continue
        
        # Create results directory if it doesn't exist
        os.makedirs('results', exist_ok=True)
        
        # Generate a base filename from the URL
        import re
        base_filename = re.sub(r'[^\w]', '_', portfolio_url.split('/')[-1])
        if not base_filename:
            base_filename = "portfolio"
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_reports = []
        
        # Generate outputs based on selected format
        output_format = args.output.lower()
        
        # Generate HTML report if needed
        if output_format in ["html", "both"]:
            log_progress(f"Generating HTML report for {portfolio_url}...", Fore.CYAN)
            html_report = generate_portfolio_report(analysis_data, portfolio_url)
            
            html_filename = f"results/portfolio_report_{base_filename}_{timestamp}.html"
            with open(html_filename, 'w', encoding='utf-8') as report_file:
                report_file.write(html_report)
            
            file_reports.append(html_filename)
            log_progress(f"HTML report saved to {html_filename}", Fore.GREEN)
        
        # Generate JSON output if needed
        if output_format in ["json", "both"]:
            log_progress(f"Generating JSON output for {portfolio_url}...", Fore.CYAN)
            json_data = generate_portfolio_json(analysis_data)
            
            json_filename = f"results/portfolio_data_{base_filename}_{timestamp}.json"
            with open(json_filename, 'w', encoding='utf-8') as json_file:
                json_file.write(json_data)
            
            file_reports.append(json_filename)
            log_progress(f"JSON data saved to {json_filename}", Fore.GREEN)
        
        # Add this file's reports to the overall list
        all_reports.extend(file_reports)
    
    # Summary
    if all_reports:
        log_progress(f"Portfolio analysis complete! Generated {len(all_reports)} files:", Fore.GREEN)
        for report in all_reports:
            print(f"  - {report}")
        return True
    else:
        log_progress("Portfolio analysis complete, but no files were generated.", Fore.YELLOW)
        return False

def process_video(args):
    """Process video files (placeholder for future implementation)"""
    log_progress("Video analysis is not yet implemented.", Fore.YELLOW)
    log_progress("This feature will be available in a future update.", Fore.YELLOW)
    return False

def process_csv_input(csv_file):
    """Process a CSV file containing input files or URLs"""
    inputs = []
    try:
        with open(csv_file, 'r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if row and row[0].strip():  # Skip empty rows
                    inputs.append(row[0].strip())
        return inputs
    except Exception as e:
        log_progress(f"Error reading CSV file: {e}", Fore.RED)
        return []

def main():
    """Main function to parse arguments and run the appropriate analysis"""
    parser = argparse.ArgumentParser(
        description="JAM - Command-line interface for ZoneSight",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze audio with diarization, output both formats
  python jam.py --type a --output both --diarization audio_file.mp3
  
  # Analyze multiple audio files
  python jam.py --type a audio1.mp3 audio2.mp3 audio3.mp3
  
  # Analyze portfolio with custom competency file
  python jam.py --type p --competency custom_competencies.rtf https://portfolio-url.com
  
  # Analyze inputs from a CSV file
  python jam.py --type a --csv inputs.csv
"""
    )
    
    # Required arguments
    parser.add_argument(
        "--type", "-t", 
        required=True,
        choices=["p", "portfolio", "a", "audio", "v", "video"],
        help="Type of analysis to perform: (p)ortfolio, (a)udio, or (v)ideo"
    )
    
    # Optional arguments
    parser.add_argument(
        "--output", "-o",
        default="both",
        choices=["json", "html", "both"],
        help="Output format: json, html, or both (default: both)"
    )
    
    parser.add_argument(
        "--competency", "-c",
        help="Path to competency file (default: test_full.rtf)"
    )
    
    parser.add_argument(
        "--diarization", "-d",
        action="store_true",
        help="Enable speaker diarization for audio analysis"
    )
    
    parser.add_argument(
        "--csv",
        help="CSV file containing input files or URLs (one per line)"
    )
    
    # Input files or URLs
    parser.add_argument(
        "input",
        nargs="*",
        help="Input files or URLs to analyze"
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_data_jam_banner()
    
    # Process CSV input if provided
    if args.csv:
        if os.path.exists(args.csv):
            csv_inputs = process_csv_input(args.csv)
            if csv_inputs:
                args.input.extend(csv_inputs)
            else:
                log_progress("No valid inputs found in CSV file", Fore.RED)
                return 1
        else:
            log_progress(f"CSV file does not exist: {args.csv}", Fore.RED)
            return 1
    
    # Check if we have input files/URLs
    if not args.input:
        log_progress("No input files or URLs provided", Fore.RED)
        parser.print_help()
        return 1
    
    # Run the appropriate analysis based on type
    analysis_type = args.type.lower()
    
    if analysis_type in ["a", "audio"]:
        success = process_audio(args)
    elif analysis_type in ["p", "portfolio"]:
        success = process_portfolio(args)
    elif analysis_type in ["v", "video"]:
        success = process_video(args)
    else:
        log_progress(f"Unknown analysis type: {analysis_type}", Fore.RED)
        return 1
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
