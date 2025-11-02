import pandas as pd
from app.gpt_model import recommend_interventions

# 1️⃣ Load your interventions data
df = pd.read_csv("data/irc_interventions.csv")


# 2️⃣ Provide sample text (like a small report)
text = """
The road section near the school lacks speed breakers. 
At night, visibility is very poor due to no street lights.
During rain, the surface becomes slippery causing vehicles to skid.
"""

# 3️⃣ Run the recommender
results = recommend_interventions(text, df)

# 4️⃣ Print results
if results:
    print("✅ Recommended Interventions Found:")
    for r in results:
        print(r)
else:
    print("⚠️ No interventions matched.")
