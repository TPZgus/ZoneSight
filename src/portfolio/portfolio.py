# Author: Miles Baird (https://github.com/kilometers)
# Portfolio analysis module

import requests
import os
import base64
import json
import time
from datetime import datetime
from portfolio.config import PDF_HOST, raw_portfolio_paths
from src.gemma_local import analyze_text_with_gemma

def generate_content_from_url_and_paths(url, paths):
    """Generate PDF content from a URL and a list of paths"""
    content = []
    for path in paths:
        content.append(generate_content_item(url + path))
    return content

def generate_content_item(url):
    """Generate PDF content from a URL"""
    try:
        pdf = requests.post(PDF_HOST + "/generate-pdf", json={"url": url}).content
        pdf_data = base64.standard_b64encode(pdf).decode("utf-8")
        return {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": pdf_data
            }
        }
    except Exception as e:
        print(f"Error generating PDF from {url}: {e}")
        return {
            "type": "text",
            "text": f"Error generating PDF from {url}: {e}"
        }

def get_portfolio_paths(student):
    """Get portfolio paths based on student flags"""
    remove = []
    if not student.get("beginner", True):
        remove += ["beginner"]
    if not student.get("intermediate", True):
        remove += ["intermediate"]
    if not student.get("advanced", True):
        remove += ["advanced"]
    if not student.get("business", True):
        remove += ["business"]
    if not student.get("resume", True):
        remove += ["resume"]

    return list(filter(lambda x: not any(s in x for s in remove), raw_portfolio_paths))

def analyze_portfolio(source_url, paths, competency_definitions, openrouter_api_key, openrouter_url, openrouter_model):
    """Analyze a portfolio and return the results"""
    from portfolio.prompt import generate_prompt
    
    try:
        print(f"Analyzing portfolio: {source_url}")
        
        print("Portfolio paths to analyze:")
        for i, path in enumerate(paths):
            print(f"  [{i+1}/{len(paths)}] {path}")
            
        print("Generating PDF content from portfolio pages...")
        pdf_start_time = time.time()
        student_content = []
        
        # Process each path with more detailed feedback
        for i, path in enumerate(paths):
            print(f"  Converting page {i+1}/{len(paths)}: {source_url + path}")
            try:
                content_item = generate_content_item(source_url + path)
                student_content.append(content_item)
                print(f"    ✓ Successfully converted page {i+1}")
            except Exception as e:
                print(f"    ✗ Failed to convert page {i+1}: {str(e)}")
        
        pdf_duration = time.time() - pdf_start_time
        print(f"PDF generation completed in {pdf_duration:.2f} seconds")
        
        # Prepare the message for the LLM
        print("Preparing competency analysis prompt...")
        system_prompt = generate_prompt()
        
        # Create a text-based representation of the student's portfolio
        # This is a simplified approach for the local model
        text_content = f"Analyze the following portfolio content from {source_url}:\n\n"
        for i, path in enumerate(paths):
            text_content += f"--- Page {i+1}: {path} ---\n"
            # In a real scenario, you'd extract text from the PDFs.
            # For now, we'll just use the path as a placeholder.
            text_content += f"Content of {path}\n\n"

        prompt = system_prompt + "\n\n" + text_content

        print("Querying local Gemma model...")
        api_start_time = time.time()
        
        analysis_text = analyze_text_with_gemma(prompt)
        
        if not analysis_text:
            raise Exception("Failed to get a response from the local Gemma model.")

        api_duration = time.time() - api_start_time
        print(f"Local model query completed in {api_duration:.2f} seconds")
            
        print("Response received, parsing competency analysis...")
        # The local model might return a string that needs to be parsed into JSON
        try:
            analysis = json.loads(analysis_text)
        except json.JSONDecodeError:
            # If the model doesn't return valid JSON, you might need to add parsing logic here
            # For now, we'll assume it returns a JSON string.
            print("Warning: The model did not return valid JSON. Attempting to proceed.")
            # Create a fallback structure
            analysis = {
                "overall_feedback": analysis_text,
                "competencies": {}
            }

        # Add metadata
        metadata = {
            "source": source_url,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"Analysis complete for {source_url}")
        return metadata | analysis
        
    except Exception as e:
        print(f"Error analyzing portfolio: {e}")
        return None

