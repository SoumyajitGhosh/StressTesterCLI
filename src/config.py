import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    @property
    def openai_api_key(self) -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
        return api_key

settings = Settings()

# For backward compatibility, keep get_api_key
def get_api_key() -> str:
    return settings.openai_api_key