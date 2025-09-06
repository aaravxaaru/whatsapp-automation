# main.py
from flask import Flask, render_template_string, request, jsonify
import random
import string
import time

app = Flask(__name__)
app.secret_key = "mr-sharabi-wp-tool"

# Simple in-memory storage
sessions = {}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🦋 MR-SHARABI WP TOOL 🦋</title>
<style>
body { font-family: 'Segoe UI', sans-serif; background:#121212; color:#fff; display:flex; flex-direction:column; align-items:center; padding:20px; }
h1 { color:#00ffd0; }
input, select, button { padding:10px; margin:6px 0; border-radius:6px; border:none; font-size:1rem; }
button { background:#00ffd0; color:#121212; cursor:pointer; }
button:hover { background:#ff00cc; color:#fff; }
.status { margin-top:10px; color:#ff00cc; }
</style>
</head>
<body>
<h1>🦋 MR-SHARABI WP TOOL 🦋</h1>

<form id="pairForm">
<label>Generate Pair Code:</label>
<button type="button" onclick="generatePair()">Generate</button>
<p>Pair Code: <span id="pairCode">---</span></p>
</form>

<form id="sendForm" method="POST" enctype="multipart/form-data">
<label>Upload creds.json:</label>
<input type="file" name="creds" required>
<label>Upload SMS file (.txt):</label>
<input type="file" name="sms" required>
<label>Hater's Name:</label>
<input type="text" name="hatersName" required>
<label>Target Type:</label>
<select name="target">
<option value="inbox">Inbox</option>
<option value="group">Group</option>
</select>
<label>Target Number / Group ID:</label>
<input type="text" name="target">
<label>Time Delay (sec):</label>
<input type="number" name="timeDelay" required>
<button type="submit">Start Sending</button>
</form>

<div class="status" id="statusMsg"></div>

<script>
function generatePair(){
    fetch('/start-pair-auth', {method:'POST'})
    .then(res=>res.json())
    .then(data=>{
        if(data.success){
            document.getElementById('pairCode').textContent = data.pair_code;
            document.getElementById('statusMsg').textContent = "✅ Pair Code Generated!";
        }
    });
}

document.getElementById('sendForm').onsubmit = function(e){
    e.preventDefault();
    const formData = new FormData(this);
    fetch('/send', {method:'POST', body:formData})
    .then(res=>res.json())
    .then(data=>{
        document.getElementById('statusMsg').textContent = data.message;
    });
}
</script>
</body>
</html>
"""

def generate_session_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/start-pair-auth', methods=['POST'])
def start_pair_auth():
    session_id = generate_session_id()
    pair_code = ''.join(random.choices(string.ascii_uppercase+string.digits, k=8))
    pair_code = pair_code[:4] + '-' + pair_code[4:]
    sessions[session_id] = {"pair_code": pair_code, "created": time.time()}
    return jsonify({"success": True, "pair_code": pair_code})

@app.route('/send', methods=['POST'])
def send_messages():
    hatersName = request.form.get("hatersName")
    target = request.form.get("target")
    timeDelay = request.form.get("timeDelay")
    # Simple response, actual WhatsApp sending needs API or selenium
    return jsonify({"message": f"Messages to {target} ({hatersName}) scheduled with {timeDelay}s delay."})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
