# Technical Roadmap: ZoneSight-Gemma Hackathon Project (Agent-Ready)

**Project Goal:** Adapt the existing ZoneSight tool to use a local Gemma 3n model for analysis, and create a simple, voice-enabled Gradio UI for students to interact with it.

**Timeline:** 14 Days

**Guiding Principle:** Each step is designed to be an atomic, verifiable action for an AI coding agent.

---

## Phase 1: Environment Setup & Core Backend Integration (Days 1-3)

**Objective:** Establish a working, local-first version of the ZoneSight analysis engine by replacing its remote API calls with local Gemma 3n calls.

### Step 1.1: Project Setup & Dependency Management
* **Action:** Create a Python virtual environment and install all dependencies.
* **Commands (Execute in terminal):**
    ```bash
    # In your cloned ZoneSight repository
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    pip install ollama gradio SpeechRecognition pyaudio
    ```
* **Note:** If `pyaudio` installation fails, install `portaudio` using your system's package manager (`brew install portaudio` or `sudo apt-get install portaudio19-dev`) and retry `pip install pyaudio`.

### Step 1.2: Install and Verify Local Gemma 3n
* **Action:** Install Ollama and pull the specified Gemma 3n model.
* **Commands (Execute in terminal):**
    ```bash
    # Install Ollama (if not already installed)
    # curl -fsSL [https://ollama.com/install.sh](https://ollama.com/install.sh) | sh
    
    # Pull the model
    ollama pull unsloth/gemma-3n-4b-it-gguf:latest
    ```
* **Action:** Verify the local model is operational.
* **Command (Execute in terminal):**
    ```bash
    ollama run unsloth/gemma-3n-4b-it-gguf:latest
    ```
* **Verification:** At the prompt, type `Why is the sky blue?` and confirm a coherent response is generated. Exit the Ollama chat with `/bye`.

### Step 1.3: Create the Gemma 3n Integration Module
* **Action:** Create a new file `src/gemma_local.py` to encapsulate all interaction with the local Ollama service.
* **File to Create:** `src/gemma_local.py`
* **Code to write to `src/gemma_local.py`:**
    ```python
    import ollama
    import json
    
    # Define the specific model we will use for this project
    MODEL_NAME = "unsloth/gemma-3n-4b-it-gguf:latest"
    
    def get_gemma_response(prompt: str) -> str:
        """
        Sends a standard prompt to the local Gemma 3n model and gets a text response.
        """
        try:
            response = ollama.chat(
                model=MODEL_NAME,
                messages=[{'role': 'user', 'content': prompt}]
            )
            return response['message']['content']
        except Exception as e:
            print(f"Error communicating with Ollama: {e}")
            return "Error: Could not get a response from the local model."
    
    def get_gemma_json_response(prompt: str) -> dict:
        """
        Sends a prompt and requests a JSON response from the local Gemma 3n model.
        This is crucial for structured data extraction.
        """
        try:
            response = ollama.chat(
                model=MODEL_NAME,
                messages=[{'role': 'user', 'content': prompt}],
                format="json"
            )
            # The response content is a JSON string, so we parse it into a Python dict
            return json.loads(response['message']['content'])
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from model response: {e}")
            print(f"Raw response: {response['message']['content']}")
            return {"error": "Failed to decode JSON from model."}
        except Exception as e:
            print(f"Error communicating with Ollama: {e}")
            return {"error": "Could not get a response from the local model."}
    ```

### Step 1.4: **[CRITICAL]** Modify ZoneSight to Use the Local Model
* **Analysis:** The remote LLM call is made in `src/portfolio/portfolio.py` within the `Portfolio` class. It uses the `openrouter.Chat.create` method. We will replace this.
* **Action:** Modify the `src/portfolio/portfolio.py` file.
* **File to Modify:** `src/portfolio/portfolio.py`
* **Modification Details:**
    1.  **Add new import:** At the top of the file, add `from ..gemma_local import get_gemma_json_response`. Note the `..` for relative import from a parent directory.
    2.  **Locate the `_call_openrouter` method:** Find the private method `_call_openrouter` within the `Portfolio` class.
    3.  **Replace the method:** Comment out the entire `_call_openrouter` method and replace it with a new method `_call_gemma_local` that uses our new module.

