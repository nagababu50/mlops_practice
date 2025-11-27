from pathlib import Path

import cloudpickle
import pandas as pd
from loguru import logger
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

from gcp_demo.estimators import HousePredictionModel
import typer


def train(model_output: Path) -> None:
    """Train House Price Prediction Model

    Args:
        model_output (Path): Path to persist trained model artifact
    """
    # Step 1: Get Data
    logger.info("...Downloading data")
    df = pd.read_csv(
        "https://raw.githubusercontent.com/melindaleung/Ames-Iowa-Housing-Dataset/master/data/ames%20iowa%20housing.csv"
    )
    logger.info(f"Data shape: {df.shape}")

    # Step 2: Train Model
    df_train, df_eval = train_test_split(df, test_size=0.1)
    model = HousePredictionModel()
    model.fit(df_train, df_train["SalePrice"])

    # FIXME: Evaluate model performance and
    # raise error if not good enough
    preds = model.predict(df_eval)
    mae = mean_absolute_error(df_eval["SalePrice"], preds['price'])
    logger.info(f"Model MAE on eval set: {mae}")

    # Save outputs for pipeline
    with open(model_output, "wb") as f:
        cloudpickle.dump(model, f)


if __name__ == "__main__":
    typer.run(train)