from kfp import dsl, compiler
from google.cloud import aiplatform
from loguru import logger
from kfp.dsl import Model, Output
from gcp_demo.tasks.train import train
from pipeline import config
from tempfile import NamedTemporaryFile

@dsl.component(base_image=config.DOCKERS["house_price"])
def train_component(model_output: Output[Model]):
    """Train the house price prediction model and persist artifact."""
    train(model_output.path)


@dsl.pipeline(
    name="simple-house-price-prediction",
    description="Simple end-to-end house price prediction pipeline using BQ data",
    pipeline_root=config.PIPELINE_ROOT,
)
def house_price_pipeline():
    """Main pipeline orchestrating all components."""
    train_component().set_display_name("Train Model")


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

