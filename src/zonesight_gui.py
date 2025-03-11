# Author:
# - Gus Halwani (https://github.com/fizt656) 

# Suppress pygame welcome message
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

# Suppress torchaudio deprecation warning
import warnings
warnings.filterwarnings("ignore", message="torchaudio._backend.set_audio_backend has been deprecated")

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from main import transcribe_and_diarize, read_competency_definitions, extract_competency_insights, generate_combined_report, generate_structured_json
from colorama import Fore, Style
import threading
from pygame import mixer
import webbrowser
from datetime import datetime
from PIL import Image, ImageTk
import json
from playsound import playsound
from portfolio.portfolio import get_portfolio_paths, analyze_portfolio, generate_portfolio_report, generate_structured_json as generate_portfolio_json
from config import OPENROUTER_API_KEY, OPENROUTER_URL, OPENROUTER_MODEL

# Define color scheme based on the new banner
PRIMARY_COLOR = "#2C3E50"  # Dark blue
SECONDARY_COLOR = "#3498DB"  # Light blue
ACCENT_COLOR = "#E74C3C"  # Red accent
BACKGROUND_COLOR = "#ECF0F1"  # Light gray background
TEXT_COLOR = "#2C3E50"  # Dark blue text

class ZoneSightApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ZoneSight - Competency Analysis Tool")
        self.root.geometry("780x850")  # Width matches banner width, height ensures all elements are visible
        
        # Center window on screen
        self.center_window()
        
        # Configure styles
        self.setup_styles()
        
        # Create main container frame
        self.main_container = ttk.Frame(root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Make window appear as the main window
        self.root.after(100, self.make_window_active)
        
        # Initialize frames dictionary
        self.frames = {}
        
        # Create and add frames
        for F in (LandingPage, AudioReflectionPage, PortfolioPage):
            frame = F(self.main_container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights for main container
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.rowconfigure(0, weight=1)
        
        # Show landing page first
        self.show_frame("LandingPage")
    
    def center_window(self):
        """Center the window on the screen"""
        # Update the window to get correct dimensions
        self.root.update_idletasks()
        
        # Get screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Get window width and height
        window_width = 780
        window_height = 850
        
        # Calculate position coordinates
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set the position
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def setup_styles(self):
        style = ttk.Style()
        
        # Configure common styles
        style.configure('TFrame', background=BACKGROUND_COLOR)
        style.configure('TLabel', background=BACKGROUND_COLOR, foreground=SECONDARY_COLOR)
        style.configure('TButton', padding=5, background=PRIMARY_COLOR, foreground='white')
        style.configure('TCheckbutton', padding=5, background=BACKGROUND_COLOR, foreground=SECONDARY_COLOR)
        style.configure('TEntry', fieldbackground='white')
        
        # Create a custom style for the Start button
        style.configure('Start.TButton', 
                       font=('Arial', 11, 'bold'),
                       padding=10,
                       background=ACCENT_COLOR)  # Accent color for start button
        
        # Create a custom style for the landing page buttons
        style.configure('Landing.TButton', 
                       font=('Arial', 12, 'bold'),
                       padding=15,
                       background=SECONDARY_COLOR)  # Secondary color for landing buttons
    
    def make_window_active(self):
        """Make the window active and bring it to the front"""
        # Bring window to front
        self.root.lift()
        # Give window focus
        self.root.focus_force()
        # Make window topmost to ensure it's at the front
        self.root.attributes('-topmost', True)
        # Deiconify in case it was minimized
        self.root.deiconify()
        # Update the window to process the above commands
        self.root.update()
        # After a short delay, set topmost to false so other windows can go in front if needed
        self.root.after(1000, lambda: self.root.attributes('-topmost', False))
        # Force focus again after a short delay
        self.root.after(1100, self.root.focus_force)
    
    def show_frame(self, frame_name):
        """Show the specified frame"""
        frame = self.frames[frame_name]
        frame.tkraise()


class LandingPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent, padding=20)
        self.controller = controller
        
        # Create a centered layout
        self.columnconfigure(0, weight=1)
        
        # Add banner image
        try:
            # Load and resize banner image
            banner_img = Image.open('ZoneSight_banner_tpz.png')
            # Calculate aspect ratio
            aspect_ratio = banner_img.width / banner_img.height
            new_width = 780  # Slightly less than window width
            new_height = int(new_width / aspect_ratio)
            banner_img = banner_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            banner_photo = ImageTk.PhotoImage(banner_img)
            
            # Create and place banner label
            banner_label = tk.Label(self, image=banner_photo)
            banner_label.image = banner_photo  # Keep a reference!
            banner_label.grid(row=0, column=0, pady=(0, 30))
        except Exception as e:
            print(f"Could not load banner image: {e}")
        
        # Welcome message
        welcome_label = ttk.Label(
            self, 
            text="Ah, looks like you're interested in jammin' on some data! What are you analyzing today?",
            font=('Arial', 14),
            foreground=SECONDARY_COLOR,  # Use secondary color for welcome text
            wraplength=780
        )
        welcome_label.grid(row=1, column=0, pady=(0, 40))
        
        # Buttons frame
        buttons_frame = ttk.Frame(self)
        buttons_frame.grid(row=2, column=0, pady=20)
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        buttons_frame.columnconfigure(2, weight=1)
        
        # Portfolio button
        portfolio_btn = ttk.Button(
            buttons_frame, 
            text="Portfolio",
            style='Landing.TButton',
            command=lambda: controller.show_frame("PortfolioPage")
        )
        portfolio_btn.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        
        # Audio Reflection button
        audio_btn = ttk.Button(
            buttons_frame, 
            text="Audio Reflection",
            style='Landing.TButton',
            command=lambda: controller.show_frame("AudioReflectionPage")
        )
        audio_btn.grid(row=0, column=1, padx=20, pady=10, sticky="ew")
        
        # Video Performance button (placeholder)
        video_btn = ttk.Button(
            buttons_frame, 
            text="Video Performance of Learning",
            style='Landing.TButton',
            command=lambda: self.show_not_implemented("Video Performance of Learning")
        )
        video_btn.grid(row=0, column=2, padx=20, pady=10, sticky="ew")
    
    def show_not_implemented(self, feature_name):
        """Show a message for features not yet implemented"""
        messagebox.showinfo(
            "Coming Soon", 
            f"The {feature_name} feature is not yet implemented. Stay tuned for future updates!"
        )


class AudioReflectionPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent, padding=10)
        self.controller = controller
        
        # Create main frame
        main_frame = self
        
        # Add banner image
        try:
            # Load and resize banner image
            banner_img = Image.open('ZoneSight_banner_tpz.png')
            # Calculate aspect ratio
            aspect_ratio = banner_img.width / banner_img.height
            new_width = 780  # Slightly less than window width
            new_height = int(new_width / aspect_ratio)
            banner_img = banner_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            banner_photo = ImageTk.PhotoImage(banner_img)
            
            # Create and place banner label
            banner_label = tk.Label(main_frame, image=banner_photo)
            banner_label.image = banner_photo  # Keep a reference!
            banner_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
            
            # Adjust starting row for other elements
            start_row = 1
        except Exception as e:
            print(f"Could not load banner image: {e}")
            start_row = 0
        
        # Back button to return to landing page
        back_button = ttk.Button(
            main_frame, 
            text="← Back to Home",
            command=lambda: controller.show_frame("LandingPage")
        )
        back_button.grid(row=start_row, column=0, sticky=tk.W, pady=5)
        start_row += 1
        
        # Audio files selection - simplified to a single row
        ttk.Label(main_frame, text="Audio Files:").grid(row=start_row, column=0, sticky=tk.W, pady=5)
        
        # Frame for audio files info and buttons
        audio_files_frame = ttk.Frame(main_frame)
        audio_files_frame.grid(row=start_row, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5)
        
        # Files counter and preview label
        self.files_info_var = tk.StringVar(value="No files selected")
        self.files_info_label = ttk.Label(audio_files_frame, textvariable=self.files_info_var, wraplength=500)
        self.files_info_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Buttons for audio files in a separate frame
        buttons_frame = ttk.Frame(audio_files_frame)
        buttons_frame.grid(row=0, column=1, sticky=tk.E)
        
        ttk.Button(buttons_frame, text="Add Files", command=self.add_audio_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons_frame, text="Clear All", command=self.clear_audio_files).pack(side=tk.LEFT, padx=2)
        
        # Store audio files paths
        self.audio_files = []
        
        # Competency file selection
        ttk.Label(main_frame, text="Competency File:").grid(row=start_row+1, column=0, sticky=tk.W, pady=5)
        self.competency_path = tk.StringVar(value="test_full.rtf")  # Default value
        ttk.Entry(main_frame, textvariable=self.competency_path, width=60).grid(row=start_row+1, column=1, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_competency).grid(row=start_row+1, column=2)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Analysis Options")
        options_frame.grid(row=start_row+2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10, padx=5)
        
        # Diarization checkbox
        self.perform_diarization = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Perform Speaker Diarization", 
                       variable=self.perform_diarization).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        
        # Music toggle
        self.play_music = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Play TPZ Theme Music", 
                       variable=self.play_music).grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Output type dropdown
        ttk.Label(options_frame, text="Output Type:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.output_type = tk.StringVar(value="Full Report")
        output_dropdown = ttk.Combobox(options_frame, textvariable=self.output_type, state="readonly")
        output_dropdown['values'] = ("Full Report", "Structured JSON", "Both")
        output_dropdown.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Start button - moved up and made more prominent
        self.start_button = ttk.Button(main_frame, text="Start Analysis", command=self.start_analysis, style='Start.TButton')
        self.start_button.grid(row=start_row+3, column=0, columnspan=3, pady=15, sticky=tk.EW)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Current Status")
        status_frame.grid(row=start_row+4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10, padx=5)
        
        # Status indicator (colored circle)
        self.status_indicator = tk.Canvas(status_frame, width=15, height=15, highlightthickness=0)
        self.status_indicator.grid(row=0, column=0, padx=(5, 0), pady=5)
        self.status_indicator.create_oval(2, 2, 13, 13, fill="gray", outline="")
        
        # Status message label
        self.status_message = ttk.Label(status_frame, text="Ready", wraplength=850)  # Increased wraplength
        self.status_message.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, length=760, mode='indeterminate')
        self.progress_bar.grid(row=start_row+5, column=0, columnspan=3, pady=10)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)

    def add_audio_files(self):
        filenames = filedialog.askopenfilenames(
            title="Select Audio Files",
            filetypes=(("Audio files", "*.wav *.mp3 *.mp4 *.mov"), ("All files", "*.*"))
        )
        if filenames:
            for filename in filenames:
                if filename not in self.audio_files:
                    self.audio_files.append(filename)
            
            # Update the files info label
            self.update_files_info()
    
    def clear_audio_files(self):
        self.audio_files.clear()
        self.files_info_var.set("No files selected")
    
    def update_files_info(self):
        """Update the files info label with the current file count and preview"""
        if not self.audio_files:
            self.files_info_var.set("No files selected")
            return
        
        count = len(self.audio_files)
        
        # Create a preview of the first few filenames
        if count == 1:
            preview = os.path.basename(self.audio_files[0])
            self.files_info_var.set(f"1 file selected: {preview}")
        else:
            # Show first 2 files and indicate if there are more
            preview = ", ".join(os.path.basename(f) for f in self.audio_files[:2])
            if count > 2:
                preview += f", and {count-2} more"
            self.files_info_var.set(f"{count} files selected: {preview}")

    def browse_competency(self):
        filename = filedialog.askopenfilename(
            title="Select Competency File",
            filetypes=(("RTF files", "*.rtf"), ("Text files", "*.txt"), ("All files", "*.*"))
        )
        if filename:
            self.competency_path.set(filename)

    def log_progress(self, message, color=Fore.GREEN):
        # Add timestamp to message
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        # Always use SECONDARY_COLOR for text
        text_color = SECONDARY_COLOR  # Light blue
        
        # Update status message with new color
        self.status_message.configure(text=formatted_message, foreground=text_color)
        
        # Update status indicator color
        indicator_color = "green"
        if color == Fore.RED:
            indicator_color = "red"
        elif color == Fore.YELLOW:
            indicator_color = "orange"
        elif color == Fore.CYAN or color == Fore.BLUE:
            indicator_color = "blue"
            
        self.status_indicator.itemconfig(1, fill=indicator_color)
        
        # Print to console for debugging
        print(f"{color}{formatted_message}{Style.RESET_ALL}")
        
        # Update UI
        self.controller.root.update_idletasks()

    def start_analysis(self):
        # Validate inputs
        if not self.audio_files:
            messagebox.showerror("Error", "Please add at least one audio file")
            return
        if not self.competency_path.get():
            messagebox.showerror("Error", "Please select a competency file")
            return
        
        # Validate file existence
        for audio_file in self.audio_files:
            if not os.path.exists(audio_file):
                messagebox.showerror("Error", f"Audio file does not exist: {audio_file}")
                return
        
        if not os.path.exists(self.competency_path.get()):
            messagebox.showerror("Error", "Competency file does not exist")
            return
        if not os.path.exists('sound.mp3'):
            messagebox.showerror("Error", "Required sound.mp3 file not found")
            return
        if not os.path.exists('coin.mp3'):
            messagebox.showerror("Error", "Required coin.mp3 file not found")
            return
        
        # Disable start button and show progress
        self.start_button.state(['disabled'])
        self.progress_bar.start()
        
        # Reset status and update UI
        self.log_progress("Starting analysis...", Fore.CYAN)
        
        # Make sure the status is visible
        self.controller.root.update()
        
        # Start analysis in a separate thread
        threading.Thread(target=self.run_analysis, daemon=True).start()

    def run_analysis(self):
        try:
            self.log_progress("Starting batch analysis...")
            self.log_progress("Note: Using local Whisper model for transcription")
            
            # Read competency definitions (only need to do this once)
            self.log_progress("Reading competency definitions...")
            competency_definitions = read_competency_definitions(self.competency_path.get())
            if competency_definitions is None:
                raise Exception("Failed to read competency definitions")
            
            # Track all generated reports
            all_reports = []
            
            # Process each audio file
            total_files = len(self.audio_files)
            for index, audio_file in enumerate(self.audio_files):
                file_name = os.path.basename(audio_file)
                self.log_progress(f"[{index+1}/{total_files}] Processing {file_name}...")
                
                # Process audio
                self.log_progress(f"Transcribing {file_name}...")
                speaker_transcripts = transcribe_and_diarize(
                    audio_file, 
                    self.perform_diarization.get()
                )
                
                if speaker_transcripts is None:
                    self.log_progress(f"Failed to process {file_name}, skipping to next file", Fore.RED)
                    continue

                # Extract insights
                self.log_progress(f"Extracting competency insights for {file_name}...")
                competency_data = {}
                
                if len(speaker_transcripts) == 1 and "Speaker 1" in speaker_transcripts:
                    speaker = "Single Speaker"
                    transcript = speaker_transcripts["Speaker 1"]
                    self.log_progress(f"Analyzing {speaker}...")
                    competency_data[speaker] = extract_competency_insights(transcript, competency_definitions)
                else:
                    for speaker, transcript in speaker_transcripts.items():
                        self.log_progress(f"Analyzing {speaker}...")
                        competency_data[speaker] = extract_competency_insights(transcript, competency_definitions)

                # Create results directory if it doesn't exist
                os.makedirs('results', exist_ok=True)
                base_filename = os.path.splitext(file_name)[0]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_reports = []
                
                # Generate and save outputs based on selected output type
                output_type = self.output_type.get()
                
                # Generate HTML report if needed
                if output_type in ["Full Report", "Both"]:
                    self.log_progress(f"Generating HTML report for {file_name}...")
                    combined_report = generate_combined_report(competency_data, file_name)
                    
                    html_filename = f"results/combined_report_{base_filename}_{timestamp}.html"
                    with open(html_filename, 'w', encoding='utf-8') as report_file:
                        report_file.write(combined_report)
                    
                    file_reports.append(html_filename)
                    self.log_progress(f"HTML report saved to {html_filename}", Fore.GREEN)
                
                # Generate JSON output if needed
                if output_type in ["Structured JSON", "Both"]:
                    self.log_progress(f"Generating JSON output for {file_name}...")
                    json_data = generate_structured_json(competency_data, file_name)
                    
                    json_filename = f"results/structured_data_{base_filename}_{timestamp}.json"
                    with open(json_filename, 'w', encoding='utf-8') as json_file:
                        json_file.write(json_data)
                    
                    file_reports.append(json_filename)  # Always add JSON file to reports list
                    self.log_progress(f"JSON data saved to {json_filename}", Fore.GREEN)
                
                # Add this file's reports to the overall list
                all_reports.extend(file_reports)

            # Play completion sound
            playsound('sound.mp3')
            
            # Handle completion based on output type
            if all_reports:
                output_type = self.output_type.get()
                
                if output_type == "Structured JSON":
                    # For JSON only, don't open browser
                    self.log_progress("Batch analysis complete! JSON files saved to results folder.", Fore.GREEN)
                    messagebox.showinfo("Success", f"Batch analysis complete! {len(all_reports)} JSON files have been saved to the results folder.")
                elif output_type == "Full Report":
                    # For HTML reports, open in browser
                    for report in all_reports:
                        webbrowser.open(f'file://{os.path.abspath(report)}')
                    self.log_progress("Batch analysis complete! HTML reports have been opened in your browser.", Fore.GREEN)
                    messagebox.showinfo("Success", f"Batch analysis complete! {len(all_reports)} HTML reports have been generated and opened in your browser.")
                else:  # Both
                    # Count HTML and JSON files
                    html_files = [f for f in all_reports if f.endswith('.html')]
                    json_files = [f for f in all_reports if f.endswith('.json')]
                    
                    # Open only HTML files in browser
                    for report in html_files:
                        webbrowser.open(f'file://{os.path.abspath(report)}')
                    
                    self.log_progress("Batch analysis complete! HTML reports opened in browser and JSON files saved.", Fore.GREEN)
                    messagebox.showinfo("Success", 
                                       f"Batch analysis complete!\n• {len(html_files)} HTML reports opened in browser\n• {len(json_files)} JSON files saved to results folder")
            else:
                self.log_progress("Batch analysis complete, but no files were generated.", Fore.YELLOW)
                messagebox.showinfo("Warning", "Batch analysis complete, but no files were generated.")

        except Exception as e:
            self.log_progress(f"Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            # Re-enable start button and stop progress bar
            self.controller.root.after(0, self.cleanup)

    def cleanup(self):
        self.start_button.state(['!disabled'])
        self.progress_bar.stop()


class PortfolioPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent, padding=10)
        self.controller = controller
        
        # Create main frame
        main_frame = self
        
        # Add banner image
        try:
            # Load and resize banner image
            banner_img = Image.open('ZoneSight_banner_tpz.png')
            # Calculate aspect ratio
            aspect_ratio = banner_img.width / banner_img.height
            new_width = 780  # Slightly less than window width
            new_height = int(new_width / aspect_ratio)
            banner_img = banner_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            banner_photo = ImageTk.PhotoImage(banner_img)
            
            # Create and place banner label
            banner_label = tk.Label(main_frame, image=banner_photo)
            banner_label.image = banner_photo  # Keep a reference!
            banner_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
            
            # Adjust starting row for other elements
            start_row = 1
        except Exception as e:
            print(f"Could not load banner image: {e}")
            start_row = 0
        
        # Back button to return to landing page
        back_button = ttk.Button(
            main_frame, 
            text="← Back to Home",
            command=lambda: controller.show_frame("LandingPage")
        )
        back_button.grid(row=start_row, column=0, sticky=tk.W, pady=5)
        start_row += 1
        
        # Portfolio URL input
        ttk.Label(main_frame, text="Portfolio URL:").grid(row=start_row, column=0, sticky=tk.W, pady=5)
        self.portfolio_url = tk.StringVar(value="https://sites.google.com/possiblezone.org/")
        ttk.Entry(main_frame, textvariable=self.portfolio_url, width=60).grid(row=start_row, column=1, columnspan=2, padx=5, sticky=tk.W)
        
        # CSV file selection
        ttk.Label(main_frame, text="Or Upload CSV:").grid(row=start_row+1, column=0, sticky=tk.W, pady=5)
        
        # Frame for CSV file info and buttons
        csv_frame = ttk.Frame(main_frame)
        csv_frame.grid(row=start_row+1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5)
        
        # CSV file info label
        self.csv_info_var = tk.StringVar(value="No file selected")
        self.csv_info_label = ttk.Label(csv_frame, textvariable=self.csv_info_var, wraplength=500)
        self.csv_info_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        # CSV file button
        ttk.Button(csv_frame, text="Browse", command=self.browse_csv).grid(row=0, column=1, sticky=tk.E, padx=5)
        
        # Competency file selection
        ttk.Label(main_frame, text="Competency File:").grid(row=start_row+2, column=0, sticky=tk.W, pady=5)
        self.competency_path = tk.StringVar(value="test_full.rtf")  # Default value
        ttk.Entry(main_frame, textvariable=self.competency_path, width=60).grid(row=start_row+2, column=1, padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_competency).grid(row=start_row+2, column=2)
        
        # Portfolio sections frame
        sections_frame = ttk.LabelFrame(main_frame, text="Portfolio Sections")
        sections_frame.grid(row=start_row+3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10, padx=5)
        
        # Create a grid for checkboxes
        sections_frame.columnconfigure(0, weight=1)
        sections_frame.columnconfigure(1, weight=1)
        sections_frame.columnconfigure(2, weight=1)
        
        # Portfolio section checkboxes
        self.include_beginner = tk.BooleanVar(value=False)
        ttk.Checkbutton(sections_frame, text="Beginner", 
                       variable=self.include_beginner).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        
        self.include_intermediate = tk.BooleanVar(value=False)
        ttk.Checkbutton(sections_frame, text="Intermediate", 
                       variable=self.include_intermediate).grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        self.include_advanced = tk.BooleanVar(value=False)
        ttk.Checkbutton(sections_frame, text="Advanced", 
                       variable=self.include_advanced).grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
        
        self.include_business = tk.BooleanVar(value=False)
        ttk.Checkbutton(sections_frame, text="Business", 
                       variable=self.include_business).grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        
        self.include_resume = tk.BooleanVar(value=False)
        ttk.Checkbutton(sections_frame, text="Resume", 
                       variable=self.include_resume).grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Analysis Options")
        options_frame.grid(row=start_row+4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10, padx=5)
        
        # Music toggle
        self.play_music = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Play TPZ Theme Music", 
                       variable=self.play_music).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        
        # Output type dropdown
        ttk.Label(options_frame, text="Output Type:").grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        self.output_type = tk.StringVar(value="Full Report")
        output_dropdown = ttk.Combobox(options_frame, textvariable=self.output_type, state="readonly")
        output_dropdown['values'] = ("Full Report", "Structured JSON", "Both")
        output_dropdown.grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
        
        # Start button
        self.start_button = ttk.Button(main_frame, text="Start Analysis", command=self.start_analysis, style='Start.TButton')
        self.start_button.grid(row=start_row+5, column=0, columnspan=3, pady=15, sticky=tk.EW)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Current Status")
        status_frame.grid(row=start_row+6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10, padx=5)
        
        # Status indicator (colored circle)
        self.status_indicator = tk.Canvas(status_frame, width=15, height=15, highlightthickness=0)
        self.status_indicator.grid(row=0, column=0, padx=(5, 0), pady=5)
        self.status_indicator.create_oval(2, 2, 13, 13, fill="gray", outline="")
        
        # Status message label
        self.status_message = ttk.Label(status_frame, text="Ready", wraplength=850)
        self.status_message.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, length=760, mode='indeterminate')
        self.progress_bar.grid(row=start_row+7, column=0, columnspan=3, pady=10)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Store CSV file path
        self.csv_file = None
        
    def browse_csv(self):
        filename = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if filename:
            self.csv_file = filename
            self.csv_info_var.set(os.path.basename(filename))
    
    def browse_competency(self):
        filename = filedialog.askopenfilename(
            title="Select Competency File",
            filetypes=(("RTF files", "*.rtf"), ("Text files", "*.txt"), ("All files", "*.*"))
        )
        if filename:
            self.competency_path.set(filename)
    
    def log_progress(self, message, color=Fore.GREEN):
        # Add timestamp to message
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        # Always use SECONDARY_COLOR for text
        text_color = SECONDARY_COLOR  # Light blue
        
        # Update status message with new color
        self.status_message.configure(text=formatted_message, foreground=text_color)
        
        # Update status indicator color
        indicator_color = "green"
        if color == Fore.RED:
            indicator_color = "red"
        elif color == Fore.YELLOW:
            indicator_color = "orange"
        elif color == Fore.CYAN or color == Fore.BLUE:
            indicator_color = "blue"
            
        self.status_indicator.itemconfig(1, fill=indicator_color)
        
        # Print to console for debugging
        print(f"{color}{formatted_message}{Style.RESET_ALL}")
        
        # Update UI
        self.controller.root.update_idletasks()
    
    def start_analysis(self):
        # Validate inputs
        if not self.portfolio_url.get() and not self.csv_file:
            messagebox.showerror("Error", "Please enter a portfolio URL or select a CSV file")
            return
        
        if not self.competency_path.get():
            messagebox.showerror("Error", "Please select a competency file")
            return
        
        if not os.path.exists(self.competency_path.get()):
            messagebox.showerror("Error", "Competency file does not exist")
            return
        
        if not os.path.exists('sound.mp3'):
            messagebox.showerror("Error", "Required sound.mp3 file not found")
            return
        if not os.path.exists('coin.mp3'):
            messagebox.showerror("Error", "Required coin.mp3 file not found")
            return
        
        # Disable start button and show progress
        self.start_button.state(['disabled'])
        self.progress_bar.start()
        
        # Reset status and update UI
        self.log_progress("Starting portfolio analysis...", Fore.CYAN)
        
        # Make sure the status is visible
        self.controller.root.update()
        
        # Start analysis in a separate thread
        threading.Thread(target=self.run_analysis, daemon=True).start()
    
    def run_analysis(self):
        try:
            self.log_progress("Starting portfolio analysis...")
            
            # Read competency definitions
            self.log_progress("Reading competency definitions...")
            competency_definitions = read_competency_definitions(self.competency_path.get())
            if competency_definitions is None:
                raise Exception("Failed to read competency definitions")
            
            # Track all generated reports
            all_reports = []
            
            # Prepare student data
            if self.csv_file:
                # Process CSV file
                self.log_progress("Reading CSV file...")
                import pandas as pd
                students = pd.read_csv(self.csv_file)
                
                # Process each student in the CSV
                for index, row in students.iterrows():
                    self.log_progress(f"Processing student {row.get('person_id', index)}...")
                    
                    # Get portfolio URL
                    source_url = row.get('source')
                    if not source_url:
                        self.log_progress(f"No source URL for student {row.get('person_id', index)}, skipping", Fore.YELLOW)
                        continue
                    
                    # Get portfolio paths
                    student_data = {
                        'beginner': self.include_beginner.get() and row.get('beginner', True),
                        'intermediate': self.include_intermediate.get() and row.get('intermediate', True),
                        'advanced': self.include_advanced.get() and row.get('advanced', True),
                        'business': self.include_business.get() and row.get('business', True),
                        'resume': self.include_resume.get() and row.get('resume', True)
                    }
                    
                    paths = get_portfolio_paths(student_data)
                    
                    # Analyze portfolio
                    self.log_progress(f"Analyzing portfolio: {source_url}")
                    analysis_data = analyze_portfolio(
                        source_url, 
                        paths, 
                        competency_definitions,
                        OPENROUTER_API_KEY,
                        OPENROUTER_URL,
                        OPENROUTER_MODEL
                    )
                    
                    if analysis_data is None:
                        self.log_progress(f"Failed to analyze portfolio: {source_url}", Fore.RED)
                        continue
                    
                    # Generate reports
                    self.process_analysis_results(analysis_data, source_url, all_reports)
            else:
                # Process single URL
                source_url = self.portfolio_url.get()
                self.log_progress(f"Processing portfolio: {source_url}")
                
                # Get portfolio paths
                student_data = {
                    'beginner': self.include_beginner.get(),
                    'intermediate': self.include_intermediate.get(),
                    'advanced': self.include_advanced.get(),
                    'business': self.include_business.get(),
                    'resume': self.include_resume.get()
                }
                
                paths = get_portfolio_paths(student_data)
                
                # Analyze portfolio
                self.log_progress(f"Analyzing portfolio: {source_url}")
                analysis_data = analyze_portfolio(
                    source_url, 
                    paths, 
                    competency_definitions,
                    OPENROUTER_API_KEY,
                    OPENROUTER_URL,
                    OPENROUTER_MODEL
                )
                
                if analysis_data is None:
                    raise Exception(f"Failed to analyze portfolio: {source_url}")
                
                # Generate reports
                self.process_analysis_results(analysis_data, source_url, all_reports)
            
            # Handle completion
            if all_reports:
                output_type = self.output_type.get()
                
                if output_type == "Structured JSON":
                    # For JSON only, don't open browser
                    self.log_progress("Portfolio analysis complete! JSON files saved to results folder.", Fore.GREEN)
                    messagebox.showinfo("Success", f"Portfolio analysis complete! {len(all_reports)} JSON files have been saved to the results folder.")
                elif output_type == "Full Report":
                    # For HTML reports, open in browser
                    for report in all_reports:
                        webbrowser.open(f'file://{os.path.abspath(report)}')
                    self.log_progress("Portfolio analysis complete! HTML reports have been opened in your browser.", Fore.GREEN)
                    messagebox.showinfo("Success", f"Portfolio analysis complete! {len(all_reports)} HTML reports have been generated and opened in your browser.")
                else:  # Both
                    # Count HTML and JSON files
                    html_files = [f for f in all_reports if f.endswith('.html')]
                    json_files = [f for f in all_reports if f.endswith('.json')]
                    
                    # Open only HTML files in browser
                    for report in html_files:
                        webbrowser.open(f'file://{os.path.abspath(report)}')
                    
                    self.log_progress("Portfolio analysis complete! HTML reports opened in browser and JSON files saved.", Fore.GREEN)
                    messagebox.showinfo("Success", 
                                       f"Portfolio analysis complete!\n• {len(html_files)} HTML reports opened in browser\n• {len(json_files)} JSON files saved to results folder")
            else:
                self.log_progress("Portfolio analysis complete, but no files were generated.", Fore.YELLOW)
                messagebox.showinfo("Warning", "Portfolio analysis complete, but no files were generated.")
                
        except Exception as e:
            error_msg = str(e)
            self.log_progress(f"Error: {error_msg}", Fore.RED)
            
            # Handle font-family error specially - don't show error dialog for this specific error
            # since the files are still being generated successfully
            if "font-family" in error_msg:
                self.log_progress("HTML report may have styling issues but was generated successfully.", Fore.YELLOW)
            else:
                # Use after method to schedule messagebox from main thread to avoid Tkinter threading issues
                self.controller.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {error_msg}"))
        finally:
            # Re-enable start button and stop progress bar
            self.controller.root.after(0, self.cleanup)
    
    def process_analysis_results(self, analysis_data, source_url, all_reports):
        """Process analysis results and generate reports"""
        # Create results directory if it doesn't exist
        os.makedirs('results', exist_ok=True)
        
        # Generate a base filename from the URL
        import re
        base_filename = re.sub(r'[^\w]', '_', source_url.split('/')[-1])
        if not base_filename:
            base_filename = "portfolio"
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate and save outputs based on selected output type
        output_type = self.output_type.get()
        
        # Generate HTML report if needed
        if output_type in ["Full Report", "Both"]:
            self.log_progress(f"Generating HTML report for {source_url}...")
            html_report = generate_portfolio_report(analysis_data, source_url)
            
            html_filename = f"results/portfolio_report_{base_filename}_{timestamp}.html"
            with open(html_filename, 'w', encoding='utf-8') as report_file:
                report_file.write(html_report)
            
            all_reports.append(html_filename)
            self.log_progress(f"HTML report saved to {html_filename}", Fore.GREEN)
        
        # Generate JSON output if needed
        if output_type in ["Structured JSON", "Both"]:
            self.log_progress(f"Generating JSON output for {source_url}...")
            json_data = generate_portfolio_json(analysis_data)
            
            json_filename = f"results/portfolio_data_{base_filename}_{timestamp}.json"
            with open(json_filename, 'w', encoding='utf-8') as json_file:
                json_file.write(json_data)
            
            all_reports.append(json_filename)  # Always add JSON file to reports list
            self.log_progress(f"JSON data saved to {json_filename}", Fore.GREEN)
    
    def cleanup(self):
        self.start_button.state(['!disabled'])
        self.progress_bar.stop()


def main():
    # Print TPZ Data Jam startup message
    print(f"{Fore.CYAN}╔═══════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}🎵 TPZ Data Jam Session Starting... 🎵{Style.RESET_ALL}{' ' * 21}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.MAGENTA}Mixing insights from your audio reflections and portfolios{Style.RESET_ALL} {Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}ZoneSight UI window should now be open on your computer{Style.RESET_ALL}{' ' * 8}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    
    root = tk.Tk()  # Use standard Tk instead of ThemedTk
    app = ZoneSightApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
