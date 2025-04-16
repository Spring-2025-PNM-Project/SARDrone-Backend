from fastapi import FastAPI, File, UploadFile

from app.routers import drone
from app.services.classification import ClassificationModel


app = FastAPI()

app.include_router(drone.router)

classificationmodel = ClassificationModel()


@app.get('/')
def root():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", port=8000, log_level="info", reload=True)
