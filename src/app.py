# src/app.py

import gradio as gr
import os
from main import run_analysis, cleanup_temp_files

def process_files(audio_file, competency_file):
    """
    Gradio interface function to process uploaded files and run analysis.
    """
    if audio_file is None or competency_file is None:
        return "Please upload both an audio file and a competency file.", None

    # The files are uploaded to a temporary directory by Gradio
    audio_path = audio_file.name
    competency_path = competency_file.name

    print(f"Audio file path: {audio_path}")
    print(f"Competency file path: {competency_path}")

    # Run the analysis from main.py
    # For the Gradio app, we'll disable diarization by default for simplicity
    html_report, json_data = run_analysis(audio_path, competency_path, perform_diarization=False)

    # Clean up temporary files created during the process
    cleanup_temp_files()

    if html_report is None:
        return "<p>Error during analysis. Please check the console for details.</p>", None

    # Gradio can render HTML directly in an iFrame
    report_iframe = f'<iframe srcdoc="{html_report.replace("\"", "&")}" frameborder="0" width="100%" height="600px"></iframe>'

    return report_iframe, json_data


def main():
    """
    Defines and launches the Gradio interface.
    """
    with gr.Blocks(title="ZoneSight Analysis") as app:
        gr.Markdown("""
        # ZoneSight: Competency Analysis
        Upload an audio file and a competency definition file (TXT or RTF) to begin.
        """)

        with gr.Row():
            audio_input = gr.File(label="Audio File (WAV, MP3, etc.)")
            competency_input = gr.File(label="Competency Definitions (TXT, RTF)")
        
        analyze_button = gr.Button("Analyze", variant="primary")

        with gr.Tabs():
            with gr.TabItem("HTML Report"):
                report_output = gr.HTML(label="Analysis Report")
            with gr.TabItem("JSON Output"):
                json_output = gr.JSON(label="Structured Data")

        analyze_button.click(
            fn=process_files,
            inputs=[audio_input, competency_input],
            outputs=[report_output, json_output]
        )

    print("Launching Gradio app...")
    app.launch()

if __name__ == "__main__":
    main()
