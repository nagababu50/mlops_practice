"""
Centralized Configuration for MLOps Pipeline

This module provides a single source of truth for all configuration values.
Most values are auto-derived from minimal user inputs following team conventions.

Usage:
    Only modify the USER_CONFIG section at the top. All other values are derived automatically.
"""

import os
from importlib import metadata
from glob import glob
from loguru import logger

# ENVIRONMENT VARIABLES 
TEAM_NAME: str = os.environ["TEAM_NAME"]
REPO_NAME: str = os.environ['REPO_NAME']
BRANCH_NAME: str = os.environ['BRANCH_NAME']
PACKAGE_VERSION: str = metadata.version("gcp_demo")


REGION: str = os.environ.get("GCP_REGION", "us-east4")


# ============================================================================
# AUTO-DERIVED CONFIGURATION - Do not modify directly
# ============================================================================
# FIXME: DETERMINE WHAT CONVENTION IS THE BEST FROM GOVERNANCE PERSPECTIVE ALSO THINKING FROM CHARGEBACK PERSPECTIVE
SERVICE_ACCOUNT=f"gc-sa-for-vertex-ai-pipelines@prj-0n-{TEAM_NAME}-sandbox.iam.gserviceaccount.com"

# Project ID: Auto-derived from team name convention or use override
PROJECT_ID: str = f"prj-0n-{TEAM_NAME}-sandbox"

# GCS Configuration
BUCKET_URI: str = f"gs://{TEAM_NAME}/{REPO_NAME}/{BRANCH_NAME}".replace("_", "-")

# Pipeline Configuration
PIPELINE_ROOT: str = f"{BUCKET_URI}/pipeline_root"


# Model Artifacts Configuration
ARTIFACT_URI: str = f"{BUCKET_URI}/artifacts"

# Docker Image Repository Base
DOCKER_BASE = f"{REGION}-docker.pkg.dev/{PROJECT_ID}/{REPO_NAME}/{BRANCH_NAME}".replace("_", "-")
DOCKERS = {}
for docker_path in glob("docker/*.Dockerfile"):
    docker_name = docker_path.split("/")[-1].split(".")[0]
    DOCKERS[docker_name] = f"{DOCKER_BASE}/{docker_name}:{PACKAGE_VERSION}"

if __name__ == "__main__":
    logger.info("===== PIPELINE CONFIGURATION =====")
    logger.info(f"TEAM_NAME: {TEAM_NAME}")
    logger.info(f"PROJECT_ID: {PROJECT_ID}")
    logger.info(f"REGION: {REGION}")
    logger.info(f"BUCKET_URI: {BUCKET_URI}")
    logger.info(f"PIPELINE_ROOT: {PIPELINE_ROOT}")
    logger.info(f"SERVICE_ACCOUNT: {SERVICE_ACCOUNT}")
    logger.info("DOCKER IMAGES:")
    for name, uri in DOCKERS.items():
        logger.info(f"  {name}: {uri}")


