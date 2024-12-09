from flask import Flask, request, jsonify, render_template_string
import requests
import re
import json
import logging
import html

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize conversation history (list of prompts and responses)
app.config['CONVERSATION'] = []

# Initialize stop flag for streaming
app.config['STOP_STREAM'] = False

@app.route('/', methods=['GET'])
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <style>
        body {
            font-family: 'Montserrat', sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            align-items: center;
            color: #ffffff;
        }

        #container {
            margin-top: 20px;
            background: linear-gradient(135deg, #222222, #110303);
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
            text-align: center;
            flex-direction: column;
            align-items: center;
            height:85vh;
            width: 90%;
        }

        h1 {
            font-size: 2.5rem;
            margin-bottom: 30px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
        }

        #input-container {
            display: flex;
            width: 100%;
        }

        textarea {
            flex-grow: 1;
            padding: 15px;
            border-radius: 15px;
            border: none;
            outline: none;
            background: #333333;
            color: #ffffff;
            resize: vertical;
            font-size: 1.1rem;
        }

        button {
            width: 100px;
            padding: 15px;
            margin-left: 10px;
            border-radius: 15px;
            border: none;
            outline: none;
            height: 50%;
            background: linear-gradient(135deg, #200770, #02164e);
            color: #ffffff;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 1.1rem;
        }

        button:hover {
            background: linear-gradient(135deg, #01fff2, #6b47dc);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
        }

        #error {
            color: #ff6666;
            font-size: 1rem;
            margin-top: 15px;
        }

        #response-container {
            background-color: hsl(254, 62%, 19%);
            background-image: radial-gradient(ellipse farthest-side at center top, hsl(237, 87%, 18%) 0%, hsl(243, 68%, 18%) 50%, hsl(254, 62%, 19%) 100%);;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 25px;
            text-decoration: solid;
            color: #ffffff;
            border: 1px solid #444;
            text-align: left;
            overflow-y: scroll;
            height: 70vh;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .message {
            display: flex;
            max-width: 80%;
            margin: 5px 0;
            padding: 10px;
            border-radius: 10px;
            word-wrap: break-word;
        }

        .user {
            background: #111cbe;
            align-self: flex-end;
        }

        .bot {
            background: rgba(160,160,208,0.4);
            align-self: flex-start;
        }

        pre {
            font-size: 1rem;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

    </style>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DeepSeek Coder</title>
</head>
<body>
    <div id="container">
        <div id="response-container"></div>
        <div id="input-container">
            <textarea id="prompt" placeholder="Enter your prompt here..."></textarea>
            <button onclick="sendPrompt()">Generate</button>
            <button onclick="stopStream()">Stop</button> <!-- New Stop button -->
        </div>
        <div id="error"></div>
    </div>

<script>
    let eventSource = null; // Store the EventSource globally

    function sendPrompt() {
        const prompt = document.getElementById('prompt').value;
        const responseEl = document.getElementById('response-container');
        const errorEl = document.getElementById('error');
        const generateButton = document.querySelector('button');
        const promptTextarea = document.getElementById('prompt');

        // Disable the button to prevent multiple clicks
        generateButton.disabled = true;

        // Clear previous errors
        errorEl.textContent = '';

        // Display the user input
        appendMessage('user', prompt);

        // Clear the textarea after getting the prompt
        promptTextarea.value = '';

        // Send the prompt to the backend
        fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt }),
        })
        .then((response) => {
            if (!response.ok) {
                throw new Error('Failed to submit the prompt.');
            }

            // Start streaming the response
            eventSource = new EventSource('/stream');
            let botMessageDiv = null;

            eventSource.onmessage = (event) => {
                // If no bot div exists yet, create one
                if (!botMessageDiv) {
                    botMessageDiv = document.createElement('div');
                    botMessageDiv.classList.add('message', 'bot');
                    responseEl.appendChild(botMessageDiv);
                }
                // Append the new part of the bot's message to the existing div
                botMessageDiv.innerHTML += event.data;
            };

            eventSource.onerror = (error) => {
                console.error('EventSource error:', error);
                eventSource.close();
            };

            // Enable the button once streaming starts
            generateButton.disabled = false;
        })
        .catch((error) => {
            console.error('Fetch error:', error);
            errorEl.textContent = `Network Error: ${error.message}`;
            generateButton.disabled = false;
        });
    }

    function stopStream() {
        if (eventSource) {
            eventSource.close(); // Close the EventSource connection
            const responseEl = document.getElementById('response-container');
            appendMessage('bot', 'Streaming stopped.');
            eventSource = null; // Reset the EventSource
        }
    }

    function escapeHTML(text) {
        const div = document.createElement('div');
        div.innerText = text;
        return div.innerHTML;
    }

    function appendMessage(sender, message) {
        const responseEl = document.getElementById('response-container');

        // Create a new div for each message (user or bot)
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        messageDiv.innerHTML = escapeHTML(message); // Escape the message content

        // Append the message div to the response container
        responseEl.appendChild(messageDiv);

        // Scroll to the bottom to show the newest message
        responseEl.scrollTop = responseEl.scrollHeight;
    }

    // Add event listener for 'Enter' key to trigger sendPrompt
    document.getElementById('prompt').addEventListener('keypress', function (event) {
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent the default "Enter" action (new line)
            sendPrompt(); // Trigger the sendPrompt function
        }
    });
