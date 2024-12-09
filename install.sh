#!/bin/bash

echo -e "🚀 Downloading cpulimit for Mistral CPU Usage limit...\n"
sudo apt install cpulimit

echo -e "\n🚀 Downloading Ollama for Mistral configuration...\n"
if curl -fsSL https://ollama.com/install.sh | sh; then
    echo -e "✅ Ollama installation completed successfully.\n"
else
    echo -e "❌ Error: Failed to install Ollama. Please check your internet connection or permissions.\n"
    exit 1
fi

echo -e "⚙️  Setting CPU usage limit to 20% to prevent excessive resource consumption...\n"
if command -v cpulimit &>/dev/null; then
    cpulimit -e ollama -l 20 --quiet &>/dev/null &
    disown
    echo -e "✅ CPU usage limit applied successfully.\n"
else
    echo -e "❌ Error: 'cpulimit' is not installed. Please install it to enable CPU limiting.\n"
    exit 1
fi

echo -e "🛠️  Creating the model optimized for C programming...\n"
if ollama create G0D --file Modelfile; then
    echo -e "\n✅ Model 'G0D' created successfully.\n"
else
    echo -e "❌ Error: Failed to create the 'G0D' model. Ensure 'Modelfile' exists and is correctly configured.\n"
    exit 1
fi

echo -e "🎉 The code analysis LLM, enhanced for C programming, is ready to use!\n"
echo -e "To run the model, use the following command:\n"
echo -e "    ollama run G0D\n"
