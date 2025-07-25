import requests

BASE_URL = "http://127.0.0.1:5000"

# --- 1. Issue a new loan ---
def issue_loan(loan_amount, loan_period):
    url = f"{BASE_URL}/lend"
    payload = {
        "loan_amount": loan_amount,
        "loan_period": loan_period
    }
    response = requests.post(url, json=payload)
    print("Loan Issuance Response:", response.json())
    return response.json().get("loan_id")

# --- 2. Make a payment ---
def make_payment(loan_id, amount, payment_type="LUMP_SUM"):
    url = f"{BASE_URL}/payment"
    payload = {
        "loan_id": loan_id,
        "payment_type": payment_type,
        "amount": amount
    }
    response = requests.post(url, json=payload)
    print("Payment Response:", response.json())

# --- 3. View ledger ---
def view_ledger(loan_id):
    url = f"{BASE_URL}/ledger/{loan_id}"
    response = requests.get(url)
    print("Ledger Response:", response.json())

# --- 4. View account overview ---
def view_overview(loan_id):
    url = f"{BASE_URL}/overview/{loan_id}"
    response = requests.get(url)
    print("Overview Response:", response.json())

# --- MAIN EXECUTION FLOW ---
if __name__ == "__main__":
    # Step 1: Issue a new loan
    loan_id = issue_loan(loan_amount=15000, loan_period=3)

    if loan_id:
        # Step 2: Make a payment
        make_payment(loan_id, amount=5000)

        # Step 3: View ledger
        view_ledger(loan_id)

        # Step 4: View account overview
        view_overview(loan_id)
