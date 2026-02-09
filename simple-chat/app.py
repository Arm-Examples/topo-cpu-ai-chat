#!/usr/bin/env python3
"""
Simple chat web interface for llama.cpp server.
Optimized for Arm CPU-based LLM inference.
"""

import os
import json
import requests
from flask import Flask, render_template, request, jsonify, Response
from datetime import datetime

app = Flask(__name__)

# Configuration from environment
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8080')
UI_TITLE = os.getenv('UI_TITLE', 'Arm CPU LLM Chat')
MAX_TOKENS = int(os.getenv('MAX_TOKENS', '2048'))
ENABLE_SVE = os.getenv('ENABLE_SVE', 'OFF')

@app.route('/')
def index():
    """Serve the chat interface"""
    return render_template('index.html', title=UI_TITLE, enable_sve=ENABLE_SVE)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests and stream responses"""
    data = request.json
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    # Get conversation history
    history = data.get('history', [])

    # Build prompt with history
    prompt = build_prompt(history, user_message)

    # Prepare request for llama.cpp server
    llama_request = {
        'prompt': prompt,
        'n_predict': MAX_TOKENS,
        'temperature': 0.7,
        'top_p': 0.9,
        'stream': True,
        'stop': ['<|im_end|>', '<|endoftext|>'],
        'timings_per_token': True
    }

    def generate():
        """Stream responses from llama.cpp server"""
        try:
            response = requests.post(
                f'{BACKEND_URL}/completion',
                json=llama_request,
                stream=True,
                timeout=300
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    # llama.cpp sends SSE format: "data: {json}"
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        json_str = line_str[6:]
                        try:
                            chunk = json.loads(json_str)
                            if 'content' in chunk:
                                predicted_per_second = chunk.get('timings', {}).get('predicted_per_second')
                                yield f"data: {json.dumps({'content': chunk['content'], 'metrics': {'predicted_per_second': predicted_per_second}})}\n\n"

                            # Check if generation is complete
                            if chunk.get('stop', False):
                                yield f"data: {json.dumps({'done': True})}\n\n"
                                break
                        except json.JSONDecodeError:
                            continue

        except requests.exceptions.RequestException as e:
            error_msg = f"Backend error: {str(e)}"
            yield f"data: {json.dumps({'error': error_msg})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        # Check backend health
        response = requests.get(f'{BACKEND_URL}/health', timeout=5)
        backend_healthy = response.status_code == 200

        return jsonify({
            'status': 'healthy' if backend_healthy else 'degraded',
            'backend': 'connected' if backend_healthy else 'disconnected',
            'timestamp': datetime.utcnow().isoformat()
        })
    except requests.exceptions.RequestException:
        return jsonify({
            'status': 'unhealthy',
            'backend': 'disconnected',
            'timestamp': datetime.utcnow().isoformat()
        }), 503

def build_prompt(history, user_message):
    """Build conversation prompt with history"""
    prompt_parts = []

    # System message
    prompt_parts.append(
        "<|im_start|>system\n"
        "You are a helpful AI assistant running on an Arm CPU. "
        "Provide clear, concise, and accurate responses.<|im_end|>\n\n"
    )

    # Add conversation history (last 5 exchanges)
    recent_history = history[-10:] if len(history) > 10 else history
    for msg in recent_history:
        role = msg.get("role", "user")
        content = msg.get("content", "").strip()
        if role == "user":
            prompt_parts.append(f"<|im_start|>user\n{content}<|im_end|>\n")
        elif role == "assistant":
            prompt_parts.append(f"<|im_start|>assistant\n{content}<|im_end|>\n")

    # Add current message
    prompt_parts.append(f"<|im_start|>user\n{user_message}<|im_end|>\n")
    prompt_parts.append("<|im_start|>assistant\n")

    return ''.join(prompt_parts)

if __name__ == '__main__':
    print(f"Starting {UI_TITLE}")
    print(f"Backend: {BACKEND_URL}")
    print(f"Max tokens: {MAX_TOKENS}")
    app.run(host='0.0.0.0', port=3000, debug=False)
