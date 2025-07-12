# Microservices Project

This project contains two microservices:
- **Data Analyzer** (Port 8000)
- **Interactive Tool Generator** (Port 8001)

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   - Edit the `.env` file
   - Replace placeholder API keys with your actual keys

3. **Run the services:**

   **Data Analyzer:**
   ```bash
   python start_data_analyzer.py
   ```

   **Tool Generator:**
   ```bash
   python start_tool_generator.py
   ```

## API Endpoints

### Data Analyzer (Port 8000)
- `GET /` - Service status
- `GET /health` - Health check
- `POST /analyze` - Analyze data

### Tool Generator (Port 8001)
- `GET /` - Service status
- `GET /health` - Health check
- `POST /generate` - Generate interactive tools

## Example Usage

### Analyze Data
```bash
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"data": "Sample data for analysis", "analysis_type": "text"}'
```

### Generate Tool
```bash
curl -X POST "http://localhost:8001/generate" \
     -H "Content-Type: application/json" \
     -d '{"tool_type": "calculator", "description": "Simple calculator tool"}'
```