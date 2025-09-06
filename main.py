from flask import Flask, render_template, request, redirect, flash, jsonify
import os
from werkzeug.utils import secure_filename
import json
import threading
import time

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'json'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global variables to track sending status
sending_sessions = {}
session_counter = 0

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send', methods=['POST'])
def send_messages():
    global session_counter
    
    try:
        # Handle file uploads
        creds_file = request.files.get('creds')
        sms_file = request.files.get('sms')
        
        if not creds_file or not sms_file:
            return jsonify({'error': 'Both files are required'}), 400
            
        if not (allowed_file(creds_file.filename) and allowed_file(sms_file.filename)):
            return jsonify({'error': 'Invalid file format'}), 400
        
        # Save uploaded files
        creds_filename = secure_filename(creds_file.filename)
        sms_filename = secure_filename(sms_file.filename)
        
        creds_path = os.path.join(app.config['UPLOAD_FOLDER'], creds_filename)
        sms_path = os.path.join(app.config['UPLOAD_FOLDER'], sms_filename)
        
        creds_file.save(creds_path)
        sms_file.save(sms_path)
        
        # Get form data
        haters_name = request.form.get('hatersName')
        message_target = request.form.get('messageTarget')
        target_number = request.form.get('targetNumber')
        group_id = request.form.get('groupID')
        time_delay = int(request.form.get('timeDelay', 5))
        
        # Generate session key
        session_counter += 1
        session_key = f"session_{session_counter}_{int(time.time())}"
        
        # Store session info
        sending_sessions[session_key] = {
            'status': 'running',
            'haters_name': haters_name,
            'message_target': message_target,
            'target_number': target_number,
            'group_id': group_id,
            'time_delay': time_delay,
            'creds_path': creds_path,
            'sms_path': sms_path
        }
        
        # Start message sending in background (placeholder)
        def send_messages_background(session_key):
            try:
                # Read SMS file
                with open(sms_path, 'r', encoding='utf-8') as f:
                    messages = f.readlines()
                
                # Simulate sending messages (replace with actual WhatsApp API logic)
                for i, message in enumerate(messages):
                    if session_key not in sending_sessions or sending_sessions[session_key]['status'] != 'running':
                        break
                        
                    # Add delay between messages
                    time.sleep(time_delay)
                    
                    # Here you would implement actual WhatsApp API calls
                    print(f"Sending message {i+1}: {message.strip()}")
                
                # Mark session as completed if not stopped
                if session_key in sending_sessions and sending_sessions[session_key]['status'] == 'running':
                    sending_sessions[session_key]['status'] = 'completed'
                    
            except Exception as e:
                print(f"Error in background sending: {str(e)}")
                if session_key in sending_sessions:
                    sending_sessions[session_key]['status'] = 'error'
        
        # Start background thread
        thread = threading.Thread(target=send_messages_background, args=(session_key,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'session_key': session_key,
            'message': f'Message sending started successfully! Session Key: {session_key}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stop', methods=['POST'])
def stop_sending():
    try:
        session_key = request.form.get('sessionKey')
        
        if not session_key:
            return jsonify({'error': 'Session key is required'}), 400
            
        if session_key not in sending_sessions:
            return jsonify({'error': 'Invalid session key'}), 400
            
        # Stop the session
        sending_sessions[session_key]['status'] = 'stopped'
        
        return jsonify({
            'success': True,
            'message': f'Session {session_key} has been stopped successfully!'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status/<session_key>')
def get_status(session_key):
    if session_key in sending_sessions:
        return jsonify(sending_sessions[session_key])
    else:
        return jsonify({'error': 'Session not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
