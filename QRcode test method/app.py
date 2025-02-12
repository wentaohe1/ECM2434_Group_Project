from flask import Flask, jsonify, redirect, request, render_template
import hmac
import time
from flask_cors import CORS
from flask_socketio import SocketIO, emit


app = Flask(__name__)
CORS(app)  
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")  # WebSocket

SECRET_KEY = b'your-secret-key'

@app.route('/')
def home():
    return render_template('example.html') 

# QRcode summoner
def generate_dynamic_params():
    timestamp = int(time.time() // 120) * 120
    signature = hmac.new(SECRET_KEY, str(timestamp).encode(), 'sha256').hexdigest()
    return {"t": timestamp, "sig": signature}

# WebSocket link
@socketio.on('connect')
def handle_connect():
    params = generate_dynamic_params()
    emit('qr_update', params)
    print(f"Front end linked send the first message: {params}")

# Send code every 2 min
def push_qr_update():
    """Upload via every 2 min"""
    while True:
        socketio.sleep(120)  # trigger every 2 mins
        params = generate_dynamic_params()
        socketio.emit('qr_update', params)
        print(f"New code send: {params}")

@socketio.on('start_update')
def handle_start_update():
    socketio.start_background_task(target=push_qr_update)


@app.route('/redirect')
def redirect_to_target():
    # get timestamp
    timestamp = request.args.get('t', type=int)
    sig = request.args.get('sig', '')
    
    # panding timestamp
    if not timestamp or not sig:
        return 'Missing parameters', 400
    
    # panding sig
    expected_sig = hmac.new(
        SECRET_KEY, 
        str(timestamp).encode(), 
        'sha256'
    ).hexdigest()
    if not hmac.compare_digest(sig, expected_sig):
        return 'Invalid signature', 403
    
    # check time limit
    current_time = int(time.time())
    if current_time - timestamp > 120:
        return 'QR code expired', 410
    
    # Redirect
    return redirect('https://your-target-website.com')

if __name__ == '__main__':
    socketio.run(app, debug=True)