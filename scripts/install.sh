#!/bin/bash

# Shelly CLI Installation Script
# This script installs Shelly CLI for production use

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${BLUE}"
    echo "🐚 ==============================================="
    echo "   Shelly CLI Installation Script"
    echo "   https://github.com/Domains18/shelly"
    echo "===============================================${NC}"
}

# Check if Python is available
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d ' ' -f 2)
    print_info "Found Python $python_version"
    
    # Check if pip is available
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed. Please install pip."
        exit 1
    fi
}

# Install Shelly
install_shelly() {
    print_info "Installing Shelly CLI..."
    
    # Build the package
    print_info "Building package..."
    python3 -m build
    
    # Install the built wheel
    wheel_file=$(ls dist/shelly_cli-*.whl | head -1)
    if [ -z "$wheel_file" ]; then
        print_error "Failed to find built wheel file"
        exit 1
    fi
    
    print_info "Installing $wheel_file"
    pip3 install --user "$wheel_file"
}

# Add to PATH if needed
setup_path() {
    local_bin="$HOME/.local/bin"
    
    if [[ ":$PATH:" != *":$local_bin:"* ]]; then
        print_warning "~/.local/bin is not in your PATH"
        print_info "Adding ~/.local/bin to your PATH..."
        
        # Detect shell and add to appropriate config file
        if [[ $SHELL == *"zsh"* ]]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
            print_info "Added to ~/.zshrc"
        elif [[ $SHELL == *"bash"* ]]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
            print_info "Added to ~/.bashrc"
        else
            print_warning "Unknown shell. Please manually add ~/.local/bin to your PATH"
        fi
        
        print_warning "Please restart your terminal or run 'source ~/.bashrc' (or ~/.zshrc)"
    fi
}

# Verify installation
verify_installation() {
    if command -v shelly &> /dev/null; then
        version=$(shelly --version)
        print_success "Shelly CLI installed successfully!"
        print_success "Version: $version"
        print_info "Run 'shelly --help' to get started"
    else
        print_error "Installation verification failed. Please check the installation manually."
        exit 1
    fi
}

# Main installation process
main() {
    print_header
    
    print_info "Starting installation process..."
    
    # Check prerequisites
    check_python
    
    # Install build dependencies
    print_info "Installing build dependencies..."
    pip3 install --user build wheel setuptools
    
    # Install Shelly
    install_shelly
    
    # Setup PATH
    setup_path
    
    # Verify installation
    verify_installation
    
    print_success "🎉 Installation completed!"
    echo
    print_info "Next steps:"
    echo "  1. Run 'shelly config --setup' to configure Shelly"
    echo "  2. Run 'shelly --help' to see available commands"
    echo "  3. Start managing your repositories with 'shelly list' and 'shelly clone'"
    echo
    print_info "For more information, visit: https://github.com/Domains18/shelly"
}

# Run main function
main
