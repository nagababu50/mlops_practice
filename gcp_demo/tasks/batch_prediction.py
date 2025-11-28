# gcp_demo/tasks/batch_prediction.py

import cloudpickle
import math
import numpy as np
import pandas as pd
from google.cloud import bigquery
import logging

logger = logging.getLogger("batch_prediction")
logging.basicConfig(level=logging.INFO)


def batch_prediction(
    model_path: str,
    bq_input_table: str,
    bq_output_table: str,
    project: str = "prj-0n-dta-pt-ai-sandbox",
    write_disposition: str = "WRITE_TRUNCATE",
    max_rows_per_load: int = 1_000_000,
):
    """
    Runs batch prediction on a BigQuery table and writes output to another table.

    Args:
        model_path: Path to trained model (cloudpickle file)
        bq_input_table: Fully-qualified BigQuery table (project.dataset.table)
        bq_output_table: Fully-qualified BigQuery table (project.dataset.table)
        project: GCP project for BigQuery client
        write_disposition: WRITE_TRUNCATE | WRITE_APPEND
        max_rows_per_load: max rows per chunk when loading into BigQuery
    """
    # Load model
    with open(model_path, "rb") as f:
        model_obj = cloudpickle.load(f)

    client = bigquery.Client(project=project)

    # Ensure dataset exists
    def ensure_dataset_exists(table_id: str):
        project_id, dataset_id, _ = table_id.split(".")
        dataset_ref = bigquery.Dataset(f"{project_id}.{dataset_id}")
        try:
            client.get_dataset(dataset_ref)
            logger.info(f"Dataset {dataset_id} exists.")
        except Exception:
            logger.info(f"Dataset {dataset_id} not found. Creating...")
            client.create_dataset(dataset_ref, exists_ok=True)

    ensure_dataset_exists(bq_output_table)

    # Read input table
    df = client.query(f"SELECT * FROM `{bq_input_table}`").to_dataframe()
    if df.empty:
        logger.warning("Input dataframe is empty. Exiting.")
        return

    df = df.replace(["NA", "N/A", "na", "null", "NULL", ""], np.nan)
    if "zipcode" not in df.columns:
        df["zipcode"] = "00000"

    # Predict directly (model handles preprocessing internally)
    preds_df = model_obj.predict(df)
    result_df = df.copy()
    result_df["PredictedSalePrice"] = preds_df["price"]

    # Cast object columns to string for BigQuery
    obj_cols = result_df.select_dtypes(include=["object"]).columns
    if len(obj_cols) > 0:
        result_df[obj_cols] = result_df[obj_cols].astype(str)

    # Load into BigQuery (chunked if necessary)
    job_config = bigquery.LoadJobConfig()
    job_config.write_disposition = getattr(bigquery.WriteDisposition, write_disposition)
    job_config.create_disposition = bigquery.CreateDisposition.CREATE_IF_NEEDED

    if len(result_df) > max_rows_per_load:
        total = len(result_df)
        parts = math.ceil(total / max_rows_per_load)
        for i in range(parts):
            start, end = i * max_rows_per_load, min((i + 1) * max_rows_per_load, total)
            chunk = result_df.iloc[start:end]
            cfg = job_config if i == 0 else bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
                create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED
            )
            client.load_table_from_dataframe(chunk, bq_output_table, job_config=cfg).result()
            logger.info("Loaded chunk %d/%d (%d rows)", i + 1, parts, len(chunk))
    else:
        client.load_table_from_dataframe(result_df, bq_output_table, job_config=job_config).result()
        logger.info("Loaded %d rows to %s", len(result_df), bq_output_table)

    logger.info(f"Predictions saved to BigQuery table: {bq_output_table}")
