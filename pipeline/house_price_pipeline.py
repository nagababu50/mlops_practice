from kfp import dsl, compiler
from google.cloud import aiplatform
from loguru import logger
from kfp.dsl import Model, Output, Input, Dataset

# from gcp_demo.tasks.train import train
# from gcp_demo.tasks import batch_prediction as bp

from pipeline import config
from tempfile import NamedTemporaryFile

base_image=config.DOCKERS["house_price"]
print(base_image)
print()

@dsl.component(base_image=config.DOCKERS["house_price"])
def train_component(model_output: Output[Model],eval_data: Output[Dataset]):
    """Train the house price prediction model and persist artifact."""
    from gcp_demo.tasks.train import train
    # train(model_output.path)
    train(
        model_output=Path(model_output.path),
        eval_output=Path(eval_data.path),   # <--- NEW
    )


@dsl.component(base_image=config.DOCKERS["house_price"])
def batch_prediction_component(model_path: Input[Model],bq_input_table: str,bq_output_table: str):
    """Runs batch prediction on a BigQuery table and writes output to another table."""
    from gcp_demo.tasks.batch_prediction import batch_prediction

    batch_prediction(
        model_path=model_path.path,
        bq_input_table=bq_input_table,
        bq_output_table=bq_output_table,
    )

@dsl.component(base_image=config.DOCKERS["house_price"])
def inference_component(eval_dataset: Input[Dataset],model_path: Input[Model],predictions_output: Output[Dataset]):
    
    from pathlib import Path
    from gcp_demo.tasks.inference import run_inference
    run_inference(
        eval_dataset=Path(eval_dataset.path),
        model_path=Path(model_path.path),
        predictions_output=Path(predictions_output.path),
    )




@dsl.pipeline(
    name="simple-house-price-prediction",
    description="Simple end-to-end house price prediction pipeline using BQ data",
    pipeline_root=config.PIPELINE_ROOT,
)
def house_price_pipeline():
    """Main pipeline orchestrating all components."""
    # TRAIN COMPONENT
    trained_model = train_component().set_display_name("Train Model")

    # BATCH PREDICTION COMPONENT
    batch_prediction_component(
        model_path=trained_model.outputs["model_output"],
        bq_input_table=f"{config.PROJECT_ID}.housing_dataset_poc.batch_housing_data",
        bq_output_table=f"{config.PROJECT_ID}.housing_dataset_poc.housing_destination_table",
    ).after(trained_model).set_display_name("Batch Prediction")

    # # INFERENCE COMPONENT
    # inference_op = inference_component(
    #     eval_dataset=trained_model.outputs["eval_output"],   # artifact URI for test csv
    #     model_path=trained_model.outputs["model_output"],
    # ).after(batch_prediction).set_display_name("Inference")



if __name__ == "__main__":
    
    # Compile pipeline to a temporary file (JSON IR)
    pipeline_file = NamedTemporaryFile(suffix=".json").name
    compiler.Compiler().compile(
        pipeline_func=house_price_pipeline,
        package_path=pipeline_file
    )
    
    logger.info(f"Pipeline compiled to {pipeline_file}")
    
    # Run the pipeline
    logger.info("\nInitializing Vertex AI...")
    aiplatform.init(project=config.PROJECT_ID, location=config.REGION)
    
    logger.info("Creating pipeline job...")
    job = aiplatform.PipelineJob(
        display_name="simple-house-price-prediction-run",
        template_path=pipeline_file,
        pipeline_root=config.PIPELINE_ROOT,
        enable_caching=False,
        project=config.PROJECT_ID,
        location=config.REGION,
    )
    
    logger.info("Submitting pipeline (sync mode for debugging)...")
    job.run(service_account=config.SERVICE_ACCOUNT)
    
    logger.info("\nPipeline execution completed!")
    logger.info(f"View pipeline in console: {job._dashboard_uri()}")

