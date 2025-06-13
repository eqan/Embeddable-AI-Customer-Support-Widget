from slowapi import Limiter
from slowapi.util import get_remote_address
import google.generativeai as genai
from config.settings import Settings

settings = Settings()

# Create a limiter instance with the default rate
limiter = Limiter(key_func=get_remote_address)

#@title Model Configuration
# Model settings for generating responses
generation_config = {
  "temperature": 1,   # Creativity (0: deterministic, 1: high variety)
  "top_p": 0.95,       # Focus on high-probability words
  "top_k": 64,        # Consider top-k words for each step
  "max_output_tokens": 8192,  # Limit response length
  "response_mime_type": "text/plain",  # Output as plain text
}

safety_settings = [
  # Gemini's safety settings for blocking harmful content
  # (Set to "BLOCK_ALL" for blocking)
  {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ALL"},
  {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ALL"},
  {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ALL"},
  {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ALL"},
]

genai.configure(api_key=settings.model_api_key)