* **Code diff for `src/portfolio/portfolio.py`:**
    ```python
    # ... other imports at the top of the file
    import openrouter
    from ..gemma_local import get_gemma_json_response # <-- ADD THIS LINE
    
    class Portfolio:
        # ... __init__ and other methods
    
        # vvvv COMMENT OUT OR DELETE THIS ENTIRE METHOD vvvv
        # def _call_openrouter(self, model, messages, temperature, max_tokens, retries=3, delay=5):
        #     for i in range(retries):
        #         try:
        #             response = openrouter.Chat.create(
        #                 model=model,
        #                 messages=messages,
        #                 temperature=temperature,
        #                 max_tokens=max_tokens,
        #             )
        #             return response
        #         except Exception as e:
        #             print(f"Error calling OpenRouter (attempt {i+1}/{retries}): {e}")
        #             if i < retries - 1:
        #                 time.sleep(delay)
        #             else:
        #                 raise
    
        # vvvv ADD THIS NEW METHOD IN ITS PLACE vvvv
        def _call_gemma_local(self, messages):
            """
            Calls the local Gemma model using our gemma_local module.
            The 'messages' are expected to be a list of dicts, e.g., [{'role': 'user', 'content': '...'}].
            We will construct a single string prompt from this for our simple implementation.
            """
            # Extract the content from the last user message to form the prompt.
            # This simplifies the logic for our local model call.
            prompt = messages[-1]['content']
            
            # Use the JSON response function as ZoneSight expects structured data
            return get_gemma_json_response(prompt)

        def _process_chunk(self, chunk):
            # ... existing code ...
            
            # vvvv FIND AND REPLACE THIS LINE vvvv
            # response = self._call_openrouter(...)
            # vvvv WITH THIS LINE vvvv
            response = self._call_gemma_local(messages=messages)

            # The local function already returns a dict, so we might not need .dict()
            # Check the return type. The original code expects a JSON string in response.choices[0].message.content
            # Our new function returns a parsed dictionary directly.
            
            # vvvv FIND AND REPLACE THIS BLOCK vvvv
            # try:
            #     response_dict = json.loads(response.choices[0].message.content)
            #     # ...
            # except (json.JSONDecodeError, KeyError) as e:
            #     # ...
            
            # vvvv WITH THIS SIMPLER BLOCK vvvv
            if "error" in response:
                print(f"Error from local Gemma: {response['error']}")
                return None # Or handle error appropriately
            
            response_dict = response # The response is already a dictionary
            
            # ... rest of the _process_chunk method
    ```
* **Verification:** Run `python src/main.py --help`. It should still work. Then, try running it with a sample file. It will be slow and use your CPU, but it should attempt to process the file using Gemma, not OpenRouter. You will likely see errors, which we will fix in the next phase by adjusting the prompts.

---

## Phase 2: Application Logic & Voice Integration (Days 4-7)

**Objective:** Create the application shell, handle state, and ensure a smooth flow from voice input to ZoneSight analysis.

### Step 2.1: Create the Main Application Scaffolding
* **Action:** Create the main entry point file `app.py` in the project's root directory.
* **File to Create:** `app.py`
* **Code to write to `app.py`:**
    ```python
    import gradio as gr
    import speech_recognition as sr
    # We will refactor main.py to provide this function
    from src.main import run_zonesight_analysis_on_transcript 
    from src.gemma_local import get_gemma_response

    def transcribe_audio(audio_filepath):
        """Transcribes audio file to text using Google's web speech API."""
        if not audio_filepath:
            return "No audio recorded.", ""
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_filepath) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data)
                return text
            except sr.UnknownValueError:
                return "Error: Could not understand audio."
            except sr.RequestError as e:
                return f"Error: Speech recognition service error; {e}"

    def chat_interface_logic(user_input, history):
        """Handles the conversational turn-taking with the local Gemma model."""
        history.append({"role": "user", "content": user_input})
        
        # Construct a simple prompt for conversation
        prompt = "You are a friendly student coach. The user is talking to you about their project. Respond conversationally.\n\n"
        # Create a string representation of the conversation for the prompt
        for message in history:
            if message["role"] == "user":
                prompt += f"Student: {message['content']}\n"
            else:
                prompt += f"Coach: {message['content']}\n"
        prompt += "Coach:"

        gemma_response = get_gemma_response(prompt)
        history.append({"role": "assistant", "content": gemma_response})
        
        # Convert history to Gradio chatbot format
        gradio_history = [(msg['content'] if msg['role'] == 'user' else None, msg['content'] if msg['role'] == 'assistant' else None) for msg in history]

        return gradio_history, ""

    def handle_transcription_and_chat(audio_filepath, history):
        """A single function to chain transcription and chat logic."""
        transcribed_text = transcribe_audio(audio_filepath)
        if "Error:" in transcribed_text:
            # Add error message to chat without calling the model
            history.append({"role": "assistant", "content": transcribed_text})
            gradio_history = [(msg['content'] if msg['role'] == 'user' else None, msg['content'] if msg['role'] == 'assistant' else None) for msg in history]
            return gradio_history, ""
        
        return chat_interface_logic(transcribed_text, history)

    def analyze_conversation_and_get_report(history):
        """Takes the full conversation history and generates the ZoneSight report."""
        full_transcript = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
        
        # This function will be created in the next step
        # It will return a report in Markdown format
        report_md = run_zonesight_analysis_on_transcript(full_transcript)
        return report_md
    
    # Gradio UI will be defined in Phase 3
    ```

