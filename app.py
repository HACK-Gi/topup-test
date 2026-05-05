from flask import Flask, render_template, request, jsonify, send_from_directory
from datetime import datetime, timedelta
import qrcode
from io import BytesIO
import base64
import requests
import time
import random
import os
from bakong_khqr import KHQR
import json
from functools import wraps

app = Flask(__name__)

# Bakong API setup
api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7ImlkIjoiMmEyMDE3MzUxMGU4NDZhMiJ9LCJpYXQiOjE3NTk3MjIzNjAsImV4cCI6MTc2NzQ5ODM2MH0._d3PWPYi-N_mPyt-Ntxj5qbtHghOdtZhka2LbdJlKRw"
khqr = KHQR(api_token)
current_transactions = {}

# Data Store API configuration
DATA_STORE_URL = 'https://mengtopup.shop'  # Change this to your data store server URL

# Admin authentication decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        password = request.args.get('pass')
        if password != "1516Coolb":
            return "Unauthorized", 401
        return f(*args, **kwargs)
    return decorated_function

# Load transactions from data store API
def load_transactions():
    try:
        response = requests.get(f'{DATA_STORE_URL}/transactions?store=mengtopup', timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return {"pending": [], "expired": [], "completed": []}

# Save transactions to data store API
def save_transactions(transactions):
    try:
        response = requests.post(f'{DATA_STORE_URL}/transactions?store=mengtopup', 
                               json=transactions, timeout=5)
        response.raise_for_status()
        return response.json().get('success', False)
    except requests.RequestException:
        return False

# Add a single transaction to data store
def add_transaction_to_store(transaction_data, status):
    try:
        response = requests.post(f'{DATA_STORE_URL}/transactions?store=mengtopup/add', 
                               json={
                                   'status': status,
                                   'transaction': transaction_data
                               }, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

# ---------- ទិន្នន័យកញ្ចប់លំនាំដើម (Default Packages) ----------
DEFAULT_PACKAGES = {
    "ml": [
        {"name": "55", "price": 0.94, "package_id": "55"},
        {"name": "86", "price": 1.35, "package_id": "86"},
        {"name": "112", "price": 1.95, "package_id": "112"},
        {"name": "165", "price": 2.75, "package_id": "165"},
        {"name": "172", "price": 2.85, "package_id": "172"},
        {"name": "257", "price": 3.95, "package_id": "257"},
        {"name": "275", "price": 4.05, "package_id": "275"},
        {"name": "343", "price": 5.25, "package_id": "343"},
        {"name": "429", "price": 6.45, "package_id": "429"},
        {"name": "514", "price": 7.65, "package_id": "514"},
        {"name": "565", "price": 8.25, "package_id": "565"},
        {"name": "600", "price": 8.95, "package_id": "600"},
        {"name": "706", "price": 10.25, "package_id": "706"},
        {"name": "792", "price": 11.55, "package_id": "792"},
        {"name": "878", "price": 12.85, "package_id": "878"},
        {"name": "963", "price": 14.05, "package_id": "963"},
        {"name": "1049", "price": 15.25, "package_id": "1049"},
        {"name": "1135", "price": 16.45, "package_id": "1135"},
        {"name": "1220", "price": 17.95, "package_id": "1220"},
        {"name": "1412", "price": 21.25, "package_id": "1412"},
        {"name": "1584", "price": 23.99, "package_id": "1584"},
        {"name": "1755", "price": 25.95, "package_id": "1755"},
        {"name": "1926", "price": 28.50, "package_id": "1926"},
        {"name": "2195", "price": 31.25, "package_id": "2195"},
        {"name": "2538", "price": 36.25, "package_id": "2538"},
        {"name": "2901", "price": 40.99, "package_id": "2901"},
        {"name": "3688", "price": 52.00, "package_id": "3688"},
        {"name": "4394", "price": 62.50, "package_id": "4394"},
        {"name": "5532", "price": 78.90, "package_id": "5532"},
        {"name": "6238", "price": 89.50, "package_id": "6238"},
        {"name": "6944", "price": 102.00, "package_id": "6944"},
        {"name": "7727", "price": 105.00, "package_id": "7727"},
        {"name": "8433", "price": 125.00, "package_id": "8433"},
        {"name": "9288", "price": 135.00, "package_id": "9288"},
        {"name": "10700", "price": 155.00, "package_id": "10700"},
        {"name": "Weekly", "price": 1.75, "package_id": "weekly"},
        {"name": "Weekly2", "price": 3.35, "package_id": "weekly2"},
        {"name": "Weekly3", "price": 5.00, "package_id": "weekly3"},
        {"name": "Weekly4", "price": 6.60, "package_id": "weekly4"},
        {"name": "Weekly5", "price": 8.25, "package_id": "weekly5"},
        {"name": "172+wkp", "price": 4.80, "package_id": "172_wkp"},
        {"name": "257+wkp", "price": 5.85, "package_id": "257_wkp"},
        {"name": "Twilight", "price": 9.25, "package_id": "twilight"},
        {"name": "50x2", "price": 1.10, "package_id": "50x2"},
        {"name": "150x2", "price": 2.85, "package_id": "150x2"},
        {"name": "250x2", "price": 4.25, "package_id": "250x2"},
        {"name": "500x2", "price": 8.90, "package_id": "500x2"},
        {"name": "ValuePass", "price": 0.99, "package_id": "valuepass"},
        {"name": "WEB", "price": 1.10, "package_id": "web"},
        {"name": "MEB", "price": 4.60, "package_id": "meb"}
    ],
    "ff": [
        {"name": "25", "price": 0.01, "package_id": "25"},
        {"name": "100", "price": 0.94, "package_id": "100"},
        {"name": "310", "price": 2.79, "package_id": "310"},
        {"name": "520", "price": 4.25, "package_id": "520"},
        {"name": "1060", "price": 8.49, "package_id": "1060"},
        {"name": "2180", "price": 17.25, "package_id": "2180"},
        {"name": "5600", "price": 40.99, "package_id": "5600"},
        {"name": "11500", "price": 82.00, "package_id": "11500"},
        {"name": "Weekly", "price": 1.75, "package_id": "weekly_ff"},
        {"name": "Weekly2", "price": 3.45, "package_id": "weekly2_ff"},
        {"name": "Weekly3", "price": 5.10, "package_id": "weekly3_ff"},
        {"name": "Weekly4", "price": 6.75, "package_id": "weekly4_ff"},
        {"name": "Weekly5", "price": 8.35, "package_id": "weekly5_ff"},
        {"name": "WeeklyLite", "price": 0.39, "package_id": "weekly_lite"},
        {"name": "WeeklyLite2", "price": 0.75, "package_id": "weekly_lite2"},
        {"name": "WeeklyLite3", "price": 1.10, "package_id": "weekly_lite3"},
        {"name": "WeeklyLite4", "price": 1.45, "package_id": "weekly_lite4"},
        {"name": "WeeklyLite5", "price": 1.75, "package_id": "weekly_lite5"},
        {"name": "Monthly", "price": 7.99, "package_id": "monthly"},
        {"name": "Monthly2", "price": 15.80, "package_id": "monthly2"},
        {"name": "Monthly3", "price": 23.50, "package_id": "monthly3"},
        {"name": "Monthly4", "price": 31.00, "package_id": "monthly4"},
        {"name": "Monthly5", "price": 38.50, "package_id": "monthly5"},
        {"name": "Evo3D", "price": 0.85, "package_id": "evo3d"},
        {"name": "Evo7D", "price": 1.05, "package_id": "evo7d"},
        {"name": "Evo30D", "price": 2.90, "package_id": "evo30d"},
        {"name": "Level6", "price": 0.39, "package_id": "level6"},
        {"name": "Level10", "price": 0.75, "package_id": "level10"},
        {"name": "Level15", "price": 0.75, "package_id": "level15"},
        {"name": "Level20", "price": 0.75, "package_id": "level20"},
        {"name": "Level25", "price": 0.75, "package_id": "level25"},
        {"name": "Level30", "price": 0.75, "package_id": "level30"}
    ],
    "pubg": [],
    "hok": [],
    "bloodstrike": [],
    "mcgg": [],
    "mlph": [],
    "ml_special_offers": [],
    "ff_special_offers": [],
    "pubg_special_offers": [],
    "hok_special_offers": [],
    "bloodstrike_special_offers": [],
    "mcgg_special_offers": [],
    "mlph_special_offers": []
}

def load_packages():
    """ទាញយក packages ពី Data Store API បើមិនបាន ប្រើ DEFAULT_PACKAGES"""
    try:
        response = requests.get(f'{DATA_STORE_URL}/packages?store=mengtopup', timeout=5)
        response.raise_for_status()
        data = response.json()
        # Ensure all keys exist
        for key in DEFAULT_PACKAGES:
            if key not in data:
                data[key] = DEFAULT_PACKAGES[key]
        return data
    except requests.RequestException:
        # Return default packages if API is unavailable
        return DEFAULT_PACKAGES
        
# ... rest of the original code follows (unchanged except for load_packages) ...

# Add this route to app.py
@app.route('/admin')
@admin_required
def admin_panel():
    status_filter = request.args.get('status', 'pending')
    search_query = request.args.get('search', '').lower()
    
    transactions = load_transactions()
    filtered = transactions.get(status_filter, [])
    
    if search_query:
        filtered = [t for t in filtered if (
            search_query in t.get('transaction_id', '').lower() or
            search_query in t.get('player_id', '').lower() or
            search_query in t.get('zone_id', '').lower() or
            search_query in t.get('package', '').lower() or
            search_query in t.get('game_type', '').lower()
        )]
    
    return render_template('admin.html', 
                         transactions=filtered,
                         current_status=status_filter,
                         search_query=search_query)

# Add this before the routes
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    return value.strftime(format)

# Create static/images directory if it doesn't exist
os.makedirs('static/images', exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

# Add these new routes for each game
@app.route('/mobile-legends')
def mobile_legend():
    return render_template('index.html')

@app.route('/free-fire')
def free_fire():
    return render_template('index.html')

@app.route('/pubg-mobile')
def pubg_mobile():
    return render_template('index.html')

@app.route('/honor-of-kings')
def honor_of_kings():
    return render_template('index.html')

@app.route('/blood-strike')
def blood_strike():
    return render_template('index.html')

@app.route('/magic-chess-go-go')
def magic_chess_go_go():
    return render_template('index.html')

@app.route('/mobile-legend')
def mobile_legend_ph():
    return render_template('index.html')


@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)


@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    try:
        amount = float(request.form['amount'])
        player_id = request.form.get('player_id', '')
        zone_id = request.form.get('zone_id', '0')
        package = request.form.get('package', '')
        game_type = request.form.get('game_type', 'ml')

        # Validate amount
        if amount <= 0:
            return jsonify({'error': 'Amount must be greater than 0'}), 400
        if amount > 10000:
            return jsonify({'error': 'Maximum amount is $10,000'}), 400

        # Verify package exists and price matches
        packages = load_packages()
        valid_package = False
        valid_price = False
        
        # Check in regular packages
        for pkg in packages.get(game_type, []):
            if pkg.get('name') == package:
                valid_package = True
                if float(pkg.get('price', 0)) == amount:
                    valid_price = True
                break
        
        # If not found in regular packages, check special offers
        if not valid_package:
            for offer in packages.get(f"{game_type}_special_offers", []):
                if offer.get('name') == package:
                    valid_package = True
                    if float(offer.get('price', 0)) == amount:
                        valid_price = True
                    break

        if not valid_package:
            return jsonify({'error': 'Invalid package selected'}), 400
        
        if not valid_price:
            return jsonify({'error': 'Package price does not match selected amount'}), 400

        # Generate transaction ID
        transaction_id = f"TRX{int(time.time())}"
        
        # Create QR data
        qr_data = khqr.create_qr(
            bank_account='meng_topup@aclb',
            merchant_name='Meng Topup',
            merchant_city='Phnom Penh',
            amount=amount,
            currency='USD',
            store_label='MShop',
            phone_number='855976666666',
            bill_number=transaction_id,
            terminal_label='Cashier-01',
            static=False
        )
        
        # Generate MD5 hash for verification
        md5_hash = khqr.generate_md5(qr_data)
        
        # Generate QR image
        qr_img = qrcode.make(qr_data)
        img_io = BytesIO()
        qr_img.save(img_io, 'PNG')
        img_io.seek(0)
        qr_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
        
        # Store current transaction 
        expiry = datetime.now() + timedelta(minutes=2)
        current_transactions[transaction_id] = {
            'amount': amount,
            'md5_hash': md5_hash,
            'expiry': expiry.isoformat(),
            'player_id': player_id,
            'zone_id': zone_id,
            'package': package,
            'game_type': game_type
        }
        
        return jsonify({
            'success': True,
            'qr_image': qr_base64,
            'transaction_id': transaction_id,
            'amount': amount,
            'expiry': expiry.isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/check_payment', methods=['POST'])
def check_payment():
    try:
        transaction_id = request.form['transaction_id']
        
        # First, check if transaction is already completed in data store
        transactions = load_transactions()
        completed_transactions = [t for t in transactions['completed'] if t['transaction_id'] == transaction_id]
        
        if completed_transactions:
            completed_txn = completed_transactions[0]
            # If already completed, return final status without further checking
            return jsonify({
                'status': 'COMPLETED',
                'message': f'Payment of ${completed_txn["amount"]:.2f} was already processed!',
                'amount': completed_txn["amount"],
                'final': True  # Add flag to indicate this is final status
            })
        
        # Check if transaction exists in current session
        if transaction_id not in current_transactions:
            return jsonify({'error': 'Invalid transaction ID'}), 400
            
        transaction = current_transactions[transaction_id]
        
        # Check if expired
        if datetime.now() > datetime.fromisoformat(transaction['expiry']):
            # Move to expired if not already there
            if not any(t['transaction_id'] == transaction_id for t in transactions['expired']):
                transactions['expired'].append({
                    **transaction,
                    'transaction_id': transaction_id,
                    'status': 'expired',
                    'timestamp': datetime.now().isoformat()
                })
                save_transactions(transactions)
                
            return jsonify({
                'status': 'EXPIRED',
                'message': 'QR​ កូដ បានផុតកំណត់ហើយ។',
                'final': True  # Final status for expired
            })
        
        md5_hash = transaction['md5_hash']
        
        # Use the new API endpoint to check payment status
        response = requests.get(f"https://aiden-bakong-proxy.vercel.app/api/check?md5={md5_hash}", timeout=5)
        
        if response.status_code == 200:
            payment_data = response.json()
            status = payment_data.get('status', 'UNPAID')
            
            if status == "PAID":
                amount = transaction['amount']
                
                # Move to completed
                completed_transaction = {
                    **transaction,
                    'transaction_id': transaction_id,
                    'status': 'completed',
                    'timestamp': datetime.now().isoformat(),
                    'telegram_sent': False
                }
                transactions['completed'].append(completed_transaction)
                # Remove from pending if exists
                transactions['pending'] = [t for t in transactions['pending'] 
                                         if t['transaction_id'] != transaction_id]
                save_transactions(transactions)
                
                # Send to Telegram only once
                send_to_telegram(completed_transaction)
                
                # Update transaction to mark Telegram as sent
                for t in transactions['completed']:
                    if t['transaction_id'] == transaction_id:
                        t['telegram_sent'] = True
                save_transactions(transactions)
                
                # Remove from current transactions to prevent future checks
                if transaction_id in current_transactions:
                    del current_transactions[transaction_id]
                
                return jsonify({
                    'status': 'PAID',
                    'message': f'Payment of ${amount:.2f} បានទទួលប្រាក់!',
                    'amount': amount,
                    'final': True  # This is the final status
                })
                
            elif status == "UNPAID":
                # Add to pending if not already there
                if not any(t['transaction_id'] == transaction_id for t in transactions['pending']):
                    transactions['pending'].append({
                        **transaction,
                        'transaction_id': transaction_id,
                        'status': 'pending',
                        'timestamp': datetime.now().isoformat()
                    })
                    save_transactions(transactions)
                    
                return jsonify({
                    'status': 'UNPAID',
                    'message': 'មិនទាន់ទូទាត់ប្រាក់',
                    'final': False  # Can continue checking
                })
            else:
                return jsonify({
                    'status': 'ERROR',
                    'message': f'Status: {status}',
                    'final': False
                })
        else:
            return jsonify({
                'status': 'ERROR',
                'message': 'Failed to check payment status',
                'final': False
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update the admin_packages and admin_special_offers routes to include HOK
@app.route('/admin/packages')
@admin_required
def admin_packages():
    """Admin endpoint for managing regular packages including MCGG"""
    try:
        packages = load_packages()
    except Exception as e:
        app.logger.error(f"Error loading packages: {str(e)}")
        packages = {
            "ml": [],
            "ff": [],
            "pubg": [],
            "hok": [],
            "bloodstrike": [],
            "mcgg": [],
            "mlph": []
        }
    
    # Validate package structure
    for game_type in ['ml', 'ff', 'pubg', 'hok', 'bloodstrike', 'mcgg', 'mlph']:
        if not isinstance(packages.get(game_type, []), list):
            packages[game_type] = []
            app.logger.warning(f"Invalid package format for {game_type}, reset to empty list")
    
    return render_template('admin_packages.html', 
                         ml_packages=packages.get('ml', []),
                         ff_packages=packages.get('ff', []),
                         pubg_packages=packages.get('pubg', []),
                         hok_packages=packages.get('hok', []),
                         bloodstrike_packages=packages.get('bloodstrike', []),
                         mcgg_packages=packages.get('mcgg', []),
                         mlph_packages=packages.get('mlph', []))

@app.route('/admin/special_offers')
@admin_required
def admin_special_offers():
    """Admin endpoint for managing special offers including MCGG"""
    try:
        packages = load_packages()
    except Exception as e:
        app.logger.error(f"Error loading special offers: {str(e)}")
        packages = {
            "ml_special_offers": [],
            "ff_special_offers": [],
            "pubg_special_offers": [],
            "hok_special_offers": [],
            "bloodstrike_special_offers": [],
            "mcgg_special_offers": [],
            "mlph_special_offers": []
        }
    
    # Validate special offers structure
    for game_type in ['ml', 'ff', 'pubg', 'hok', 'bloodstrike', 'mcgg', 'mlph']:
        offer_key = f"{game_type}_special_offers"
        if not isinstance(packages.get(offer_key, []), list):
            packages[offer_key] = []
            app.logger.warning(f"Invalid special offers format for {game_type}, reset to empty list")
    
    return render_template('admin_special_offers.html',
        ml_offers=packages.get("ml_special_offers", []),
        ff_offers=packages.get("ff_special_offers", []),
        pubg_offers=packages.get("pubg_special_offers", []),
        hok_offers=packages.get("hok_special_offers", []),
        bloodstrike_offers=packages.get("bloodstrike_special_offers", []),
        mcgg_offers=packages.get("mcgg_special_offers", []),
        mlph_offers=packages.get("mlph_special_offers", [])
    )

@app.route('/admin/update_package', methods=['POST'])
@admin_required
def update_package():
    try:
        data = request.get_json() or request.form
        game_type = data.get('game_type')
        package_name = data.get('package_name')
        new_price = data.get('new_price')

        if not all([game_type, package_name, new_price]):
            return jsonify({'error': 'Missing required fields'}), 400

        try:
            new_price = float(new_price)
        except ValueError:
            return jsonify({'error': 'Price must be a number'}), 400

        # Update via API
        response = requests.post(f'{DATA_STORE_URL}/packages/update?store=mengtopup', 
                               json={
                                   'game_type': game_type,
                                   'package_name': package_name,
                                   'new_price': new_price,
                                   'is_special_offer': False
                               }, timeout=5)
        
        if response.status_code == 200:
            return jsonify({'success': True, 'new_price': new_price})
        else:
            return jsonify({'error': 'Failed to update package'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_packages')
def get_packages():
    try:
        packages = load_packages()
        
        # Ensure all required keys exist
        required_keys = [
            'ml', 'ff', 'pubg', 'hok', 'bloodstrike', 'mcgg', 'mlph',
            'ml_special_offers', 'ff_special_offers', 'pubg_special_offers',
            'hok_special_offers', 'bloodstrike_special_offers', 'mcgg_special_offers', 'mlph_special_offers'
        ]
        
        for key in required_keys:
            if key not in packages:
                packages[key] = []
        
        return jsonify(packages)
        
    except Exception as e:
        print(f"Error loading packages: {str(e)}")
        return jsonify({
            "ml": [],
            "ff": [],
            "pubg": [],
            "hok": [],
            "bloodstrike": [],
            "mcgg": [],
            "ml_special_offers": [],
            "ff_special_offers": [],
            "pubg_special_offers": [],
            "hok_special_offers": [],
            "bloodstrike_special_offers": [],
            "mcgg_special_offers": [],
            "mlph_special_offers": [],
            "error": str(e)
        }), 500
    
@app.route('/admin/update_special_offer', methods=['POST'])
@admin_required
def update_special_offer():
    try:
        data = request.get_json() or request.form
        game_type = data.get('game_type')
        offer_name = data.get('offer_name')
        new_price = data.get('new_price')

        if not all([game_type, offer_name, new_price]):
            return jsonify({'error': 'Missing required fields'}), 400

        try:
            new_price = float(new_price)
        except ValueError:
            return jsonify({'error': 'Price must be a number'}), 400

        # Update via API
        response = requests.post(f'{DATA_STORE_URL}/packages/update?store=mengtopup', 
                               json={
                                   'game_type': game_type,
                                   'package_name': offer_name,
                                   'new_price': new_price,
                                   'is_special_offer': True
                               }, timeout=5)
        
        if response.status_code == 200:
            return jsonify({'success': True, 'new_price': new_price})
        else:
            return jsonify({'error': 'Failed to update special offer'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/transactions')
def transactions_page():
    """Display transactions page for users"""
    return render_template('transactions.html')

@app.route('/api/transactions')
def api_transactions():
    """API endpoint to get transactions data"""
    try:
        transactions = load_transactions()
        
        # Combine all transactions and sort by timestamp (newest first)
        all_txns = []
        for status in ['pending', 'completed', 'expired']:
            for txn in transactions.get(status, []):
                txn['status'] = status
                all_txns.append(txn)
        
        # Sort by timestamp, newest first
        all_txns.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return jsonify({
            'success': True,
            'transactions': all_txns
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def send_to_telegram(transaction):
    """Send transaction details to Telegram"""
    # Generate invoice number
    invoice_number = f"INVNO-S{datetime.now().strftime('%Y%m%d%H%M')}"
    
    # Load packages data
    try:
        packages_data = load_packages()
    except Exception:
        packages_data = {}
    
    # Get package name (the item name from default_packages, e.g., "55", "Weekly")
    game_type = transaction.get('game_type', 'ml')
    package_name = transaction.get('package', '')
    
    # Determine processing channel and format according to new structure
    if game_type == 'ff':  # Free Fire
        process_chat_id = '-1003998311429'
        process_text = f"ff {transaction['player_id']} {package_name}"
    elif game_type == 'bloodstrike':
        process_chat_id = '-1003998311429'
        process_text = f"bloodstrike {transaction['player_id']} 0000 {package_name}"
    elif game_type == 'pubg':  # PUBG Mobile
        process_chat_id = '-1003998311429'
        process_text = f"pubg {transaction['player_id']} 0000 {package_name}"
    elif game_type == 'hok':  # HONOR OF KING
        process_chat_id = '-1003998311429'
        process_text = f"hok {transaction['player_id']} 0000 {package_name}"
    elif game_type == 'mcgg':  # Magic Chess: Go Go
        process_chat_id = '-1003998311429'
        process_text = f"magicchess {transaction['player_id']} {transaction['zone_id']} {package_name}"
    elif game_type == 'mlph':  # Mobile Legend PH
        process_chat_id = '-1003998311429'
        process_text = f"mlbbph {transaction['player_id']} {transaction['zone_id']} {package_name}"
    else:  # Mobile Legends (default)
        process_chat_id = '-1003998311429'
        process_text = f"mlbb {transaction['player_id']} {transaction['zone_id']} {package_name}"
    
    # Create invoice message               
    invoice_text = (
        "Payment Successful\n"
        f"📄 Invoice: {invoice_number}\n"
        f"👤 Player ID: {transaction['player_id']}\n"
        f"🌐 Zone ID: {transaction['zone_id']}\n"
        f"🎮 Package: {package_name}\n"
        f"💵 Amount: ${float(transaction['amount']):.2f}\n"
        f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    
    try:
        # Send to processing channel with timeout
        requests.post(
            'https://api.telegram.org/bot8218348626:AAHHMxBKNC-iz3midb86aJsG8ueBX6juxuw/sendMessage',
            json={
                'chat_id': process_chat_id,
                'text': process_text
            },
            timeout=5
        )
        
        # Send to invoice channel with timeout
        requests.post(
            'https://api.telegram.org/bot8218348626:AAHHMxBKNC-iz3midb86aJsG8ueBX6juxuw/sendMessage',
            json={
                'chat_id': '-1003998311429',
                'text': invoice_text,
                'parse_mode': 'Markdown'
            },
            timeout=5
        )
        
        return invoice_number
        
    except Exception as e:
        print(f"Error sending to Telegram: {e}")
        return None
if __name__ == '__main__':
    app.run()
