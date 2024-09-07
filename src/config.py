import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_URL = os.getenv('OPENROUTER_URL', 'https://openrouter.ai/api/v1/chat/completions')
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet')
DIARIZATION_MODEL = os.getenv('DIARIZATION_MODEL', 'pyannote/speaker-diarization')
SITE_URL = os.getenv('SITE_URL', 'https://your-site-url.com')
SITE_NAME = os.getenv('SITE_NAME', 'Your Site Name')
HUGGING_FACE_TOKEN = os.getenv('HUGGING_FACE_TOKEN')