### Step 2.2: **[CRITICAL]** Refactor ZoneSight for Programmatic Access
* **Analysis:** `src/main.py` currently uses `argparse` and is designed for command-line execution. We need to wrap its core functionality in a single function that our Gradio app can import and call with a string of text.
* **Action:** Modify `src/main.py`.
* **File to Modify:** `src/main.py`
* **Refactoring Details:**
    1.  Keep all existing imports.
    2.  Create a new function `run_zonesight_analysis_on_transcript(transcript: str) -> str`.
    3.  Move the logic from the existing `main()` function inside this new function.
    4.  Instead of reading a file from a path provided by `argparse`, the new function will take the `transcript` string as its input.
    5.  The function should return the generated report as a Markdown string.

* **Code diff for `src/main.py`:**
    ```python
    # ... existing imports ...
    from portfolio.portfolio import Portfolio
    
    def run_zonesight_analysis_on_transcript(transcript: str) -> str:
        """
        Takes a raw text transcript, runs ZoneSight analysis, and returns a Markdown report.
        This is the new entry point for our Gradio app.
        """
        # Create a temporary file to hold the transcript, as the Portfolio class expects a filepath
        # This is a simple way to adapt the existing code without a major rewrite.
        temp_file_path = "temp_transcript.txt"
        with open(temp_file_path, "w") as f:
            f.write(transcript)

        # Instantiate the portfolio with the path to the temp file
        # We can use default config values for other arguments
        portfolio = Portfolio(
            file_path=temp_file_path,
            output_dir="reports",
            config_path="src/portfolio/config.py", # or appropriate default
            template_path="src/portfolio/data/blank_template.json" # or appropriate default
        )
        
        # Run the portfolio generation
        portfolio.run()

        # The report is saved to a file. We need to read it back and return it.
        # The output filename is based on the input name.
        report_filename = portfolio.output_filename.replace(".json", ".md") # Assuming it creates a markdown report
        report_path = os.path.join("reports", report_filename)

        if os.path.exists(report_path):
            with open(report_path, "r") as f:
                report_content = f.read()
            os.remove(temp_file_path) # Clean up temp file
            return report_content
        else:
            os.remove(temp_file_path) # Clean up temp file
            return "## Error: Report file not generated."

    def main():
        # The original main function for command-line use can be kept for testing
        # Or modified to use the new function
        parser = argparse.ArgumentParser(...)
        # ... existing argparse setup ...
        args = parser.parse_args()
        
        # To maintain CLI functionality, read the file and pass its content
        with open(args.file_path, 'r') as f:
            content = f.read()
        
        report = run_zonesight_analysis_on_transcript(content)
        print("Report generation complete. Check the 'reports' directory.")

    if __name__ == "__main__":
        main()
    ```

---

## Phase 3: Gradio UI Development & State Management (Days 8-10)

**Objective:** Build and wire up a polished Gradio UI, ensuring conversation history is managed correctly.

