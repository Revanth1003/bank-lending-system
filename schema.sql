DROP TABLE IF EXISTS loans;
DROP TABLE IF EXISTS payments;

CREATE TABLE loans (
    loan_id TEXT PRIMARY KEY,
    loan_amount REAL,
    loan_period INTEGER,
    interest_rate REAL,
    total_amount REAL,
    amount_paid REAL
);

CREATE TABLE payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    loan_id TEXT,
    payment_type TEXT,
    amount REAL,
    payment_date TEXT,
    FOREIGN KEY (loan_id) REFERENCES loans (loan_id)
);
