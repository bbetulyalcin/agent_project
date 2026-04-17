from flask import Flask, jsonify, request
import json

app = Flask(__name__)


def load_db():
    with open('db.json', 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/api/user', methods=['GET'])
def get_user():
    email = request.args.get('email')
    if email:
        email = email.strip().lower() 
        
    db = load_db()
    users = {k.lower(): v for k, v in db['users'].items()}
    
    user = users.get(email)
    if user:
        return jsonify(user)
    
    print(f"--- [DEBUG] Bulunamayan E-posta: '{email}' ---") 
    return jsonify({"error": "User not found"}), 404

@app.route('/api/transactions/<user_id>', methods=['GET'])
def get_transactions(user_id):
    user_id = user_id.strip().upper() 
    db = load_db()

    txs = db['transactions'].get(user_id, [])
    print(f"--- [API] {user_id} için {len(txs)} adet işlem bulundu ---")
    
    return jsonify(txs)

@app.route('/api/fraud-check/<tx_id>', methods=['GET'])
def get_fraud(tx_id):
    tx_id = tx_id.strip().upper() 
    db = load_db()
    
    reason = db['fraud_reasons'].get(tx_id)
    
    if reason:
        return jsonify({"transaction_id": tx_id, "reason": reason})
    
    print(f"--- [DEBUG] {tx_id} için red kaydı bulunamadı ---")
    return jsonify({"error": "No fraud record found for this transaction"}), 404

    
if __name__ == '__main__':
    print("API Sunucusu http://127.0.0.1:5000 adresinde çalışıyor...")
    app.run(port=5000, debug=True)