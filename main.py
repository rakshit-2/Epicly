from fastapi import FastAPI
from settings import settings

app = FastAPI()

@app.get("/")
async def test():
  return {
    "status": "success",
    "message": "Hello World"
  }

if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host=settings.DB_HOST, port=settings.DB_PORT)