</script>


</body>
</html>
    ''')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt', '')

    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    # Reset stop flag when generating a new prompt
    app.config['STOP_STREAM'] = False

    # Append the user prompt to the conversation history
    app.config['CONVERSATION'].append(f"User: {prompt}")

    return jsonify({'message': 'Prompt received. Streaming will begin.'}), 200

@app.route('/stream', methods=['GET'])
def stream():
    conversation = app.config.get('CONVERSATION', [])
    if not conversation:
        app.logger.error("No conversation available. Ensure /generate was called first.")
        return jsonify({'error': 'No conversation available. Please submit the prompt first.'}), 400

    def stream_response():
        try:
            ollama_url = 'http://localhost:11434/api/generate'
            payload = {
                'model': 'mannix/deepseek-coder-v2-lite-instruct:latest',
                'prompt': "\n".join(conversation[-5:]),
                'stream': True,
                'options': {
                    'num_ctx': 8192,
                    'num_predict': 12022,
                    'temperature': 0.5,
                    'top_k': 32,
                    'top_p': 0.7,
                    'repeat_penalty': 1.1,
                    'repeat_last_n': 64,
                    'seed': 42
                }
            }

            with requests.post(ollama_url, json=payload, stream=True, timeout=300) as response:
                response.raise_for_status()

                full_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            json_line = json.loads(line.decode('utf-8'))
                            if 'response' in json_line:
                                response_chunk = format_response(json_line['response'])
                                full_response += response_chunk
                                # Check if the stop flag is set, if so, stop the streaming
                                if app.config['STOP_STREAM']:
                                    yield f"data: Streaming stopped.\n\n"
                                    break
                                yield f"data: {response_chunk}\n\n"
                            if json_line.get('done', False):
                                break
                        except json.JSONDecodeError as e:
                            app.logger.error(f"JSON decode error: {e}")
                            yield f"data: Error parsing response: {str(e)}\n\n"

                # Append the full bot response to conversation history
                if full_response:
                    app.config['CONVERSATION'].append(f"Bot: {full_response}")

        except requests.RequestException as e:
            app.logger.error(f"Request error: {e}")
            yield f"data: Failed to connect to the backend API: {str(e)}\n\n"
        except Exception as e:
            app.logger.error(f"Unexpected error: {e}")
            yield f"data: Unexpected error: {str(e)}\n\n"

    response = app.response_class(stream_response(), content_type='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    response.headers['X-Accel-Buffering'] = 'no'  # Prevent buffering in proxies like Nginx
    return response

def format_response(response_text):
    response_text = html.escape(response_text)
    response_text = re.sub(r'\*\*', '', response_text)
    response_text = re.sub(r'# # # (.*?):', r'<br><br><strong>\1</strong>:', response_text)
    response_text = response_text.replace('\n', '<br>')
    return response_text

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