### Step 3.1: Build the Gradio UI Layout and State
* **Action:** Define the Gradio interface in `app.py` and include `gr.State` to properly manage the conversation history across interactions.
* **File to Modify:** `app.py`
* **Code to add/replace at the end of `app.py`:**
    ```python
    # ... (all your functions from Phase 2 go here) ...

    with gr.Blocks(theme=gr.themes.Soft(), title="ZoneSight Gemma") as demo:
        gr.Markdown("# ZoneSight-Gemma: Student Project Coach")
        gr.Markdown("Talk about your project, and when you're done, click 'Analyze' to get feedback on your competencies.")
        
        # State object to hold the conversation history in a structured way
        conversation_state = gr.State(value=[])

        with gr.Row():
            with gr.Column(scale=2):
                chatbot_ui = gr.Chatbot(label="Conversation", height=500, bubble_full_width=False)
                textbox = gr.Textbox(label="Your Message", placeholder="Type or use the microphone...", scale=4)
            
            with gr.Column(scale=1):
                audio_input = gr.Audio(sources=["microphone"], type="filepath", label="Record Your Voice")
                transcribe_btn = gr.Button("Transcribe and Send")
                gr.Markdown("---")
                analyze_btn = gr.Button("Analyze Full Conversation", variant="primary")

        with gr.Accordion("Analysis Report", open=False) as report_accordion:
            report_output = gr.Markdown("Your report will appear here...")

        # Event Handlers
        
        # Handle direct text submission
        textbox.submit(
            fn=chat_interface_logic,
            inputs=[textbox, conversation_state],
            outputs=[chatbot_ui, textbox, conversation_state]
        )

        # Handle audio submission
        transcribe_btn.click(
            fn=handle_transcription_and_chat,
            inputs=[audio_input, conversation_state],
            outputs=[chatbot_ui, conversation_state]
        )

        # Handle analysis button click
        analyze_btn.click(
            fn=analyze_conversation_and_get_report,
            inputs=[conversation_state],
            outputs=[report_output]
        ).then(lambda: gr.update(open=True), outputs=report_accordion) # Automatically open the accordion

    # Launch the app
    if __name__ == "__main__":
        demo.launch()
    ```

---

## Phase 4: Finalization & Submission Prep (Days 11-14)

**Objective:** Polish, document, and package the project for submission. These are primarily manual tasks for the user.

### Step 4.1: Testing and Refinement
* **Action:** Manually test the entire application flow.
* **Checklist:**
    - \[ \] Does audio recording work reliably?
    - \[ \] Is transcription accurate enough?
    - \[ \] Are Gemma's conversational responses coherent?
    - \[ \] Does the "Analyze" function produce a well-formatted Markdown report?
    - \[ \] Is the UI intuitive and free of bugs?
    - \[ \] Add error handling for when the model or speech recognition fails.

### Step 4.2: Create the Video Demo (3 mins max)
* **Action:** Plan and record the demo video.
* **Video Storyboard:**
    1.  **Problem (15s):** "Assessing student skills like critical thinking is hard. It's usually based on final essays, not the learning process."
    2.  **Solution Intro (30s):** "Introducing ZoneSight-Gemma, a private, on-device AI coach that helps students reflect on their learning process by simply talking about their work."
    3.  **Live Demo (90s):** Show the clean Gradio UI. Record yourself talking to the app. Show the conversation. Click "Analyze." Scroll through the generated report.
    4.  **Technical "Wow" Factor (30s):** "This entire application, from speech-to-text to the advanced Gemma 3n model, is running 100% locally on this laptop. It's completely private and works offline." Show the terminal running Ollama in the background.
    5.  **Vision & Impact (15s):** "This empowers students with personalized feedback and gives educators deeper insight into the learning journey."

### Step 4.3: Write the Technical Writeup & Prepare Code
* **Action:** Write the technical document and clean the repository.
* **Key Writeup Sections:** Architecture Diagram, "Why Gemma 3n?", Challenges Overcome, Technical Choices.
* **Repo Cleanup:** Create a new `README.md` with setup/run instructions. Finalize `requirements.txt`. Remove API keys and temporary files.

### Step 4.4: Submit
* **Action:** Generate a public Gradio link for the live demo.
* **Command (Execute in terminal):**
    ```bash
    python app.py --share
    ```
* **Action:** Assemble all materials (video link, writeup, code repo link, live demo link) and submit on the Kaggle competition page.

