# gcp_demo/tasks/inference.py
from pathlib import Path
import cloudpickle
import pandas as pd
from loguru import logger


def run_inference(
    eval_dataset: Path,
    model_path: Path,
    predictions_output: Path,
):
    """
    Runs inference using the trained HousePredictionModel.

    Args:
        eval_dataset (Path): Path to CSV test data
        model_path (Path): Path to trained model (.pkl)
        predictions_output (Path): Where predictions should be saved
    """

    logger.info("===== Starting Inference =====")

    # Load model
    logger.info(f"Loading model from {model_path}...")
    with open(model_path, "rb") as f:
        model = cloudpickle.load(f)

    # Load test dataset
    logger.info(f"Loading test dataset from {eval_dataset}...")
    df = pd.read_csv(eval_dataset)

    # Remove target col if present
    if "SalePrice" in df.columns:
        logger.info("Dropping target column SalePrice...")
        X_test = df.drop(columns=["SalePrice"])
    else:
        X_test = df.copy()

    # Run predictions (model internally handles preprocessing)
    logger.info("Running model predictions...")
    preds_df = model.predict(X_test)

    # Handle different predict output shapes
    if isinstance(preds, pd.DataFrame) and "price" in preds:
        df["PredictedSalePrice"] = preds["price"]
    else:
        # Fallback: prediction might be just a numpy array
        df["PredictedSalePrice"] = preds

    # Save outputs
    logger.info(f"Saving predictions to {predictions_output}...")
    df.to_csv(predictions_output, index=False)

    logger.info("===== Inference Completed Successfully =====")
