import spacy

# Load NLP model
nlp = spacy.load("en_core_web_sm")

def recommend_interventions(text, df):
    # Normalize column names to avoid KeyError
    df.columns = df.columns.str.strip().str.lower()

    results = []
    doc = nlp(text.lower())

    for _, row in df.iterrows():
        keywords = [k.strip().lower() for k in row['keywords'].split(',')]
        intervention_name = row['intervention']
        matched = False

        for keyword in keywords:
            for token in doc:
                if keyword in token.text or token.similarity(nlp(keyword)) > 0.7:
                    matched = True
                    break
            if matched:
                break

        if matched:
            results.append({
                "Intervention": intervention_name,
                "IRC Code": row["irc_code"],
                "Clause": row["clause"],
                "Cost Level": row["cost_level"],
                "Estimated Cost (₹)": row["cost_estimate_in_inr"],
                "Keywords Matched": ', '.join(keywords)
            })

    return results
