from flask import Flask, render_template_string, request, jsonify, send_from_directory
from datetime import datetime
import os
import random

app = Flask(__name__)

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

messages = []

# List of pastel colors for user messages
user_colors = {}

# HTML Template with Title, Logout Button, and File Attachment
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shhh 🤫🤐</title>
    <style>
     @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400&family=Shadows+Into+Light&display=swap');
        body {
            font-family: 'Poppins', sans-serif;
            display: flex;
            flex-direction: column;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #f9f9f9, #f1c6f0);
            color: #333;
            overflow: hidden;
        }
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: #ff69b4;
            color: white;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        header h1 {
            font-family: 'Shadows Into Light', cursive;
            font-size: 24px;
            margin: 0;
        }
        #logout-button {
            padding: 10px 20px;
            border: none;
            background: #ffffff;
            color: #ff69b4;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }
        #logout-button:hover {
            background: #ff85c1;
            color: white;
        }
        #chat-box {
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 15px;
            overflow-y: auto;
            background: rgba(255, 255, 255, 0.8);
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            margin: 10px;
            margin-bottom: 80px;
            padding-bottom: 70px; /* Add padding at the bottom to prevent messages from being hidden */
        }

        #messages {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        #messages li {
            padding: 10px 15px;
            margin-bottom: 10px;
            border-radius: 20px;
            background: #f7c0dc;
            color: #000;
            display: block;
            font-family: 'Poppins', sans-serif;
            word-wrap: break-word;
            max-width: 70%;
            line-height: 1.5;
        }
        #message-input {
            display: flex;
            padding: 15px;
            background: #fff;
            border-top: 1px solid #ddd;
            border-radius: 30px;
            margin: 10px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            position: fixed; /* Keep it fixed to the bottom */
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 1000; /* Ensure it stays on top of other elements */
        }


    #message-input input[type="file"] {
        display: none;
    }

    #attach-label {
        padding: 8px 16px;
        border: none;
        background: #ff69b4;
        color: white;
        border-radius: 20px;
        cursor: pointer;
        font-size: 14px;
        transition: background 0.3s;
        margin-right: 10px;
        flex-shrink: 0;
    }

    #attach-label:hover {
        background: #ff85c1;
    }

    #message-input input[type="text"] {
        flex: 1;
        padding: 8px 16px;
        border: 1px solid #ddd;
        border-radius: 20px;
        font-size: 14px;
        outline: none;
        font-family: 'Poppins', sans-serif;
        margin-right: 10px;
    }

    #message-input button {
        padding: 8px 16px;
        border: none;
        background: #ff69b4;
        color: white;
        border-radius: 20px;
        cursor: pointer;
        font-size: 14px;
        transition: background 0.3s;
        flex-shrink: 0;
    }

    #message-input button:hover {
        background: #ff85c1;
    }

    /* Media query for screens ≤ 768px */
    @media (max-width: 768px) {
        header h1 {
            font-size: 18px;
        }
        
        #messages li {
            max-width: 100%;
            font-size: 14px;
            display: block;
            word-break: break-word;
        }

        #message-input {
            padding: 8px;
            flex-direction: column;
            margin: 0;
        }

        #attach-label,
        #message-input input[type="text"],
        #message-input button {
            margin: 5px 0;
            width: 100%;
        }
        
        #message-input input[type="text"] {
            margin-right: 0;
        }
    }
</style>
</head>
<body>
    <header>
        <h1>Shhh 🤫🤐 Secret Chat Room</h1>
        <button id="logout-button" onclick="logout()">Logout</button>
    </header>
    <div id="chat-box">
        <ul id="messages"></ul>
    </div>
    <div id="message-input">
        <label for="file-upload" id="attach-label">Attach File</label>
        <input type="file" id="file-upload" onchange="uploadFile()">
        <input id="message" type="text" autocomplete="off" placeholder="Type your kawaii message...">
        <button onclick="sendMessage()">Send</button>
    </div>

    <script>
        let username = localStorage.getItem('username');
        if (!username) {
            username = prompt("Enter your kawaii name:");
            localStorage.setItem('username', username);
        }

        const messages = document.getElementById('messages');
        const messageInput = document.getElementById('message');

        function fetchMessages() {
            fetch('/messages')
                .then(response => response.json())
                .then(data => {
                    messages.innerHTML = '';
                    data.forEach(msg => {
                        const li = document.createElement('li');
                        if (msg.file_url) {
                            li.innerHTML = msg.username + ': <a href="' + msg.file_url + '" target="_blank">[File: ' + msg.file_url + ']</a>';
                        } else {
                            li.textContent = msg.username + ': ' + msg.message;
                        }
                        li.style.backgroundColor = msg.color;
                        messages.appendChild(li);
                    });
                    messages.scrollTop = messages.scrollHeight;
                });
        }

        function sendMessage() {
            const message = messageInput.value;
            if (message) {
                fetch('/send_message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username: username, message: message })
                }).then(() => {
                    messageInput.value = '';
                    fetchMessages();
                });
            }
        }

        function uploadFile() {
            const fileInput = document.getElementById('file-upload');
            const file = fileInput.files[0];
            if (file) {
                const formData = new FormData();
                formData.append('file', file);
                formData.append('username', username);

                fetch('/upload', {
                    method: 'POST',
                    body: formData
                }).then(response => response.json())
                  .then(data => {
                      fetch('/send_message', {
                          method: 'POST',
                          headers: {
                              'Content-Type': 'application/json',
                          },
                          body: JSON.stringify({ username: username, message: '', file_url: data.file_url })
                      }).then(() => {
                          fetchMessages();
                      });
                  });
            }
        }

        function logout() {
            localStorage.removeItem('username');
            location.reload(); // Reload the page to prompt for a new username
        }

        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        setInterval(fetchMessages, 2000);

        fetchMessages();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/messages')
def get_messages():
    return jsonify(messages)

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    username = data['username']

    if username not in user_colors:
        user_colors[username] = random.choice(['#f7c0dc', '#b0e0e6', '#ffeb3b', '#8bc34a', '#ffc107'])

    message = {
        'username': username,
        'message': data.get('message', ''),
        'file_url': data.get('file_url', None),
        'color': user_colors[username],
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    messages.append(message)
    return '', 204

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    filename = file.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    file_url = f'/download/{filename}'
    return jsonify({'file_url': file_url}), 200

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

