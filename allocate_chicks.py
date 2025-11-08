import csv
from datetime import datetime

# === CONFIG (adjust once) ===
MAX_PER_CUSTOMER = 1000
REMOTE_ZONES = {"East", "West"}  # Add your remote zones if needed
# (Remote reserve logic can be added later—MVP skips it for speed)

def load_supply():
    with open('supply.txt') as f:
        return int(f.read().strip())

def load_customers():
    customers = []
    with open('customers.csv', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            lfd = row['last_fulfilled_date']
            row['last_fulfilled_date'] = datetime.strptime(lfd, '%Y-%m-%d') if lfd else datetime.min
            row['order_qty'] = int(row['order_qty'])
            customers.append(row)
    return customers

def allocate_chicks(supply, customers):
    remaining = supply
    allocated = []
    waitlisted = []
    
    # 1. Contract farms (fulfill 100% up to MAX_PER_CUSTOMER)
    contract_customers = [c for c in customers if c['tier'] == 'Contract']
    for c in contract_customers:
        qty = min(c['order_qty'], MAX_PER_CUSTOMER)
        if remaining >= qty:
            c['allocated'] = qty
            allocated.append(c)
            remaining -= qty
        else:
            c['allocated'] = 0
            waitlisted.append(c)
    
    # 2. Loyal: sort by oldest last_fulfilled_date (fair rotation)
    loyal_customers = [c for c in customers if c['tier'] == 'Loyal']
    loyal_customers.sort(key=lambda x: x['last_fulfilled_date'])
    for c in loyal_customers:
        qty = min(c['order_qty'], MAX_PER_CUSTOMER)
        if remaining >= qty:
            c['allocated'] = qty
            allocated.append(c)
            remaining -= qty
        else:
            c['allocated'] = 0
            waitlisted.append(c)
    
    # 3. New customers: first in CSV order
    new_customers = [c for c in customers if c['tier'] == 'New']
    for c in new_customers:
        qty = min(c['order_qty'], MAX_PER_CUSTOMER)
        if remaining >= qty:
            c['allocated'] = qty
            allocated.append(c)
            remaining -= qty
        else:
            c['allocated'] = 0
            waitlisted.append(c)
    
    return allocated, waitlisted, remaining

def save_results(allocated, waitlisted):
    # Dispatch list for warehouse
    with open('dispatch_list.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Customer ID', 'Farm Name', 'Phone', 'Chicks Allocated'])
        for c in allocated:
            writer.writerow([c['customer_id'], c['farm_name'], c['phone'], c['allocated']])
    
    # SMS files
    with open('sms_alloc.txt', 'w') as f:
        for c in allocated:
            f.write(f"{c['phone']}: Confirmed {c['allocated']} chicks today. Pickup by 2PM. -ChickFlow\n")
    
    with open('sms_waitlist.txt', 'w') as f:
        for c in waitlisted:
            if c['allocated'] == 0:
                f.write(f"{c['phone']}: Today's chicks fully allocated. You're prioritized for tomorrow. Thank you! -ChickFlow\n")

def main():
    supply = load_supply()
    customers = load_customers()
    print(f"🚛 Allocating {supply} day-old chicks...")
    
    allocated, waitlisted, remaining = allocate_chicks(supply, customers)
    
    print(f"✅ Allocated: {len(allocated)} farms")
    print(f"⏳ Waitlisted: {len(waitlisted)} farms")
    print(f"📦 Leftover: {remaining} chicks")
    
    save_results(allocated, waitlisted)
    print("\n📁 Output files created:")
    print(" - dispatch_list.csv")
    print(" - sms_alloc.txt")
    print(" - sms_waitlist.txt")
    print("\n👉 Next: Send SMS & dispatch!")

if __name__ == "__main__":
    main()