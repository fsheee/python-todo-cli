#!/bin/bash
# Docker Build Script for Phase 4
# Implements: phase4-docker-build skill
# Version: 1.0.0

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
BACKEND_TAG="todo-chatbot-backend:latest"
FRONTEND_TAG="todo-chatbot-frontend:latest"
LOAD_TO_MINIKUBE=true
SOURCE_BACKEND="../../phase3-chatbot"
SOURCE_FRONTEND="../../phase3-chatbot/frontend"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-tag)
            BACKEND_TAG="$2"
            shift 2
            ;;
        --frontend-tag)
            FRONTEND_TAG="$2"
            shift 2
            ;;
        --no-minikube)
            LOAD_TO_MINIKUBE=false
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --backend-tag TAG       Backend image tag (default: todo-chatbot-backend:latest)"
            echo "  --frontend-tag TAG      Frontend image tag (default: todo-chatbot-frontend:latest)"
            echo "  --no-minikube           Don't load images into Minikube"
            echo "  --help                  Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo "========================================="
echo "  Phase 4 Docker Build Script"
echo "========================================="
echo ""

# Step 1: Validate preconditions
echo -e "${YELLOW}[1/7] Validating preconditions...${NC}"

if ! docker --version &> /dev/null; then
    echo -e "${RED}ERROR: Docker not installed${NC}"
    exit 1
fi
echo "✅ Docker is installed"

if [ "$LOAD_TO_MINIKUBE" = true ]; then
    if ! minikube status &> /dev/null; then
        echo -e "${RED}ERROR: Minikube not running${NC}"
        echo "Start Minikube with: minikube start"
        exit 1
    fi
    echo "✅ Minikube is running"
fi

if [ ! -d "$SOURCE_BACKEND" ]; then
    echo -e "${RED}ERROR: Backend source not found at $SOURCE_BACKEND${NC}"
    exit 1
fi
echo "✅ Backend source found"

if [ ! -d "$SOURCE_FRONTEND" ]; then
    echo -e "${RED}ERROR: Frontend source not found at $SOURCE_FRONTEND${NC}"
    exit 1
fi
echo "✅ Frontend source found"

echo ""

# Create logs directory
mkdir -p ../logs

# Step 2: Build backend image
echo -e "${YELLOW}[2/7] Building backend image...${NC}"
echo "Image tag: $BACKEND_TAG"

BACKEND_START=$(date +%s)
if docker build \
    -f docker/backend-phase3.Dockerfile \
    -t "$BACKEND_TAG" \
    "$SOURCE_BACKEND" \
    --progress=plain \
    2>&1 | tee ../logs/backend-build.log; then

    BACKEND_EXIT_CODE=0
    BACKEND_END=$(date +%s)
    BACKEND_TIME=$((BACKEND_END - BACKEND_START))
    BACKEND_SIZE=$(docker images "$BACKEND_TAG" --format "{{.Size}}")
    echo -e "${GREEN}✅ Backend image built successfully${NC}"
    echo "   Size: $BACKEND_SIZE"
    echo "   Build time: ${BACKEND_TIME}s"
else
    BACKEND_EXIT_CODE=$?
    echo -e "${RED}❌ Backend image build failed${NC}"
    echo "   Check logs at: logs/backend-build.log"
fi

echo ""

# Step 3: Build frontend image
echo -e "${YELLOW}[3/7] Building frontend image...${NC}"
echo "Image tag: $FRONTEND_TAG"

FRONTEND_START=$(date +%s)
if docker build \
    -f docker/frontend.Dockerfile \
    -t "$FRONTEND_TAG" \
    "$SOURCE_FRONTEND" \
    --progress=plain \
    2>&1 | tee ../logs/frontend-build.log; then

    FRONTEND_EXIT_CODE=0
    FRONTEND_END=$(date +%s)
    FRONTEND_TIME=$((FRONTEND_END - FRONTEND_START))
    FRONTEND_SIZE=$(docker images "$FRONTEND_TAG" --format "{{.Size}}")
    echo -e "${GREEN}✅ Frontend image built successfully${NC}"
    echo "   Size: $FRONTEND_SIZE"
    echo "   Build time: ${FRONTEND_TIME}s"
else
    FRONTEND_EXIT_CODE=$?
    echo -e "${RED}❌ Frontend image build failed${NC}"
    echo "   Check logs at: logs/frontend-build.log"
fi

echo ""

# Step 4: Verify images built
echo -e "${YELLOW}[4/7] Verifying images...${NC}"

if docker images | grep -q "$BACKEND_TAG"; then
    echo "✅ Backend image verified in Docker"
else
    echo -e "${RED}❌ Backend image not found in Docker${NC}"
    BACKEND_EXIT_CODE=1
fi

if docker images | grep -q "$FRONTEND_TAG"; then
    echo "✅ Frontend image verified in Docker"
else
    echo -e "${RED}❌ Frontend image not found in Docker${NC}"
    FRONTEND_EXIT_CODE=1
fi

echo ""

