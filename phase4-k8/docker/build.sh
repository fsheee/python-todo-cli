#!/bin/bash
# Docker Build Script for Phase 4
# Run from: phase4-k8/ directory
# Usage: ./docker/build.sh [OPTIONS]

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BACKEND_TAG="todo-chatbot-backend:latest"
FRONTEND_TAG="todo-chatbot-frontend:latest"
LOAD_TO_MINIKUBE=true

# Resolve repo root relative to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PHASE4_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

SOURCE_BACKEND="$REPO_ROOT/phase3-chatbot/backend"
SOURCE_FRONTEND="$REPO_ROOT/phase3-chatbot/frontend"

while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-tag)  BACKEND_TAG="$2"; shift 2 ;;
        --frontend-tag) FRONTEND_TAG="$2"; shift 2 ;;
        --no-minikube)  LOAD_TO_MINIKUBE=false; shift ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "  --backend-tag TAG    Backend image tag (default: todo-chatbot-backend:latest)"
            echo "  --frontend-tag TAG   Frontend image tag (default: todo-chatbot-frontend:latest)"
            echo "  --no-minikube        Don't load images into Minikube"
            exit 0 ;;
        *) echo -e "${RED}Unknown option: $1${NC}"; exit 1 ;;
    esac
done

echo "========================================="
echo "  Phase 4 Docker Build Script"
echo "========================================="
echo ""

# Step 1: Validate preconditions
echo -e "${YELLOW}[1/5] Validating preconditions...${NC}"

if ! docker --version &> /dev/null; then
    echo -e "${RED}ERROR: Docker not installed${NC}"; exit 1
fi
echo "  Docker OK"

if [ "$LOAD_TO_MINIKUBE" = true ]; then
    if ! minikube status &> /dev/null; then
        echo -e "${RED}ERROR: Minikube not running. Start with: minikube start${NC}"; exit 1
    fi
    echo "  Minikube OK"
fi

[ -d "$SOURCE_BACKEND" ] && echo "  Backend source OK" || { echo -e "${RED}ERROR: Backend not found at $SOURCE_BACKEND${NC}"; exit 1; }
[ -d "$SOURCE_FRONTEND" ] && echo "  Frontend source OK" || { echo -e "${RED}ERROR: Frontend not found at $SOURCE_FRONTEND${NC}"; exit 1; }

echo ""
mkdir -p "$PHASE4_DIR/logs"

# Step 2: Build backend image
echo -e "${YELLOW}[2/5] Building backend image ($BACKEND_TAG)...${NC}"

BACKEND_START=$(date +%s)
if docker build \
    -f "$SCRIPT_DIR/backend-phase3.Dockerfile" \
    -t "$BACKEND_TAG" \
    "$SOURCE_BACKEND" \
    --progress=plain \
    2>&1 | tee "$PHASE4_DIR/logs/backend-build.log"; then
    BACKEND_OK=true
    BACKEND_SIZE=$(docker images "$BACKEND_TAG" --format "{{.Size}}" | head -1)
    echo -e "${GREEN}  Backend built: $BACKEND_SIZE in $(($(date +%s) - BACKEND_START))s${NC}"
else
    BACKEND_OK=false
    echo -e "${RED}  Backend build failed. See logs/backend-build.log${NC}"
fi

echo ""

# Step 3: Build frontend image
echo -e "${YELLOW}[3/5] Building frontend image ($FRONTEND_TAG)...${NC}"

FRONTEND_START=$(date +%s)
if docker build \
    -f "$SCRIPT_DIR/frontend.Dockerfile" \
    -t "$FRONTEND_TAG" \
    "$SOURCE_FRONTEND" \
    --progress=plain \
    2>&1 | tee "$PHASE4_DIR/logs/frontend-build.log"; then
    FRONTEND_OK=true
    FRONTEND_SIZE=$(docker images "$FRONTEND_TAG" --format "{{.Size}}" | head -1)
    echo -e "${GREEN}  Frontend built: $FRONTEND_SIZE in $(($(date +%s) - FRONTEND_START))s${NC}"
else
    FRONTEND_OK=false
    echo -e "${RED}  Frontend build failed. See logs/frontend-build.log${NC}"
fi

echo ""

# Step 4: Load into Minikube
if [ "$LOAD_TO_MINIKUBE" = true ] && [ "$BACKEND_OK" = true ] && [ "$FRONTEND_OK" = true ]; then
    echo -e "${YELLOW}[4/5] Loading images into Minikube...${NC}"
    minikube image load "$BACKEND_TAG" && echo "  Backend loaded" || echo -e "${RED}  Backend load failed${NC}"
    minikube image load "$FRONTEND_TAG" && echo "  Frontend loaded" || echo -e "${RED}  Frontend load failed${NC}"
else
    echo -e "${YELLOW}[4/5] Skipping Minikube load${NC}"
fi

echo ""

# Step 5: Summary
echo -e "${YELLOW}[5/5] Summary${NC}"
echo "========================================="
[ "$BACKEND_OK" = true ] && echo -e "  Backend:  ${GREEN}OK${NC} ($BACKEND_SIZE)" || echo -e "  Backend:  ${RED}FAILED${NC}"
[ "$FRONTEND_OK" = true ] && echo -e "  Frontend: ${GREEN}OK${NC} ($FRONTEND_SIZE)" || echo -e "  Frontend: ${RED}FAILED${NC}"
echo "========================================="

[ "$BACKEND_OK" = true ] && [ "$FRONTEND_OK" = true ] && exit 0 || exit 1
