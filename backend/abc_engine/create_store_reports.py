
import os
import pandas as pd
import google.generativeai as genai

# 1️⃣ Get your Gemini API key from env var
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise Exception("Please set GEMINI_API_KEY env variable.")

# 2️⃣ Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-pro")

# 3️⃣ Read the action plan CSV
csv_file = "actionplan.csv"
df = pd.read_csv(csv_file)

# 4️⃣ Get unique stores
stores = df["store_id"].unique()

# 5️⃣ For each store, build prompt and call Gemini
for store_id in stores:
    store_df = df[df["store_id"] == store_id]
    # Convert store data to markdown table text to give context
    table = store_df.to_markdown(index=False)

    prompt = f"""
You are a retail analyst.
For Store {store_id}, here are the SKUs and planned actions from our system:

{table}

Follow this business rule to explain actions:
- donate (days < 4)
- flash sale (4 < days < 6)
- clearance sale (6 < days < 8)
- reroute (8 < days < 15)
- keep on shelf (> 15 days)

Generate:
1. A markdown table grouping SKUs by action:
   - donate, flash sale, clearance sale, reroute, keep on shelf
   - columns: SKU ID, Action, Restock, Target store (if rerouting), Bundle with SKU

2. After the table, **write on its own line**:
   
   Detailed Report

Then write a human-like explanation mentioning:
   - why we took these actions (e.g., days left < 4 etc.)
   - for rerouted SKUs, mention the target store and why (higher expected sales / possible stockouts)
   - bundling suggestions as seen in the data (bundle_with_sku column)
Write it as if explaining to a store manager.
"""

    # 6️⃣ Call Gemini
    response = model.generate_content(prompt)

    # 7️⃣ Save the response to a markdown file
    output_file = f"store_{store_id}_report.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(response.text)

    print(f"✅ Generated report for Store {store_id} → {output_file}")
