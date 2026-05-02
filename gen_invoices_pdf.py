import os
import random
import csv
import argparse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

VENDORS = ["Acme Supplies","BrightStationery","OfficeGoods Co.","Global Paperworks","PrimeStation"]
ITEMS = ["Notebook","Printer Ink","Stapler","A4 Paper Pack","Desk Lamp","Mouse","Keyboard","USB Cable"]
CURRENCIES = ["USD","EUR"]

def money(x):
    return f"{x:.2f}"

def make_invoice(i):
    vendor = random.choice(VENDORS)
    invoice_no = f"INV-{1000 + i}"
    day = random.randint(1,28)
    month = random.randint(1,12)
    year = random.choice([2024,2025])
    date = f"{year}-{month:02d}-{day:02d}"
    n_items = random.randint(1,6)
    lines = []
    subtotal = 0.0
    for _ in range(n_items):
        desc = random.choice(ITEMS)
        qty = random.randint(1,10)
        unit = round(random.uniform(5,150),2)
        line_total = qty * unit
        subtotal += line_total
        lines.append({"description": desc, "qty": qty, "unit_price": unit, "line_total": line_total})
    tax = round(subtotal * random.choice([0.05,0.07,0.10]),2)
    total = round(subtotal + tax,2)
    currency = random.choice(CURRENCIES)
    return {
        "vendor": vendor,
        "invoice_no": invoice_no,
        "date": date,
        "lines": lines,
        "subtotal": round(subtotal,2),
        "tax": tax,
        "total": total,
        "currency": currency
    }

def write_invoice_pdf(inv, path):
    c = canvas.Canvas(path, pagesize=letter)
    w, h = letter
    x = 50
    y = h - 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, inv["vendor"])
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(x, y, f"Invoice No: {inv['invoice_no']}")
    c.drawString(x+300, y, f"Date: {inv['date']}")
    y -= 20
    c.line(x, y, w-50, y)
    y -= 15
    c.drawString(x, y, "Description")
    c.drawString(x+300, y, "Qty")
    c.drawString(x+350, y, "Unit")
    c.drawString(x+430, y, "Line Total")
    y -= 10
    c.line(x, y, w-50, y)
    y -= 20
    for ln in inv["lines"]:
        if y < 120:
            c.showPage()
            y = h - 50
        c.drawString(x, y, ln["description"])
        c.drawRightString(x+330, y, str(ln["qty"]))
        c.drawRightString(x+410, y, money(ln["unit_price"]))
        c.drawRightString(x+500, y, money(ln["line_total"]))
        y -= 16
    y -= 10
    c.line(x, y, w-50, y)
    y -= 20
    c.drawRightString(x+500, y, "Subtotal: " + money(inv["subtotal"]))
    y -= 16
    c.drawRightString(x+500, y, "Tax: " + money(inv["tax"]))
    y -= 16
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(x+500, y, "Total: " + money(inv["total"]))
    c.save()

def generate(folder, n):
    os.makedirs(folder, exist_ok=True)
    gt = []
    for i in range(1, n+1):
        inv = make_invoice(i)
        fname = f"invoice_{i}.pdf"
        path = os.path.join(folder, fname)
        write_invoice_pdf(inv, path)
        gt.append([fname, inv["vendor"], inv["invoice_no"], inv["date"], f"{inv['subtotal']:.2f}", f"{inv['tax']:.2f}", f"{inv['total']:.2f}", inv["currency"]])
    gt_path = os.path.join(folder, "ground_truth.csv")
    with open(gt_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["file","vendor","invoice_no","date","subtotal","tax","total","currency"])
        writer.writerows(gt)
    print(f"Generated {n} invoices in {folder} with ground_truth.csv")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=50)
    p.add_argument("--out", type=str, default="sample_invoices")
    args = p.parse_args()
    generate(args.out, args.n)
