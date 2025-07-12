# OpenAI API Test Script

This script tests the connection to the OpenAI API by making a request to the models endpoint.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your OpenAI API key:**

   **Option A: Environment variable**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

   **Option B: .env file**
   ```bash
   cp .env.example .env
   # Edit .env and replace 'your-api-key-here' with your actual API key
   ```

   **Option C: Pass directly to the function**
   ```python
   from test_openai_api import test_openai_api
   test_openai_api(api_key="your-api-key-here")
   ```

## Usage

Run the script:
```bash
python test_openai_api.py
```

## What it does

- Makes a GET request to `https://api.openai.com/v1/models`
- Shows the response status code
- If successful, displays the number of available models and lists the first 5
- Includes proper error handling for network issues and API errors

## Example Output

```
🔍 Making request to OpenAI API...
📊 Status Code: 200
✅ Success! API connection working.
📋 Available models: 50

📝 First 5 models:
  1. gpt-4o
  2. gpt-4o-mini
  3. gpt-4-turbo
  4. gpt-4
  5. gpt-3.5-turbo
```