# Author: Gus Halwani (https://github.com/fizt656)

import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter configuration for competency analysis
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_URL = os.getenv('OPENROUTER_URL', 'https://openrouter.ai/api/v1/chat/completions')
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3.7-sonnet')
SITE_URL = os.getenv('SITE_URL', 'https://your-site-url.com')
SITE_NAME = os.getenv('SITE_NAME', 'Your Site Name')

# Diarization configuration
DIARIZATION_MODEL = os.getenv('DIARIZATION_MODEL', 'pyannote/speaker-diarization')
HUGGING_FACE_TOKEN = os.getenv('HUGGING_FACE_TOKEN')
