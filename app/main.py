from fastapi import FastAPI, File, UploadFile

from app.routers import drone
from app.services.classification import ClassificationModel


app = FastAPI()

app.include_router(drone.router)

classificationmodel = ClassificationModel()


@app.get('/')
def root():
    return {"Hello": "World"}

@app.post("/upload/")
async def process_image(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        result = classificationmodel.generate(image_bytes)
        return {"result": result}
    except Exception as e:
        return {"message": e.args}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", port=8000, log_level="info", reload=True)
