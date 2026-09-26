import os
import pandas as pd
import json

_BASE = os.path.dirname(__file__)
_DATASET_PATH = os.path.join(_BASE, "student_career_with_domains.xlsx")
_REPRESENTATIVE_THRESHOLD = 0.90

_popularity_index = None


def _build_popularity_index():
    df = pd.read_excel(_DATASET_PATH)
    counts = df.groupby(["Career_Domain", "Chosen_Course"]).size().reset_index(name="count")
    max_per_domain = counts.groupby("Career_Domain")["count"].transform("max")
    counts["popularity"] = (counts["count"] / max_per_domain).round(4)
    counts["is_representative"] = counts["popularity"] >= _REPRESENTATIVE_THRESHOLD
    return counts


def get_popularity_index():
    global _popularity_index
    if _popularity_index is None:
        _popularity_index = _build_popularity_index()
    return _popularity_index


def get_top_courses_by_domain(domain_name, top_n=10):
    index = get_popularity_index()
    subset = index[index["Career_Domain"] == domain_name]
    return subset.sort_values("count", ascending=False).head(top_n).to_dict("records")


def _build_reasons(domain, popularity, is_representative):
    reasons = ["High {} domain probability".format(domain)]
    if is_representative:
        if popularity >= 1.0:
            reasons.append("One of the most common {} courses in the historical dataset".format(domain))
        else:
            reasons.append("Representative course within {} domain".format(domain))
    return reasons


def recommend_courses(domain_probabilities, top_n=5):
    index = get_popularity_index()
    scored = []

    for domain, prob_pct in domain_probabilities.items():
        if prob_pct <= 0:
            continue
        domain_courses = index[index["Career_Domain"] == domain]
        representative = domain_courses[domain_courses["is_representative"]]
        if representative.empty:
            representative = domain_courses.head(1)
        prob_dec = prob_pct / 100.0

        for _, row in representative.iterrows():
            score = round(prob_dec * row["popularity"] * 100, 2)
            if score > 0:
                scored.append({
                    "course": row["Chosen_Course"],
                    "domain": row["Career_Domain"],
                    "score": score,
                    "reason": _build_reasons(
                        row["Career_Domain"],
                        row["popularity"],
                        row["is_representative"],
                    ),
                })

    scored.sort(key=lambda x: x["score"], reverse=True)

    seen = set()
    unique = []
    for item in scored:
        if item["course"] not in seen:
            seen.add(item["course"])
            unique.append(item)
        if len(unique) >= top_n:
            break

    return unique


def recommend_from_prediction(prediction_result, top_n=5):
    ranking = prediction_result.get("Career_Readiness_Ranking", [])
    domain_probs = {entry["domain"]: entry["probability"] for entry in ranking}
    return recommend_courses(domain_probs, top_n=top_n)


if __name__ == "__main__":
    from predict import predict_domains, load_data

    print("=" * 60)
    print("RECOMMENDATION ENGINE TEST (TWO-STAGE RANKING)")
    print("=" * 60)

    print("\nRepresentative threshold: {}% of max popularity".format(_REPRESENTATIVE_THRESHOLD * 100))
    index = get_popularity_index()
    print("  Total domain-course pairs: {}".format(len(index)))
    print("  Domains: {}".format(index["Career_Domain"].nunique()))
    print("  Courses: {}".format(index["Chosen_Course"].nunique()))
    print("  Representative courses: {}".format(index["is_representative"].sum()))
    print("  Non-representative courses: {}".format((~index["is_representative"]).sum()))

    print("\nSample: Representative courses in Technology & Computing:")
    tech_repr = index[(index["Career_Domain"] == "Technology & Computing") & (index["is_representative"])]
    for _, c in tech_repr.sort_values("popularity", ascending=False).iterrows():
        print("  {:50s} popularity={:.4f}".format(c["Chosen_Course"], c["popularity"]))

    df = load_data()
    for idx in [0, 50, 200, 1000, 5000]:
        sample = df.iloc[idx].to_dict()
        print("\n" + "=" * 70)
        print("Student {} -- {}".format(idx, sample.get("Chosen_Course", "N/A")))
        print("=" * 70)
        pred = predict_domains(sample)
        print("Predicted: {} ({:.2f}%)".format(pred["Predicted_Domain"], pred["Prediction_Probability"]))
        recs = recommend_from_prediction(pred)
        print("\nTop {} Recommended Courses:".format(len(recs)))
        for rank, r in enumerate(recs, 1):
            print("  {}. {:50s} ({:35s}) score={:6.2f}".format(
                rank, r["course"], r["domain"], r["score"]))
            for line in r["reason"]:
                print("       {}".format(line))
