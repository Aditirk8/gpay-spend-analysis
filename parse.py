from bs4 import BeautifulSoup
import re

def parse_gpay_html(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml")

    transactions = []

    for cell in soup.find_all(string=re.compile(r"Paid ₹")):
        try:
            text = cell.strip()

            # Extract amount and merchant
            match = re.match(r"Paid ₹([\d.]+) to (.+?) using Bank Account", text)
            if not match:
                continue
            amount = float(match.group(1))
            merchant = match.group(2).strip()

            # Get all text in the transaction block
            parent = cell.parent
            siblings = list(parent.parent.stripped_strings)

            # Extract date
            date_str = None
            for s in siblings:
                if "IST" in s:
                    date_str = s.strip()
                    break

            # Extract transaction ID and status
            # Structure: [..., "Google Pay", transaction_id, status]
            transaction_id = None
            status = None
            for i, s in enumerate(siblings):
                if s == "Completed" or s == "Pending" or s == "Failed":
                    status = s
                    if i >= 1:
                        transaction_id = siblings[i-1].strip()
                    break

            transactions.append({
                "transaction_id": transaction_id,
                "amount": amount,
                "merchant": merchant,
                "datetime_raw": date_str,
                "status": status,
            })

        except Exception as e:
            print(f"Skipped a row due to error: {e}")

    return transactions


if __name__ == "__main__":
    results = parse_gpay_html("data/raw/My Activity.html")
    for r in results[:5]:
        print(r)
    print(f"\nTotal transactions found: {len(results)}")