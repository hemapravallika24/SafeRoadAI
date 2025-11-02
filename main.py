import pandas as pd
from extract_from_pdf import extract_text_from_pdf
import json
import os

# ---------- Load data ----------
df = pd.read_csv("data/irc_interventions.csv")

# ---------- Cost mapping ----------
cost_map = {"Low": 10000, "Medium": 50000, "High": 200000}

def recommend_interventions(issue_text):
    """Match issue description with IRC interventions"""
    results = []
    for _, row in df.iterrows():
        if any(keyword.lower().strip() in issue_text.lower() for keyword in row["keywords"].split(",")):
            results.append({
                "intervention": row["intervention"],
                "irc_code": row["irc_code"],
                "clause": row["clause"],
                "cost_level": row["cost"],
                "estimated_cost": cost_map.get(row["cost"], 0)
            })
    return results

def process_pdf_report(pdf_path):
    """Extract text from PDF and find interventions"""
    report_text = extract_text_from_pdf(pdf_path)
    sections = [s.strip() for s in report_text.split("\n") if s.strip()]
    results = []

    for issue in sections:
        recs = recommend_interventions(issue)
        if recs:
            total_cost = sum(r["estimated_cost"] for r in recs)
            results.append({
                "issue": issue,
                "recommendations": recs,
                "total_cost": total_cost
            })
    return results

if __name__ == "__main__":
    pdf_path = "data/sample_report.pdf"
    print("🚧 Road Safety Intervention GPT (PDF Mode + Cost Estimation)\n")

    all_results = process_pdf_report(pdf_path)
    grand_total = sum(item["total_cost"] for item in all_results)

    for item in all_results:
        print(f"🛑 Issue: {item['issue']}")
        for rec in item["recommendations"]:
            print(f"   🔹 {rec['intervention']} | {rec['irc_code']} | Clause: {rec['clause']} | Cost: ₹{rec['estimated_cost']:,}")
        print(f"   💰 Total Estimated Cost: ₹{item['total_cost']:,}\n")

    print(f"✅ Grand Total Project Estimate: ₹{grand_total:,}")

    # ---------- Export to JSON ----------
    os.makedirs("output", exist_ok=True)
    output_file = "output/intervention_report.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4, ensure_ascii=False)
    print(f"\n📁 Report saved at: {output_file}")
