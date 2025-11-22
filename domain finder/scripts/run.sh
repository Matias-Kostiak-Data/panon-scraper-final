#!/bin/bash

# Domain Finder - Quick Run Script
# Version: 1.0

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${BLUE}🚀 Starting Domain Finder...${NC}"
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✅ Virtual environment activated${NC}"
else
    echo -e "${RED}❌ Virtual environment not found${NC}"
    echo "Run: ./scripts/setup_macos.sh"
    exit 1
fi

# Run the script
python src/domain_finder.py