from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import drone, login


app = FastAPI()

app.include_router(drone.router)
app.include_router(login.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all domains
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # allow all headers
)


@app.get('/')
def root():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", port=8000, log_level="info", reload=True)
