"""
Gavigans Agent Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Google API Key for Gemini
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Memory summarization settings
MEMORY_SUMMARIZATION_THRESHOLD = 30  # Summarize after this many events
MEMORY_KEEP_RECENT_EVENTS = 10  # Keep this many recent events raw
