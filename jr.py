import pandas as pd
import os
import requests

def inject_journal(file_path):
    source = pd.read_excel(file_path, sheet_name="Source Data", header=1)
    journal = pd.read_excel(file_path, sheet_name="Journal Entry", header=6)

    amounts = source["amount"].dropna().reset_index(drop=True)
    journal = journal[(journal["DEBITS"].notna()) | (journal["CREDITS"].notna())].reset_index(drop=True)

    for i in range(min(len(amounts), len(journal))):
        if pd.notna(journal.at[i, "DEBITS"]):
            journal.at[i, "DEBITS"] = amounts[i]
        elif pd.notna(journal.at[i, "CREDITS"]):
            journal.at[i, "CREDITS"] = amounts[i]

    return journal

def generate_payload(journal_df, txn_date="2025-06-24"):
    journal_df.columns = journal_df.columns.str.strip()
    lines = []

    for _, row in journal_df.iterrows():
        debit = row.get("DEBITS", 0) or 0
        credit = row.get("CREDITS", 0) or 0
        base = {
            "DetailType": "JournalEntryLineDetail",
            "Amount": round(debit or credit, 2),
            "Description": row.get("Description", ""),
            "JournalEntryLineDetail": {
                "PostingType": "Debit" if debit else "Credit",
                "AccountRef": { "name": row["Account"] }
            }
        }
        if row.get("Class"):
            base["JournalEntryLineDetail"]["ClassRef"] = { "name": row["Class"] }
        lines.append(base)

    return { "TxnDate": txn_date, "Line": lines }

def post_to_qbo(payload):
    import json
    from dotenv import load_dotenv
    load_dotenv()

    token = os.getenv("ACCESS_TOKEN")
    realm = os.getenv("Realm_ID")
    url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{realm}/journalentry"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.status_code,response.text