def generate_portfolio_report(analysis_data, source_url):
    """Generate an HTML report from portfolio analysis data"""
    try:
        print(f"Generating portfolio report for {source_url}...")
        report_start_time = time.time()
        
        html_template = """<!DOCTYPE html>
<html>
<head>
    <title>Portfolio Analysis Report</title>
    <style>
body {font-family: Arial, sans-serif; margin: 20px;}
h1, h2, h3 {color: #333;}
.competency {margin-bottom: 30px; border: 1px solid #ddd; padding: 15px; border-radius: 5px;}
.rating {font-weight: bold;}
.evidence {margin-top: 10px;}
.improvement {margin-top: 10px; color: #555;}
.examples {margin-top: 10px; font-style: italic; color: #777;}
.radar-chart {margin: 20px 0;}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>Portfolio Analysis Report</h1>
    <p><strong>Source:</strong> {source_url}</p>
    <p><strong>Analysis Date:</strong> {timestamp}</p>
    
    <h2>Overall Feedback</h2>
    <p>{overall_feedback}</p>
    
    <div class="radar-chart">
        <canvas id="competencyRadar" width="400" height="300"></canvas>
    </div>
    
    <h2>Competency Analysis</h2>
    {competency_sections}
    
    <script>
        // Radar chart data
        const ctx = document.getElementById('competencyRadar').getContext('2d');
        new Chart(ctx, {{
            type: 'radar',
            data: {{
                labels: {labels},
                datasets: [{{
                    label: 'Competency Ratings',
                    data: {values},
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                scales: {{
                    r: {{
                        angleLines: {{
                            display: true
                        }},
                        suggestedMin: 0,
                        suggestedMax: 10
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""
        
        # Extract competency data
        competencies = analysis_data.get("competencies", {})
        if not competencies:
            competencies = {}
        
        # Generate competency sections
        competency_sections = ""
        labels = []
        values = []
        
        for comp_name, comp_data in competencies.items():
            try:
                # Ensure comp_name is a string
                comp_name_str = str(comp_name).capitalize()
                labels.append(comp_name_str)
                
                # Ensure value is a number
                try:
                    value = float(comp_data.get("value", 0))
                except (ValueError, TypeError):
                    value = 0
                values.append(value)
                
                # Safely get text fields
                evidence = str(comp_data.get("evidence", "")).replace("'", "&#39;").replace('"', "&quot;")
                improvement = str(comp_data.get("areas_for_improvement", "")).replace("'", "&#39;").replace('"', "&quot;")
                examples = str(comp_data.get("examples", "")).replace("'", "&#39;").replace('"', "&quot;")
                
                competency_sections += f"""
        <div class="competency">
            <h3>{comp_name_str}</h3>
            <p class="rating">Rating: {value}/10</p>
            <p class="evidence"><strong>Evidence:</strong> {evidence}</p>
            <p class="improvement"><strong>Areas for Improvement:</strong> {improvement}</p>
            <p class="examples"><strong>Examples:</strong> {examples}</p>
        </div>"""
            except Exception as e:
                print(f"Error processing competency {comp_name}: {e}")
                continue
        
        # Ensure we have at least one competency
        if not labels:
            labels = ["No competencies found"]
            values = [0]
            competency_sections = "<div class='competency'><h3>No competencies found</h3><p>The analysis did not return any competency data.</p></div>"
        
        # Safely get overall feedback
        overall_feedback = str(analysis_data.get("overall_feedback", "No overall feedback provided.")).replace("'", "&#39;").replace('"', "&quot;")
        
        # Format the HTML report
        html_report = html_template.format(
            source_url=source_url,
            timestamp=analysis_data.get("timestamp", datetime.now().isoformat()),
            overall_feedback=overall_feedback,
            competency_sections=competency_sections,
            labels=json.dumps(labels),
            values=json.dumps(values)
        )
        
        report_duration = time.time() - report_start_time
        print(f"Portfolio report generation completed in {report_duration:.2f} seconds")
        print(f"Report contains {len(competencies)} competency assessments")
        
        return html_report
    except Exception as e:
        print(f"Error generating portfolio report: {e}")
        # Return a simple error report
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Portfolio Analysis Error</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #d9534f; }}
        .error {{ color: #d9534f; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>Error Generating Portfolio Report</h1>
    <p>There was an error generating the portfolio analysis report:</p>
    <p class="error">{str(e)}</p>
    <p>Please try again or contact support if the issue persists.</p>
</body>
</html>"""

def generate_structured_json(analysis_data):
    """Generate structured JSON from portfolio analysis data"""
    print("Generating structured JSON output...")
    json_start_time = time.time()
    
    # Count competencies
    competency_count = len(analysis_data.get("competencies", {}))
    
    # Generate JSON
    json_data = json.dumps(analysis_data, indent=2)
    
    json_duration = time.time() - json_start_time
    print(f"JSON generation completed in {json_duration:.2f} seconds")
    print(f"JSON contains data for {competency_count} competencies")
    
    return json_data
