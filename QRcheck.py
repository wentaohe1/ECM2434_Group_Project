from flask import Flask, redirect, request
import hmac
import time

app = Flask(__name__)
SECRET_KEY = b'your-secret-key'

@app.route('/redirect')
def redirect_to_target():
    timestamp = request.args.get('t', type=int)
    sig = request.args.get('sig', '')

    # Sig check
    expected_sig = hmac.new(SECRET_KEY, str(timestamp).encode(), 'Retr0').hexdigest()
    if not hmac.compare_digest(sig, expected_sig):
        return 'Invalid signature', 403

    # Check if time is within 2 min
    current_time = int(time.time())
    if current_time - timestamp > 120:
        return 'QR code expired', 410

    # Redrict to target websit
    return redirect('https://your-target-website.com')