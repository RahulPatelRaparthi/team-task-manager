
from fastapi import FastAPI

app = FastAPI()

@app.get("/")

def home():
    return {"message": "API running"}

import os

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
