import uuid
import random
import datetime

def random_date(start_year=1970, end_year=2000):
    start = datetime.date(start_year, 1, 1)
    end = datetime.date(end_year, 12, 31)
    return start + datetime.timedelta(days=random.randint(0, (end - start).days))

def random_timestamp(days_ago=90):
    now = datetime.datetime.now()
    start = now - datetime.timedelta(days=days_ago)
    random_seconds = random.randint(0, int((now - start).total_seconds()))
    return start + datetime.timedelta(seconds=random_seconds)

def generate():
    sql = ["-- [ignoring loop detection]\n"]
    
    first_names = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Ayaan", "Krishna", "Ishaan", "Shaurya", "Ananya", "Diya", "Aditi", "Isha", "Kavya", "Riya", "Neha", "Pooja", "Anjali", "Sneha", "Rahul", "Rohit", "Amit", "Sumit", "Vikram", "Suresh", "Ramesh", "Sunil", "Anil", "Rajesh"]
    last_names = ["Sharma", "Verma", "Gupta", "Malhotra", "Singh", "Patel", "Reddy", "Rao", "Das", "Bose", "Jain", "Mehta", "Chawla", "Bhatia", "Iyer", "Nair", "Pillai", "Menon", "Khan", "Choudhary"]
    
    customers = []
    cust_vals = []
    for i in range(50):
        cid = str(uuid.uuid4())
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        email = f"{fname.lower()}.{lname.lower()}{random.randint(1,999)}@example.com"
        phone = f"+91{random.randint(9000000000, 9999999999)}"
        dob = random_date(1960, 2002)
        status = random.choice(['ACTIVE']*40 + ['INACTIVE']*5 + ['SUSPENDED']*3 + ['LOCKED']*2)
        
        customers.append({'id': cid, 'fname': fname, 'lname': lname, 'email': email, 'phone': phone, 'dob': dob, 'status': status})
        cust_vals.append(f"('{cid}', '{fname}', '{lname}', '{email}', '{phone}', '{dob}', '{status}')")
        
    sql.append("INSERT INTO customers (id, first_name, last_name, email, phone, date_of_birth, status) VALUES\n" + ",\n".join(cust_vals) + ";\n")
    
    accounts = []
    acc_vals = []
    account_types = ['CHECKING', 'SAVINGS', 'CREDIT', 'LOAN']
    for c in customers:
        for _ in range(random.randint(1, 3)):
            aid = str(uuid.uuid4())
            acc_num = f"IND{random.randint(100000000000, 999999999999)}"
            acc_type = random.choice(account_types)
            curr = 'INR' if random.random() < 0.9 else 'USD'
            
            if acc_type == 'SAVINGS': bal = round(random.uniform(5000, 500000), 2)
            elif acc_type == 'CHECKING': bal = round(random.uniform(10000, 1000000), 2)
            elif acc_type == 'CREDIT': bal = round(random.uniform(-50000, 10000), 2)
            else: bal = round(random.uniform(-1000000, 0), 2)
                
            status = random.choice(['ACTIVE']*85 + ['FROZEN']*5 + ['RESTRICTED']*5 + ['CLOSED']*5)
            
            accounts.append({'id': aid, 'customer_id': c['id'], 'acc_num': acc_num, 'type': acc_type, 'currency': curr, 'balance': bal, 'status': status})
            acc_vals.append(f"('{aid}', '{c['id']}', '{acc_num}', '{acc_type}', '{curr}', {bal}, '{status}')")
            
    sql.append("INSERT INTO accounts (id, customer_id, account_number, account_type, currency, balance, status) VALUES\n" + ",\n".join(acc_vals) + ";\n")

    devices = []
    dev_vals = []
    for _ in range(70):
        did = str(uuid.uuid4())
        c = random.choice(customers)
        fingerprint = str(uuid.uuid4()).replace('-', '')
        dtype = random.choice(['MOBILE', 'DESKTOP', 'TABLET'])
        if dtype == 'MOBILE': os_v = random.choice(['Android 14', 'iOS 18'])
        elif dtype == 'DESKTOP': os_v = random.choice(['Windows 11', 'macOS Sonoma'])
        else: os_v = random.choice(['Android 14', 'iOS 18', 'Windows 11'])
            
        trusted = 'TRUE' if random.random() < 0.8 else 'FALSE'
        devices.append({'id': did, 'customer_id': c['id'], 'fingerprint': fingerprint, 'type': dtype, 'os': os_v, 'trusted': trusted})
        dev_vals.append(f"('{did}', '{c['id']}', '{fingerprint}', '{dtype}', '{os_v}', {trusted})")

    sql.append("INSERT INTO devices (id, customer_id, device_fingerprint, device_type, os_version, is_trusted) VALUES\n" + ",\n".join(dev_vals) + ";\n")

    merchants = []
    merch_vals = []
    merchant_names = [("Amazon India", "5310"), ("Flipkart", "5310"), ("Swiggy", "5812"), ("Zomato", "5812"), ("Reliance Digital", "5732"), ("BigBasket", "5411"), ("Paytm", "4814"), ("IRCTC", "4112"), ("BookMyShow", "7832"), ("Tata Cliq", "5310"), ("Myntra", "5691"), ("MakeMyTrip", "4722"), ("Uber", "4121"), ("Ola", "4121"), ("Blinkit", "5411"), ("Zepto", "5411"), ("Croma", "5732"), ("Nykaa", "5977"), ("FirstCry", "5641"), ("Urban Company", "7299")]
    merchant_pool = [{'name': n, 'mcc': m, 'tier': 'LOW' if random.random() < 0.7 else 'MEDIUM'} for n, m in merchant_names]
    merchant_pool.extend([{'name': 'CryptoEx India', 'mcc': '6051', 'tier': 'HIGH'}, {'name': 'Offshore Betting Site', 'mcc': '7995', 'tier': 'BLACKLISTED'}, {'name': 'Unknown Electronics', 'mcc': '5732', 'tier': 'BLACKLISTED'}])
    while len(merchant_pool) < 30: merchant_pool.append({'name': f"Local Shop {len(merchant_pool)}", 'mcc': '5411', 'tier': 'LOW'})
        
    for m in merchant_pool:
        mid = str(uuid.uuid4())
        merchants.append({'id': mid, 'name': m['name'], 'mcc': m['mcc'], 'tier': m['tier'], 'country': 'IN'})
        merch_vals.append(f"('{mid}', '{m['name']}', '{m['mcc']}', 'IN', '{m['tier']}')")

    sql.append("INSERT INTO merchants (id, merchant_name, category_code, country_code, risk_tier) VALUES\n" + ",\n".join(merch_vals) + ";\n")

    transactions = []
    tx_vals = []
    for _ in range(480):
        tid = str(uuid.uuid4())
        acc = random.choice(accounts)
        merch = random.choice(merchants)
        customer_devices = [d for d in devices if d['customer_id'] == acc['customer_id']]
        dev = random.choice(customer_devices) if customer_devices and random.random() < 0.8 else None
        
        ttype = random.choice(['PURCHASE', 'PURCHASE', 'PURCHASE', 'TRANSFER', 'DEPOSIT', 'WITHDRAWAL', 'REFUND'])
        if ttype in ['DEPOSIT', 'WITHDRAWAL', 'TRANSFER']: merch = None
            
        status = random.choices(['COMPLETED', 'PENDING', 'FAILED', 'REJECTED', 'REVERSED'], weights=[85, 5, 5, 3, 2])[0]
        size = random.choices(['Small', 'Medium', 'Large'], weights=[70, 25, 5])[0]
        if size == 'Small': amt = round(random.uniform(100, 5000), 2)
        elif size == 'Medium': amt = round(random.uniform(5000, 50000), 2)
        else: amt = round(random.uniform(50000, 200000), 2)
            
        ip = f"103.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
        lat, lon = round(random.uniform(8.0, 37.0), 6), round(random.uniform(68.0, 97.0), 6)
        risk = round(random.uniform(0, 30), 2)
        ts = random_timestamp()
        
        m_val = f"'{merch['id']}'" if merch else "NULL"
        d_val = f"'{dev['id']}'" if dev else "NULL"
        transactions.append({'id': tid, 'acc_id': acc['id'], 'amt': amt, 'status': status, 'type': ttype})
        tx_vals.append(f"('{tid}', '{acc['id']}', {m_val}, {d_val}, {amt}, '{acc['currency']}', '{ttype}', '{status}', '{ip}', {lat}, {lon}, {risk}, '{ts}', '{ts}')")
        
    fraud_cases = [
        {'type': 'HIGH_AMOUNT', 'amt': 450000, 'risk': 85.5, 'alert': 'HIGH_RISK_SCORE'},
        {'type': 'HIGH_AMOUNT', 'amt': 490000, 'risk': 88.0, 'alert': 'HIGH_RISK_SCORE'},
        {'type': 'LOC', 'lat': 55.7558, 'lon': 37.6173, 'ip': '45.12.34.56', 'risk': 92.1, 'alert': 'UNUSUAL_LOCATION'},
        {'type': 'LOC', 'lat': 39.9042, 'lon': 116.4074, 'ip': '114.25.66.77', 'risk': 94.5, 'alert': 'UNUSUAL_LOCATION'},
        {'type': 'BLACKLISTED', 'risk': 99.0, 'alert': 'KNOWN_FRAUD_MERCHANT'},
        {'type': 'BLACKLISTED', 'risk': 99.0, 'alert': 'KNOWN_FRAUD_MERCHANT'},
        {'type': 'RAPID', 'amt': 20000, 'risk': 81.2, 'alert': 'VELOCITY_LIMIT'},
        {'type': 'RAPID', 'amt': 20000, 'risk': 83.4, 'alert': 'VELOCITY_LIMIT'},
        {'type': 'RAPID', 'amt': 20000, 'risk': 89.9, 'alert': 'VELOCITY_LIMIT'},
        {'type': 'DEVICE', 'risk': 78.5, 'alert': 'DEVICE_ANOMALY'},
        {'type': 'DEVICE', 'risk': 79.0, 'alert': 'DEVICE_ANOMALY'},
        {'type': 'FAILED_REPEAT', 'status': 'FAILED', 'risk': 65.0, 'alert': 'VELOCITY_LIMIT'},
        {'type': 'FAILED_REPEAT', 'status': 'FAILED', 'risk': 75.0, 'alert': 'VELOCITY_LIMIT'},
        {'type': 'FAILED_REPEAT', 'status': 'FAILED', 'risk': 85.0, 'alert': 'VELOCITY_LIMIT'},
        {'type': 'RANDOM', 'risk': 88.0, 'alert': 'HIGH_RISK_SCORE'},
        {'type': 'RANDOM', 'risk': 91.0, 'alert': 'HIGH_RISK_SCORE'},
        {'type': 'RANDOM', 'risk': 95.0, 'alert': 'HIGH_RISK_SCORE'},
        {'type': 'RANDOM', 'risk': 96.0, 'alert': 'HIGH_RISK_SCORE'},
        {'type': 'RANDOM', 'risk': 82.0, 'alert': 'HIGH_RISK_SCORE'},
        {'type': 'RANDOM', 'risk': 84.0, 'alert': 'HIGH_RISK_SCORE'},
    ]
    
    alert_vals = []
    for fc in fraud_cases:
        tid = str(uuid.uuid4())
        acc = random.choice(accounts)
        merch = random.choice(merchants)
        if fc['type'] == 'BLACKLISTED': merch = next(m for m in merchants if m['tier'] == 'BLACKLISTED')
        dev = random.choice([d for d in devices if d['customer_id'] == acc['customer_id']] or [None])
        if fc['type'] == 'DEVICE': dev = None
        amt = fc.get('amt', round(random.uniform(5000, 50000), 2))
        status = fc.get('status', 'COMPLETED')
        ip = fc.get('ip', f"103.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}")
        lat, lon = fc.get('lat', round(random.uniform(8.0, 37.0), 6)), fc.get('lon', round(random.uniform(68.0, 97.0), 6))
        ts = random_timestamp(days_ago=5)
        
        m_val = f"'{merch['id']}'" if merch else "NULL"
        d_val = f"'{dev['id']}'" if dev else "NULL"
        
        tx_vals.append(f"('{tid}', '{acc['id']}', {m_val}, {d_val}, {amt}, '{acc['currency']}', 'PURCHASE', '{status}', '{ip}', {lat}, {lon}, {fc['risk']}, '{ts}', '{ts}')")
        
        aid = str(uuid.uuid4())
        astatus = random.choice(['NEW', 'UNDER_REVIEW', 'FALSE_POSITIVE', 'CONFIRMED_FRAUD'])
        alert_vals.append(f"('{aid}', '{tid}', '{fc['alert']}', '{astatus}', '{ts}')")

    sql.append("INSERT INTO transactions (id, account_id, merchant_id, device_id, amount, currency, transaction_type, status, ip_address, latitude, longitude, risk_score, created_at, updated_at) VALUES\n" + ",\n".join(tx_vals) + ";\n")
    sql.append("INSERT INTO fraud_alerts (id, transaction_id, alert_type, status, created_at) VALUES\n" + ",\n".join(alert_vals) + ";\n")

    log_vals = []
    for _ in range(10):
        c = random.choice(customers)
        ts = random_timestamp(days_ago=2)
        log_vals.append(f"('{str(uuid.uuid4())}', 'customers', '{c['id']}', 'UPDATE', '{{\"status\": \"ACTIVE\"}}', '{{\"status\": \"{c['status']}\"}}', 'system_admin', '{ts}')")
        
    for _ in range(10):
        t = random.choice([tx for tx in transactions if tx['status'] in ['FAILED', 'REJECTED']])
        ts = random_timestamp(days_ago=1)
        log_vals.append(f"('{str(uuid.uuid4())}', 'transactions', '{t['id']}', 'UPDATE', '{{\"status\": \"PENDING\"}}', '{{\"status\": \"{t['status']}\"}}', 'payment_gateway', '{ts}')")

    sql.append("INSERT INTO audit_logs (id, table_name, record_id, action, old_data, new_data, changed_by, created_at) VALUES\n" + ",\n".join(log_vals) + ";\n")

    with open('seed_data.sql', 'w') as f:
        f.write("\n".join(sql))

if __name__ == "__main__":
    generate()

