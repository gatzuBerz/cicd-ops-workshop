from contextlib import asynccontextmanager

import joblib
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel

from ci_cd.inference import MODEL_PATH

CLASSES = ["setosa", "versicolor", "virginica"]

model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the model once, when the server starts."""
    global model
    model = joblib.load(MODEL_PATH)
    yield


app = FastAPI(title="Iris classifier", lifespan=lifespan)


class Flower(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float


class Prediction(BaseModel):
    prediction: str
    probabilities: dict[str, float]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict")
def predict(flower: Flower) -> Prediction:
    X = np.array(
        [
            [
                flower.sepal_length,
                flower.sepal_width,
                flower.petal_length,
                flower.petal_width,
            ]
        ]
    )
    probabilities = model.predict_proba(X)[0].tolist()
    return Prediction(
        prediction=CLASSES[int(model.predict(X)[0])],
        probabilities=dict(zip(CLASSES, probabilities, strict=True)),
    )
