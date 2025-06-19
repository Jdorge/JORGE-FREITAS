import uvicorn

if __name__ == "__main__":
    uvicorn.run("src.microservices.data_analyzer:app", host="0.0.0.0", port=8000)