# Step 5: Load images into Minikube (if enabled)
if [ "$LOAD_TO_MINIKUBE" = true ] && [ $BACKEND_EXIT_CODE -eq 0 ] && [ $FRONTEND_EXIT_CODE -eq 0 ]; then
    echo -e "${YELLOW}[5/7] Loading images into Minikube...${NC}"

    echo "Loading backend image..."
    if minikube image load "$BACKEND_TAG"; then
        echo "✅ Backend image loaded into Minikube"
        BACKEND_IN_MINIKUBE=true
    else
        echo -e "${RED}❌ Failed to load backend image into Minikube${NC}"
        BACKEND_IN_MINIKUBE=false
    fi

    echo "Loading frontend image..."
    if minikube image load "$FRONTEND_TAG"; then
        echo "✅ Frontend image loaded into Minikube"
        FRONTEND_IN_MINIKUBE=true
    else
        echo -e "${RED}❌ Failed to load frontend image into Minikube${NC}"
        FRONTEND_IN_MINIKUBE=false
    fi

    echo ""
    echo "Verifying images in Minikube..."
    minikube image ls | grep todo-chatbot || echo "No images found"
else
    echo -e "${YELLOW}[5/7] Skipping Minikube load${NC}"
    BACKEND_IN_MINIKUBE=false
    FRONTEND_IN_MINIKUBE=false
fi

echo ""

# Step 6: Generate status report
echo -e "${YELLOW}[6/7] Generating status report...${NC}"

cat > ../logs/build-status.json <<EOF
{
  "backend": {
    "success": $([ $BACKEND_EXIT_CODE -eq 0 ] && echo "true" || echo "false"),
    "image": "$BACKEND_TAG",
    "size": "${BACKEND_SIZE:-unknown}",
    "build_time": "${BACKEND_TIME:-unknown}s",
    "loaded_to_minikube": $BACKEND_IN_MINIKUBE
  },
  "frontend": {
    "success": $([ $FRONTEND_EXIT_CODE -eq 0 ] && echo "true" || echo "false"),
    "image": "$FRONTEND_TAG",
    "size": "${FRONTEND_SIZE:-unknown}",
    "build_time": "${FRONTEND_TIME:-unknown}s",
    "loaded_to_minikube": $FRONTEND_IN_MINIKUBE
  },
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF

echo "Status report saved to: logs/build-status.json"
cat ../logs/build-status.json

echo ""

# Step 7: Create PHR (Prompt History Record)
echo -e "${YELLOW}[7/7] Creating PHR...${NC}"

PHR_FILE="../history/prompts/docker-build-$(date +%Y-%m-%d-%H-%M-%S).md"

cat > "$PHR_FILE" <<EOF
# Docker Build Execution

**Date:** $(date)
**Skill:** phase4-docker-build v1.0.0
**Status:** $([ $BACKEND_EXIT_CODE -eq 0 ] && [ $FRONTEND_EXIT_CODE -eq 0 ] && echo "✅ SUCCESS" || echo "❌ FAILURE")

## Summary

### Backend
- **Image:** $BACKEND_TAG
- **Status:** $([ $BACKEND_EXIT_CODE -eq 0 ] && echo "✅ Success" || echo "❌ Failed")
- **Exit Code:** $BACKEND_EXIT_CODE
- **Size:** ${BACKEND_SIZE:-unknown}
- **Build Time:** ${BACKEND_TIME:-unknown}s
- **In Minikube:** $BACKEND_IN_MINIKUBE

### Frontend
- **Image:** $FRONTEND_TAG
- **Status:** $([ $FRONTEND_EXIT_CODE -eq 0 ] && echo "✅ Success" || echo "❌ Failed")
- **Exit Code:** $FRONTEND_EXIT_CODE
- **Size:** ${FRONTEND_SIZE:-unknown}
- **Build Time:** ${FRONTEND_TIME:-unknown}s
- **In Minikube:** $FRONTEND_IN_MINIKUBE

## Logs
- Backend: \`logs/backend-build.log\`
- Frontend: \`logs/frontend-build.log\`
- Status JSON: \`logs/build-status.json\`

## Next Steps

### Verify Images
\`\`\`bash
# Check Docker images
docker images | grep todo-chatbot

# Check Minikube images (if loaded)
minikube image ls | grep todo-chatbot
\`\`\`

### Deploy with Helm
\`\`\`bash
cd phase4-k8
helm install todo-app helm/gordon -f secrets.yaml
\`\`\`

### Verify Deployment
\`\`\`bash
kubectl get pods
kubectl get svc
kubectl get ingress
\`\`\`

## Troubleshooting

$(if [ $BACKEND_EXIT_CODE -ne 0 ] || [ $FRONTEND_EXIT_CODE -ne 0 ]; then
    echo "### Build Failures Detected"
    echo ""
    echo "**Common Issues:**"
    echo "- Missing dependencies in requirements.txt or package.json"
    echo "- Python/Node version mismatch"
    echo "- Out of disk space"
    echo "- Network issues downloading packages"
    echo ""
    echo "**Actions:**"
    echo "1. Review build logs for specific errors"
    echo "2. Verify Phase 3 code integrity"
    echo "3. Check Docker daemon status"
    echo "4. Ensure sufficient disk space"
else
    echo "No issues detected. Build completed successfully."
fi)
EOF

echo "PHR created at: $PHR_FILE"

echo ""
echo "========================================="
echo "  Build Complete"
echo "========================================="

# Exit with appropriate code
if [ $BACKEND_EXIT_CODE -eq 0 ] && [ $FRONTEND_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All images built successfully${NC}"
    exit 0
else
    echo -e "${RED}❌ Some builds failed${NC}"
    exit 1
fi
