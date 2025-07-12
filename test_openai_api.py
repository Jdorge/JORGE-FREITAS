import requests
import os
from typing import Optional

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def test_openai_api(api_key: Optional[str] = None) -> None:
    """
    Test OpenAI API connection by making a request to the models endpoint.
    
    Args:
        api_key: OpenAI API key. If not provided, will try to get from OPENAI_API_KEY environment variable.
    """
    # Get API key from parameter or environment variable
    if api_key is None:
        api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ Error: OpenAI API key not found!")
        print("Please set your API key in one of these ways:")
        print("1. Set the OPENAI_API_KEY environment variable")
        print("2. Pass the api_key parameter to this function")
        print("3. Create a .env file with OPENAI_API_KEY=your_key_here")
        return
    
    # API endpoint
    url = "https://api.openai.com/v1/models"
    
    # Headers with API key
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        print("🔍 Making request to OpenAI API...")
        response = requests.get(url, headers=headers)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success! API connection working.")
            data = response.json()
            print(f"📋 Available models: {len(data.get('data', []))}")
            
            # Show first few models
            models = data.get('data', [])
            if models:
                print("\n📝 First 5 models:")
                for i, model in enumerate(models[:5]):
                    print(f"  {i+1}. {model.get('id', 'Unknown')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_openai_api()