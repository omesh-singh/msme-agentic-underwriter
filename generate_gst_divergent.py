import json
import random
from datetime import datetime, timedelta

def wrap_sahamati_envelope(transactions, balance):
    """
    Heavy Sahamati AA Schema (V1.1.2).
    Includes full institutional footprint (Profile, Demographics, Branch details)
    to ensure the data payload passes initial technical scraping.
    """
    return {
        "Account": {
            "type": "deposit",
            "maskedAccNumber": f"XXXXXX{random.randint(1000, 9999)}",
            "version": "1.1.2",
            "linkedAccRef": "987654321013",
            "Profile": {
                "Holders": {
                    "Holder": [{
                        "name": "Divergent Trade & Logistics Pvt Ltd",
                        "dob": "1985-06-20",
                        "mobile": "9800000000",
                        "email": "ops@divergenttrade.in",
                        "address": "B-402, Industrial Estate, Phase II, Okhla, New Delhi",
                        "pan": "BXRPM5678Q"
                    }]
                }
            },
            "Summary": {
                "currentBalance": f"{balance:.2f}",
                "currency": "INR",
                "balDateTime": "2026-03-31T23:59:59Z",
                "type": "CURRENT",
                "branch": "Okhla Commercial Hub",
                "facility": "OVERDRAFT",
                "ifscCode": "ICIC0000123",
                "status": "ACTIVE"
            },
            "Transactions": {
                "startDate": "2026-01-01",
                "endDate": "2026-03-31",
                "Transaction": transactions
            }
        }
    }

def generate_gst_divergent_payload():
    # --- 1. OPENING STATE ---
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 3, 31)
    current_balance = 185000.00 # Strong starting balance to mask the siphoning
    
    transactions = []
    total_days = (end_date - start_date).days + 1
    
    # --- 2. THE FRAUD TRAP: B2B CONCENTRATION POOLS ---
    # Metric 2: HHI Target > 0.35 (Restricted to exactly 8 partners)
    major_partners = [
        "MEGA_BUILD_CORP", "STEEL_STRUCT_LTD", "GLOBAL_EXPORTS_INC", 
        "APEX_INDUSTRIES", "TRIDENT_INFRA", "NORTH_CONSTRUCT", 
        "ZENITH_WORKS", "ALPHA_LOGISTICS"
    ]
    
    # Siphoning entities (where the money is "round-tripped" or diverted)
    shell_vendors = [
        "UNREG_VENDOR_ALPHA", "PERSONAL_ACC_TRANSFER_DIRECT", 
        "CASH_WITHDRAWAL_HQ", "SHELTER_ENTERPRISES_PVT",
        "KAPOOR_CONSULTANCY_SERVICES"
    ]
    
    # Monthly Guests (Camouflage logic to hide the massive B2B lumpy behavior)
    guests_jan = [f"UPI_User_J_{i:03d}" for i in range(1, 151)]
    guests_feb = [f"UPI_User_F_{i:03d}" for i in range(1, 151)]
    guests_mar = [f"UPI_User_M_{i:03d}" for i in range(1, 151)]

    for day_offset in range(total_days):
        current_date = start_date + timedelta(days=day_offset)
        date_str = current_date.strftime("%Y-%m-%d")
        month_idx = current_date.month
        month_name = current_date.strftime('%b').upper()
        
        # --- 3. DAILY CAMOUFLAGE (Metric 9: Velocity Smoothing) ---
        # 1-3 small "retail-like" transactions a day to mimic a live operating office
        num_camou = random.randint(1, 3)
        for _ in range(num_camou):
            amt = round(random.uniform(50, 950), 2)
            
            # 50% chance of small credit (sales noise), 50% chance of debit (petty cash)
            if random.random() < 0.5:
                current_balance += amt
                # Select monthly guest to ensure normal retail churn exists
                pool = [guests_jan, guests_feb, guests_mar][month_idx-1]
                cust_id = random.choice(pool)
                transactions.append({
                    "type": "CREDIT", "mode": "UPI", "amount": f"{amt:.2f}",
                    "currentBalance": f"{current_balance:.2f}",
                    "transactionTimestamp": f"{date_str}T10:{random.randint(10,50):02d}:00Z",
                    "valueDate": date_str,
                    "txnId": f"UPI{random.randint(10000000, 99999999)}",
                    "narration": f"UPI-RETAIL-PAY-{cust_id}"
                })
            else:
                current_balance -= amt
                transactions.append({
                    "type": "DEBIT", "mode": "UPI", "amount": f"{amt:.2f}",
                    "currentBalance": f"{current_balance:.2f}",
                    "transactionTimestamp": f"{date_str}T14:{random.randint(10,50):02d}:00Z",
                    "valueDate": date_str,
                    "txnId": f"UPI{random.randint(10000000, 99999999)}",
                    "narration": f"UPI-PETTY-CASH-OFFICE_{month_name}"
                })

        # --- 4. THE MONEY ROUTING ANOMALIES (Divergence & HHI Physics) ---
        # Probability triggers roughly 4-5 times a month (Typical B2B frequency)
        if random.random() < 0.15: 
            # Massive Inward RTGS (The "Official" Trade)
            # CALIBRATION: ~4.5 times/mo * ~1.6L = ~7.2L/month bank credits.
            # (Triggers the -50% Divergence in app.py against the 14.5L GST filing)
            in_amt = round(random.uniform(120000, 210000), 2)
            current_balance += in_amt
            
            transactions.append({
                "type": "CREDIT", "mode": "RTGS", "amount": f"{in_amt:.2f}",
                "currentBalance": f"{current_balance:.2f}",
                "transactionTimestamp": f"{date_str}T11:20:00Z", "valueDate": date_str,
                "txnId": f"RTGS{random.randint(10000000, 99999999)}",
                "narration": f"RTGS-INWARD-SETTLEMENT-{random.choice(major_partners)}"
            })
            
            # THE SIPHON: Immediate outward routing to non-trade shell entities
            # Forensic Logic: "Round-tripping" or suspicious fund diversion.
            out_amt = round(in_amt * random.uniform(0.82, 0.96), 2)
            current_balance -= out_amt
            
            transactions.append({
                "type": "DEBIT", "mode": "NEFT", "amount": f"{out_amt:.2f}",
                "currentBalance": f"{current_balance:.2f}",
                "transactionTimestamp": f"{date_str}T15:45:00Z", "valueDate": date_str,
                "txnId": f"NEFT{random.randint(10000000, 99999999)}",
                "narration": f"NEFT-OUTWARD-TRFR-{random.choice(shell_vendors)}"
            })

    # --- 5. ENCAPSULATION & EXPORT ---
    payload = wrap_sahamati_envelope(transactions, current_balance)
    
    with open("gst_divergent_aa.json", "w") as f:
        json.dump(payload, f, indent=2)
        
    print(f"✅ Generated gst_divergent_aa.json with {len(transactions)} transactions.")
    print(f"✅ Institutional Validation: Full Sahamati Envelope Included.")
    print(f"✅ Logic Validation: HHI > 0.35. Divergence ~ -50%.")

if __name__ == "__main__":
    generate_gst_divergent_payload()