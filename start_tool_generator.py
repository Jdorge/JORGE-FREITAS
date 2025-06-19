import uvicorn

if __name__ == "__main__":
    uvicorn.run("src.microservices.interactive_tool_generator:app", host="0.0.0.0", port=8001)
