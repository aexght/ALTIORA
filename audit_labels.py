import os, json, warnings
import numpy as np
import pandas as pd
from collections import Counter, defaultdict
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

warnings.filterwarnings("ignore")

BASE = os.path.dirname(__file__)
REPORTS_DIR = os.path.join(BASE, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

IGNORE_COLS = ["Student_ID", "Satisfaction_Score"]
TARGET = "Chosen_Course"
CAT_COLS = ["Class12_Stream", "Subject_Combination"]
MARKS_COLS = [
    "Physics_Marks", "Chemistry_Marks", "Mathematics_Marks",
    "Biology_Marks", "Computer_Science_Marks", "Statistics_Marks",
    "Accountancy_Marks", "Economics_Marks", "Business_Studies_Marks", "English_Marks"
]
NUM_COLS = [
    "Class10_Percentage", "Class12_Percentage",
    "Logical_Score", "Analytical_Score",
    "Technical_Interest", "Business_Interest",
    "Creativity_Score", "Communication_Score",
    "Leadership_Score", "Research_Interest"
]
FEATURE_COLS = CAT_COLS + MARKS_COLS + NUM_COLS

print("Loading dataset...")
df = pd.read_excel(os.path.join(BASE, "student_career_synthetic_expanded_86000.xlsx"))
data = df.drop(columns=IGNORE_COLS, errors="ignore").copy()
print(f"Rows: {len(data)}, Features: {len(FEATURE_COLS)}, Classes: {data[TARGET].nunique()}")

# Fill NaN marks with 0
for c in MARKS_COLS:
    data[c] = data[c].fillna(0)

print("=" * 70)
print("ANALYSIS 1: EXACT DUPLICATE FEATURE VECTORS")
print("=" * 70)

dup_groups = data.groupby(FEATURE_COLS)[TARGET].apply(set)
dup_counts = data.groupby(FEATURE_COLS).size()
multi_label_mask = dup_groups.apply(len) > 1
multi_label = dup_groups[multi_label_mask]
total_exact_dupes = dup_counts[dup_counts > 1].sum()

print(f"\nTotal exact-duplicate groups (same features, multiple rows): {len(dup_counts[dup_counts > 1])}")
print(f"Total rows involved in exact duplicates: {int(total_exact_dupes)}")
print(f"Duplicate groups with DIFFERENT labels: {len(multi_label)}")

if len(multi_label) > 0:
    print(f"\nExamples of exact duplicates with different labels:")
    for idx, (feat_key, labels) in enumerate(list(multi_label.items())[:5]):
        label_str = ", ".join(sorted(labels))
        count = dup_counts[feat_key]
        print(f"  Group {idx+1}: {count} rows -> labels: {label_str}")
    print(f"\n  ... and {len(multi_label) - 5} more groups")

    # How many rows are affected by different-label duplicates?
    affected_rows = 0
    label_pairs = Counter()
    for feat_key, labels in multi_label.items():
        count = dup_counts[feat_key]
        affected_rows += count
        label_pairs[tuple(sorted(labels))] += 1
    print(f"\nTotal rows with conflicting labels: {affected_rows} ({affected_rows/len(data)*100:.2f}%)")
    print(f"Unique label-conflict patterns: {len(label_pairs)}")

# Also check: exact feature duplicates by stream
if len(multi_label) > 0:
    print(f"\nConflicts by stream:")
    for stream in data["Class12_Stream"].unique():
        stream_groups = data[data["Class12_Stream"] == stream].groupby(FEATURE_COLS)[TARGET].apply(set)
        stream_conflicts = stream_groups[stream_groups.apply(len) > 1]
        print(f"  {stream}: {len(stream_conflicts)} conflicting groups")
else:
    print("No exact duplicates with different labels found.")

print("\n" + "=" * 70)
print("ANALYSIS 2: LABEL AGREEMENT AMONG NEAREST NEIGHBORS")
print("=" * 70)

print("\nEncoding features for similarity search...")
# One-hot encode categoricals, scale numerics, keep marks as-is
cat_encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
cat_encoded = cat_encoder.fit_transform(data[CAT_COLS].astype(str))

scaler = StandardScaler()
num_scaled = scaler.fit_transform(data[NUM_COLS])

# Use feature matrix with cat + marks + num
marks = data[MARKS_COLS].values
feature_matrix = np.hstack([cat_encoded, marks, num_scaled])
print(f"Feature matrix shape: {feature_matrix.shape}")

# Sample for nearest neighbor analysis (too expensive for 86k x 86k)
np.random.seed(42)
sample_size = 10000
sample_idx = np.random.choice(len(data), sample_size, replace=False)
sample_features = feature_matrix[sample_idx]
sample_labels = data[TARGET].iloc[sample_idx].values

print(f"Finding 10 nearest neighbors for {sample_size} sampled students...")
nn = NearestNeighbors(n_neighbors=11, metric="cosine", n_jobs=1)
nn.fit(feature_matrix)
distances, indices = nn.kneighbors(sample_features)

# For each sample, check how many of its 10 nearest neighbors share the same label
agreement_rates = []
for i in range(sample_size):
    neighbor_labels = data[TARGET].iloc[indices[i, 1:]].values  # exclude self
    same_label_count = np.sum(neighbor_labels == sample_labels[i])
    agreement_rates.append(same_label_count / 10)

agreement_rates = np.array(agreement_rates)
print(f"\nLabel Agreement with 10 Nearest Neighbors:")
print(f"  Mean agreement: {agreement_rates.mean()*100:.2f}%")
print(f"  Median agreement: {np.median(agreement_rates)*100:.2f}%")
print(f"  Std dev: {agreement_rates.std()*100:.2f}%")
print(f"  % samples with 0/10 same label: {(agreement_rates == 0).mean()*100:.2f}%")
print(f"  % samples with 10/10 same label: {(agreement_rates == 1).mean()*100:.2f}%")

# Distribution
print(f"\n  Agreement distribution:")
for bin_start in np.arange(0, 1.1, 0.1):
    if bin_start < 1:
        pct = ((agreement_rates >= bin_start) & (agreement_rates < bin_start + 0.1)).mean() * 100
        print(f"    {bin_start*100:.0f}-{bin_start*100+10:.0f}%: {pct:.2f}%")
    else:
        pct = (agreement_rates == 1).mean() * 100
        print(f"    100%:        {pct:.2f}%")

print("\n" + "=" * 70)
print("ANALYSIS 3: CLUSTER ANALYSIS")
print("=" * 70)

# For computational efficiency, use a sample and fewer clusters
cluster_sample_size = 20000
np.random.seed(42)
cs_idx = np.random.choice(len(data), cluster_sample_size, replace=False)
cs_features = feature_matrix[cs_idx]
cs_labels = data[TARGET].iloc[cs_idx].values

# Use KMeans with k=50 (roughly 400 samples per cluster on average)
print(f"\nClustering {cluster_sample_size} samples into 50 clusters...")
kmeans = KMeans(n_clusters=50, random_state=42, n_init="auto")
cluster_ids = kmeans.fit_predict(cs_features)

sil_score = silhouette_score(cs_features, cluster_ids)
print(f"Silhouette score: {sil_score:.4f}")

# Analyze cluster purity
cluster_label_distributions = {}
cluster_purities = []
for cid in range(50):
    mask = cluster_ids == cid
    cluster_labels = cs_labels[mask]
    label_counts = Counter(cluster_labels)
    total = len(cluster_labels)
    most_common = label_counts.most_common(1)[0]
    purity = most_common[1] / total
    unique_count = len(label_counts)
    cluster_label_distributions[cid] = {
        "size": int(total),
        "purity": float(round(purity, 4)),
        "unique_labels": int(unique_count),
        "top_label": str(most_common[0]),
        "top_pct": round(most_common[1] / total * 100, 1),
    }
    cluster_purities.append(purity)

cluster_purities = np.array(cluster_purities)
print(f"\nCluster Purity Metrics:")
print(f"  Mean cluster purity: {cluster_purities.mean()*100:.2f}%")
print(f"  Median cluster purity: {np.median(cluster_purities)*100:.2f}%")
print(f"  Min cluster purity: {cluster_purities.min()*100:.2f}%")
print(f"  Max cluster purity: {cluster_purities.max()*100:.2f}%")

# Distribution of unique labels per cluster
uniq_per_cluster = np.array([v["unique_labels"] for v in cluster_label_distributions.values()])
print(f"\n  Unique labels per cluster:")
print(f"    Mean: {uniq_per_cluster.mean():.1f}")
print(f"    Median: {np.median(uniq_per_cluster):.1f}")
print(f"    Min: {uniq_per_cluster.min()}")
print(f"    Max: {uniq_per_cluster.max()}")

print(f"\n  Bottom 5 clusters (lowest purity):")
sorted_clusters = sorted(cluster_label_distributions.values(), key=lambda x: x["purity"])
for c in sorted_clusters[:5]:
    print(f"    Size={c['size']:4d}, Purity={c['purity']*100:5.2f}%, "
          f"Unique={c['unique_labels']:2d}, Top={c['top_label'][:35]} ({c['top_pct']}%)")

print(f"\n  Top 5 clusters (highest purity):")
for c in sorted_clusters[-5:]:
    print(f"    Size={c['size']:4d}, Purity={c['purity']*100:5.2f}%, "
          f"Unique={c['unique_labels']:2d}, Top={c['top_label'][:35]} ({c['top_pct']}%)")

print("\n" + "=" * 70)
print("ANALYSIS 4: STREAM / SUBJECT COMBINATION CONSISTENCY")
print("=" * 70)

print("\nFor each stream + subject combination, checking assigned courses:")

# Define expected course categories per stream
science_expected_prefixes = [
    "B.Sc", "B.Tech", "MBBS", "BDS", "BAMS", "BHMS", "B.Pharm", "D.Pharm", "Pharm.D",
    "BPT", "BOT", "BASLP", "BUMS", "B.Des", "General Nursing", "BCA"
]
commerce_expected_prefixes = [
    "B.Com", "BBA", "BCA", "Bachelor of", "CA ", "CMA ", "Company Secretary",
    "B.Sc Economics", "B.Sc Finance", "B.Sc Statistics", "B.Sc Actuarial",
    "BMS", "B.Sc Mathematics", "BA LLB", "BBA LLB", "B.Com LLB"
]

stream_subject_groups = data.groupby(["Class12_Stream", "Subject_Combination", TARGET]).size().reset_index(name="count")
stream_subject_groups = stream_subject_groups.sort_values(["Class12_Stream", "Subject_Combination", "count"], ascending=[True, True, False])

for (stream, subj), group_df in stream_subject_groups.groupby(["Class12_Stream", "Subject_Combination"]):
    total = group_df["count"].sum()
    top_courses = group_df.head(8)
    top_pct = (top_courses["count"].sum() / total * 100)
    course_list = ", ".join([f"{r['Chosen_Course']} ({r['count']/total*100:.0f}%)"
                            for _, r in top_courses.iterrows()])
    print(f"\n  {stream} / {subj} ({total} students)")
    print(f"    Top courses ({top_pct:.0f}% of students): {course_list}")

    # Check for logical inconsistencies
    if stream == "Science":
        unexpected = []
        for _, r in group_df.iterrows():
            course = r["Chosen_Course"]
            if not any(course.startswith(pre) for pre in science_expected_prefixes):
                unexpected.append(course)
        if unexpected:
            print(f"    POTENTIAL ISSUES: {len(unexpected)} unusual courses for Science stream")
            for c in unexpected[:3]:
                count = group_df[group_df[TARGET] == c]["count"].values[0]
                print(f"      - {c} ({count} students)")
    elif stream == "Commerce":
        unexpected = []
        for _, r in group_df.iterrows():
            course = r["Chosen_Course"]
            if not any(course.startswith(pre) for pre in commerce_expected_prefixes):
                unexpected.append(course)
        if unexpected:
            print(f"    POTENTIAL ISSUES: {len(unexpected)} unusual courses for Commerce stream")
            for c in unexpected[:3]:
                count = group_df[group_df[TARGET] == c]["count"].values[0]
                print(f"      - {c} ({count} students)")

# Further check: mean marks by stream for overlapping courses
print(f"\n  --- Cross-stream course overlap analysis ---")
science_students = data[data["Class12_Stream"] == "Science"][TARGET].unique()
commerce_students = data[data["Class12_Stream"] == "Commerce"][TARGET].unique()
overlap = set(science_students) & set(commerce_students)
print(f"  Courses taken by BOTH Science and Commerce students: {len(overlap)}")
if len(overlap) > 0:
    for course in sorted(list(overlap))[:10]:
        sci = data[(data["Class12_Stream"] == "Science") & (data[TARGET] == course)]
        com = data[(data["Class12_Stream"] == "Commerce") & (data[TARGET] == course)]
        print(f"    {course}: Science={len(sci)}, Commerce={len(com)}")
    if len(overlap) > 10:
        print(f"    ... and {len(overlap)-10} more")

print(f"\n  --- Expected vs actual enrollment by stream ---")
for stream in ["Science", "Commerce"]:
    stream_data = data[data["Class12_Stream"] == stream]
    top5 = stream_data[TARGET].value_counts().head(5)
    print(f"\n  {stream} Top-5 enrollments:")
    for course, count in top5.items():
        pct = count / len(stream_data) * 100
        print(f"    {course}: {count} ({pct:.1f}%)")

print("\n" + "=" * 70)
print("ANALYSIS 5: UPPER BOUND ACCURACY ESTIMATE")
print("=" * 70)

# Estimate the maximum possible accuracy given label ambiguity
# Use nearest neighbor consistency as a proxy for label noise
# If 10 nearest neighbors only agree X% of the time, then X% is roughly
# the upper bound for any model's accuracy on this data
nn_upper_bound = np.mean(agreement_rates) * 100
print(f"\nMethod: Nearest-neighbor label consistency (10 neighbors)")
print(f"Estimated upper-bound accuracy: {nn_upper_bound:.2f}%")
print(f"Interpretation: If even the 10 most similar students only share")
print(f"the same label {nn_upper_bound:.1f}% of the time, then the maximum")
print(f"achievable classification accuracy is roughly {nn_upper_bound:.1f}%.")
print(f"This suggests inherent label noise/ambiguity of ~{100-nn_upper_bound:.1f}%.")

# Also estimate using cluster purity
cluster_upper_bound = np.mean(cluster_purities) * 100
print(f"\nMethod: KMeans cluster purity (50 clusters)")
print(f"Estimated upper-bound accuracy: {cluster_upper_bound:.2f}%")

# If exact duplicates with different labels exist
if len(multi_label) > 0:
    conflict_pct = affected_rows / len(data) * 100
    print(f"\nMethod: Exact feature duplicate conflict rate")
    print(f"Rows with identical features but different labels: {conflict_pct:.2f}%")
    print(f"This is a direct measure of irreducible label noise.")

print(f"\n--- LABEL CONSISTENCY REPORT SUMMARY ---")
summary = {
    "total_rows": len(data),
    "total_classes": data[TARGET].nunique(),
    "exact_duplicate_groups": int(len(dup_counts[dup_counts > 1])),
    "rows_in_duplicates": int(total_exact_dupes),
    "conflicting_duplicate_groups": int(len(multi_label)),
    "rows_with_conflicting_labels": int(affected_rows) if len(multi_label) > 0 else 0,
    "nn_label_agreement_mean_pct": round(float(agreement_rates.mean() * 100), 2),
    "nn_label_agreement_median_pct": round(float(np.median(agreement_rates) * 100), 2),
    "cluster_purity_mean_pct": round(float(cluster_purities.mean() * 100), 2),
    "silhouette_score": round(float(sil_score), 4),
    "upper_bound_accuracy_nn_pct": round(nn_upper_bound, 2),
    "upper_bound_accuracy_cluster_pct": round(cluster_upper_bound, 2),
    "overlapping_courses_between_streams": len(overlap),
}

summary_path = os.path.join(REPORTS_DIR, "label_consistency_report.json")
with open(summary_path, "w") as f:
    json.dump(summary, f, indent=2)
print(f"\nSummary saved to {summary_path}")
print("\nLabel audit complete.")
