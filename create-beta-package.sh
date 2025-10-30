#!/bin/bash
#
# Email Automation App - Beta Package Creator
# This script creates a distribution package for beta testers
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Email Automation - Beta Package Creator${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Get version number
read -p "Enter version number (e.g., 1.0): " VERSION
if [ -z "$VERSION" ]; then
    VERSION="1.0"
fi

PACKAGE_NAME="email-automation-beta-v${VERSION}"
ARCHIVE_NAME="${PACKAGE_NAME}.tar.gz"

echo -e "${YELLOW}Creating package: ${ARCHIVE_NAME}${NC}"
echo ""

# Check if required files exist
echo -e "${YELLOW}Checking required files...${NC}"
REQUIRED_FILES=(
    "Dockerfile"
    "docker-compose.yml"
    "requirements.txt"
    ".env.example"
    "BETA_INSTALL.md"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}Error: Missing required file: $file${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} $file"
done

# Check if required directories exist
REQUIRED_DIRS=(
    "src"
    "templates"
    "static"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        echo -e "${RED}Error: Missing required directory: $dir${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} $dir/"
done

echo ""
echo -e "${YELLOW}Cleaning up old packages...${NC}"
rm -f email-automation-beta*.tar.gz 2>/dev/null || true
rm -f email-automation-beta*.zip 2>/dev/null || true
echo -e "${GREEN}✓${NC} Cleanup complete"

echo ""
echo -e "${YELLOW}Creating archive...${NC}"

# Create the tar.gz archive
tar -czf "$ARCHIVE_NAME" \
    --exclude="*.pyc" \
    --exclude="__pycache__" \
    --exclude="*.env" \
    --exclude=".env" \
    --exclude=".git" \
    --exclude="*.log" \
    Dockerfile \
    docker-compose.yml \
    requirements.txt \
    .env.example \
    BETA_INSTALL.md \
    src/ \
    templates/ \
    static/

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Archive created successfully"
else
    echo -e "${RED}Error: Failed to create archive${NC}"
    exit 1
fi

# Get file size
FILE_SIZE=$(du -h "$ARCHIVE_NAME" | cut -f1)

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Package Created Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Package: ${GREEN}$ARCHIVE_NAME${NC}"
echo -e "Size: ${GREEN}$FILE_SIZE${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Test the package yourself first"
echo "2. Upload to cloud storage or GitHub"
echo "3. Send download link to beta testers"
echo "4. Include BETA_INSTALL.md instructions"
echo ""
echo -e "${YELLOW}Quick test command:${NC}"
echo "  mkdir /tmp/beta-test && cd /tmp/beta-test"
echo "  tar -xzf $(pwd)/$ARCHIVE_NAME"
echo "  Follow BETA_INSTALL.md"
echo ""
echo -e "${GREEN}Happy testing!${NC}"
