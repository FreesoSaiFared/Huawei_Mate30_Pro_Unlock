#!/bin/bash

# Huawei Mate 30 Pro Unlock Tool - Automatic Setup Script
# Installs dependencies and sets up the environment

set -e  # Exit on any error

echo "🔓 Huawei Mate 30 Pro Unlock Tool - Setup"
echo "=========================================="

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Check for Ubuntu/Debian
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS="Windows"
else
    OS="Unknown"
fi

echo "🖥️  Detected OS: $OS"

# Install Python and pip if not present
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "macOS: brew install python3"
    echo "Windows: Download from python.org"
    exit 1
fi

if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    echo "❌ pip is not installed. Installing pip..."
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        sudo apt install python3-pip -y
    else
        python3 -m ensurepip --default-pip
    fi
fi

# Install rich library
echo "📦 Installing rich library for TUI interface..."
python3 -m pip install rich>=13.0.0 --user

# Install ADB/Fastboot on Ubuntu/Debian
if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    echo "🔧 Installing ADB and Fastboot..."

    # Update package list
    sudo apt update

    # Install ADB
    if ! command -v adb &> /dev/null; then
        echo "📱 Installing ADB..."
        sudo apt install android-tools-adb -y
    else
        echo "✅ ADB already installed"
    fi

    # Install Fastboot
    if ! command -v fastboot &> /dev/null; then
        echo "⚡ Installing Fastboot..."
        sudo apt install android-tools-fastboot -y
    else
        echo "✅ Fastboot already installed"
    fi

elif [[ "$OS" == "macOS" ]]; then
    if ! command -v adb &> /dev/null; then
        echo "📱 Installing ADB/Fastboot via Homebrew..."
        if command -v brew &> /dev/null; then
            brew install android-platform-tools
        else
            echo "❌ Homebrew not found. Please install Homebrew first:"
            echo "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
    else
        echo "✅ ADB/Fastboot already installed"
    fi

elif [[ "$OS" == "Windows" ]]; then
    echo "📱 For Windows, please download and install ADB/Fastboot from:"
    echo "https://developer.android.com/studio/releases/platform-tools"
    echo ""
    echo "Make sure to add the platform-tools directory to your PATH"
fi

# Create desktop shortcut (optional)
if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    read -p "Create desktop shortcut? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        DESKTOP_DIR="$HOME/Desktop"
        if [ -d "$DESKTOP_DIR" ]; then
            cat > "$DESKTOP_DIR/Mate30-Pro-Unlock.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Huawei Mate 30 Pro Unlock
Comment=Unlock bootloader for Huawei Mate 30 Pro
Exec=python3 $(pwd)/mate30_pro_tui.py
Icon=phone
Terminal=true
Categories=System;
EOF
            chmod +x "$DESKTOP_DIR/Mate30-Pro-Unlock.desktop"
            echo "✅ Desktop shortcut created"
        fi
    fi
fi

# Make scripts executable
chmod +x mate30_pro_tui.py
chmod +x setup.sh

# Test installation
echo "🧪 Testing installation..."

if command -v adb &> /dev/null; then
    echo "✅ ADB installed correctly"
else
    echo "❌ ADB not found in PATH"
fi

if command -v fastboot &> /dev/null; then
    echo "✅ Fastboot installed correctly"
else
    echo "❌ Fastboot not found in PATH"
fi

if python3 -c "import rich; print('✅ Rich library installed correctly')" 2>/dev/null; then
    echo "✅ Rich library installed correctly"
else
    echo "❌ Rich library not found"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📱 Next steps:"
echo "1. Enable USB debugging on your device"
echo "2. Connect your device via USB"
echo "3. Run the tool:"
echo "   python3 mate30_pro_tui.py"
echo ""
echo "For help: python3 mate30_pro_tui.py --help"