# Mistral: Enhanced C Programming LLM with Ollama Integration

## Overview
Welcome to **Mistral** — a powerful code analysis Large Language Model (LLM) designed specifically for **C programming**. Mistral is built on the Ollama platform, leveraging state-of-the-art AI to help you analyze and optimize your C code more efficiently.

This repository provides an easy way to set up and run the **G0D model**, a model focused on C programming, with enhanced capabilities for code analysis.

## Features
- **Enhanced C Programming Support**: Tailored to analyze, refactor, and optimize C code.
- **CPU Limiting**: Automatically limits CPU usage to 20%, ensuring that the model runs efficiently without overburdening your system.
- **Seamless Setup**: The script automates the entire setup process, from installation to model creation.

---

## 🚀 Installation

### Prerequisites
Ensure you have the following installed on your machine:
- A Unix-like operating system (Linux/macOS)
- `curl` (for downloading the setup script)
- `cpulimit` (for limiting CPU usage)

### Steps to Install
1. Clone this repository or download the `install.sh` script.
2. Run the following command to install Ollama and set up the environment:

```bash
# Download and run the installation script
echo -e "Downloading Ollama for Mistral configuration...\n"
curl -fsSL https://ollama.com/install.sh | sh

# Set CPU limit to 20% to prevent high resource consumption
echo -e "Setting CPU limit to 20%, preventing CPU bounding...\n"
cpulimit -e ollama -l 20 --quiet &>/dev/null &
disown

# Create the G0D model focused on C programming
echo -e "Creating the G0D model focused on C programming...\n"
ollama create G0D --file Modelfile
