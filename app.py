import sqlite3
import uuid
from datetime import datetime

from flask import Flask, jsonify, request

app = Flask(__name__)
DATABASE = 'lending.db'

# --- DB CONNECTION ---
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

# --- INIT DB ---
def init_db():
    with app.app_context():
        db = get_db()
        with open('schema.sql', mode='r') as f:
            db.executescript(f.read())
        db.commit()

# --- HEALTH CHECK ---
@app.route('/')
def home():
    return jsonify({"message": "Bank Lending API is running"}), 200

# --- LEND API ---
@app.route('/lend', methods=['POST'])
def lend():
    data = request.get_json()

    try:
        loan_id = str(uuid.uuid4())
        principal = float(data['loan_amount'])
        years = int(data['loan_period'])
        annual_rate = 10  # example fixed rate
        total_amount = principal + (principal * annual_rate * years / 100)
        monthly_emi = round(total_amount / (years * 12), 2)

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO loans (loan_id, loan_amount, loan_period, interest_rate, total_amount, amount_paid)
            VALUES (?, ?, ?, ?, ?, 0)
        """, (loan_id, principal, years, annual_rate, total_amount))
        db.commit()

        return jsonify({
            "message": "Loan issued successfully",
            "loan_id": loan_id,
            "monthly_emi": monthly_emi,
            "total_amount": total_amount
        }), 201

    except KeyError as e:
        return jsonify({"error": f"Missing field {str(e)}"}), 400

# --- PAYMENT API ---
@app.route('/payment', methods=['POST'])
def payment():
    data = request.get_json()
    try:
        loan_id = data['loan_id']
        payment_type = data['payment_type']  # EMI or LUMP_SUM
        amount = float(data['amount'])

        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT total_amount, amount_paid FROM loans WHERE loan_id = ?", (loan_id,))
        loan = cursor.fetchone()

        if not loan:
            return jsonify({"error": "Loan not found"}), 404

        new_paid = loan['amount_paid'] + amount
        if new_paid > loan['total_amount']:
            return jsonify({"error": "Payment exceeds total amount"}), 400

        cursor.execute("UPDATE loans SET amount_paid = ? WHERE loan_id = ?", (new_paid, loan_id))
        cursor.execute("""
            INSERT INTO payments (loan_id, payment_type, amount, payment_date)
            VALUES (?, ?, ?, ?)
        """, (loan_id, payment_type, amount, datetime.now().isoformat()))
        db.commit()

        return jsonify({
            "message": "Payment successful",
            "loan_id": loan_id,
            "amount_paid": new_paid
        }), 200

    except KeyError as e:
        return jsonify({"error": f"Missing field {str(e)}"}), 400

# --- LEDGER API ---
@app.route('/ledger/<loan_id>', methods=['GET'])
def ledger(loan_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM payments WHERE loan_id = ? ORDER BY payment_date", (loan_id,))
    rows = cursor.fetchall()

    payments = [{
        "payment_type": row["payment_type"],
        "amount": row["amount"],
        "payment_date": row["payment_date"]
    } for row in rows]

    return jsonify({
        "loan_id": loan_id,
        "payments": payments
    }), 200

# --- ACCOUNT OVERVIEW API ---
@app.route('/overview/<loan_id>', methods=['GET'])
def overview(loan_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM loans WHERE loan_id = ?", (loan_id,))
    loan = cursor.fetchone()

    if not loan:
        return jsonify({"error": "Loan not found"}), 404

    balance_amount = loan['total_amount'] - loan['amount_paid']

    return jsonify({
        "loan_id": loan['loan_id'],
        "loan_amount": loan['loan_amount'],
        "loan_period": loan['loan_period'],
        "interest_rate": loan['interest_rate'],
        "total_amount": loan['total_amount'],
        "amount_paid": loan['amount_paid'],
        "balance_amount": balance_amount
    }), 200

if __name__ == '__main__':
    init_db()
    import os

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

