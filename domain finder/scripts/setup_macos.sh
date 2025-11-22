#!/bin/bash

# Domain Finder - macOS Setup Script
# Version: 1.0
# Date: 2025-11-15
# Platform: macOS 10.15+

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo ""
echo "======================================================================"
echo "🏐 DOMAIN FINDER - AUTOMATED SETUP FOR macOS"
echo "======================================================================"
echo ""

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Step 1: Check Python version
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 STEP 1: Checking Python Version"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3.8+ required (found: $PYTHON_VERSION)"
        print_info "Install Python 3.8+ with: brew install python3"
        exit 1
    fi
else
    print_error "Python 3 not found"
    print_info "Install with: brew install python3"
    exit 1
fi

# Step 2: Create virtual environment
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔨 STEP 2: Creating Virtual Environment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$PROJECT_ROOT"

if [ -d "venv" ]; then
    print_warning "Virtual environment already exists"
    read -p "Remove and recreate? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        print_info "Removed existing venv"
    else
        print_info "Keeping existing venv"
    fi
fi

if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_success "Using existing virtual environment"
fi

# Step 3: Activate virtual environment
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚡ STEP 3: Activating Virtual Environment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

source venv/bin/activate
print_success "Virtual environment activated"

# Step 4: Upgrade pip
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 STEP 4: Upgrading pip"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

pip install --upgrade pip --quiet
print_success "pip upgraded to latest version"

# Step 5: Install dependencies
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 STEP 5: Installing Dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

print_info "Installing requirements..."
pip install -r requirements.txt --quiet

# Verify installations
REQUIRED_PACKAGES=("requests" "pandas" "python-dotenv" "PyYAML")
ALL_INSTALLED=true

for package in "${REQUIRED_PACKAGES[@]}"; do
    if python -c "import $package" 2>/dev/null; then
        print_success "$package installed"
    else
        print_error "$package NOT installed"
        ALL_INSTALLED=false
    fi
done

if [ "$ALL_INSTALLED" = false ]; then
    print_error "Some packages failed to install"
    exit 1
fi

# Step 6: Create .env file
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔑 STEP 6: Setting up Environment Variables"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f ".env" ]; then
    print_warning ".env file already exists"
    read -p "Overwrite with template? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        print_success ".env file created from template"
    else
        print_info "Keeping existing .env file"
    fi
else
    cp .env.example .env
    print_success ".env file created from template"
fi

print_warning "⚠️  IMPORTANT: Edit .env file with your Google API credentials"
print_info "See docs/API_SETUP.md for instructions"

# Step 7: Create necessary directories
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 STEP 7: Creating Directories"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

mkdir -p logs
mkdir -p data/input
mkdir -p data/output

print_success "Directory structure created"

# Step 8: Validate installation
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ STEP 8: Validating Installation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python scripts/validate_env.py

# Final summary
echo ""
echo "======================================================================"
echo "🎉 SETUP COMPLETE!"
echo "======================================================================"
echo ""
print_success "Virtual environment: venv/"
print_success "Dependencies: Installed"
print_success "Configuration: .env created"
print_success "Directories: Created"
echo ""
print_warning "⚠️  NEXT STEPS:"
echo "   1. Edit .env file with your Google API credentials"
echo "   2. Run: source venv/bin/activate"
echo "   3. Run: python src/domain_finder.py"
echo ""
print_info "📖 Documentation: README.md and USAGE_GUIDE.md"
echo ""
echo "======================================================================"