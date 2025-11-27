# Runbook

## Step 1: Create .env file
```
# Team name (used for project ID derivation)
TEAM_NAME="dta-pt-ai"
SERVICE_ACCOUNT="gc-sa-for-vertex-ai-pipelines@prj-0n-dta-pt-ai-sandbox.iam.gserviceaccount.com"
REPO_NAME="gcp_demo"
BRANCH_NAME="kfp-rj"

# GCP SETTINGS
GCP_REGION="us-east4"
```

## Step 2: Create virtual environment
```
uv sync --all-groups
```

## Step 3: Create and Publish all Docker

```
UV_ENV_FILE=.env uv run -- ./docker/build_and_push.sh
```

## Step 4: Publish Pipeline
```
UV_ENV_FILE=.env uv run python -m pipeline.house_price_pipeline.py
```

## Local Testing

* Use VSCode Launch configuration to run the train job


# Contribution Guide
* Ensure that code is formatted as per PEP8 guidelines. Run this command to ensure format `uv run poe format`
* Ensure that code is annotated by running `uv run poe lint`


