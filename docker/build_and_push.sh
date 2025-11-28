#!/bin/bash
set -e

# ============================================================================
# Build and Push Training Docker Image
# ============================================================================
# This script builds and pushes the training Docker image to Artifact Registry.
# Configuration is read from the root config.py file.
# ============================================================================


# Extract config values from Python config
REGION=$(python3 -c "from pipeline.config import REGION; print(REGION)")
DOCKER_BASE=$(python3 -c "from pipeline.config import DOCKER_BASE; print(DOCKER_BASE)")
VERSION=$(python3 -c "from pipeline.config import PACKAGE_VERSION; print(PACKAGE_VERSION)")
echo ">>> Loading DOCKERS mapping from Python config..."
DOCKER_LINES=$(python3 - <<'PY'
import json
from pipeline.config import DOCKERS
for name, uri in DOCKERS.items():
	print(f"{name}|{uri}")
PY
)

if [ -z "$DOCKER_LINES" ]; then
	echo "No DOCKERS found in Python config." >&2
	exit 1
fi

echo ">>> Configuring Docker authentication for Artifact Registry (once)..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

COUNT=0
while IFS='|' read -r IMAGE_NAME FULL_IMAGE_URI; do

	# FIXME: automatically create docker registry repo if not exists

	DF="docker/${IMAGE_NAME}.Dockerfile"
	if [ ! -f "$DF" ]; then
		echo "Skipping ${IMAGE_NAME}: Dockerfile '$DF' not found" >&2
		continue
	fi

	echo ">>> Building image: ${IMAGE_NAME} using ${DF}"
	docker build -f "$DF" -t "${IMAGE_NAME}:${VERSION}" .

	echo ">>> Tagging image ${IMAGE_NAME}:${VERSION} as ${FULL_IMAGE_URI}"
	docker tag "${IMAGE_NAME}:${VERSION}" "${FULL_IMAGE_URI}"

	echo ">>> Pushing ${FULL_IMAGE_URI}"
	docker push "${FULL_IMAGE_URI}"

	echo ">>> Successfully pushed ${FULL_IMAGE_URI}"
	COUNT=$((COUNT+1))
done <<< "$DOCKER_LINES"

echo ">>> DONE! Built and pushed ${COUNT} image(s)."
