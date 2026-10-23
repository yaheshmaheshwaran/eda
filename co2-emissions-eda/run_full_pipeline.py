"""
=============================================================================
KPR INSTITUTE OF ENGINEERING AND TECHNOLOGY
Department of Artificial Intelligence and Data Science
Course: U21ADP05 – Exploratory Data Analysis and Visualization | Assignment II
Student: Yahesh M | Repository: https://github.com/yaheshmaheshwaran/eda

CASE STUDY:
Exploratory Data Analysis, Statistical Visualization, and Deep Neural
Network Classification of National Carbon Emission Trajectories
=============================================================================
"""

import os, copy, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.inspection import permutation_importance
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, roc_curve,
                             confusion_matrix, log_loss)

warnings.filterwarnings("ignore")
SEED = 42
np.random.seed(SEED)

os.makedirs("figures", exist_ok=True)
os.makedirs("dataset", exist_ok=True)
os.makedirs("co2-emissions-eda/visualizations", exist_ok=True)
os.makedirs("co2-emissions-eda/figures", exist_ok=True)

sns.set_style("whitegrid")
PAL = {"Low": "#2B5F91", "High": "#D95F02"}

# ===========================================================================
# STAGES 1-2: ACQUIRE & PARSE
# ===========================================================================
print("="*70)
print("STAGE 1 & 2: ACQUIRE & PARSE")
print("="*70)

DATA_PATH = "dataset/owid_co2_data.csv"
df = pd.read_csv(DATA_PATH)
print(f"Loaded benchmark dataset: {df.shape[0]:,} rows x {df.shape[1]} columns")

# Target Formulation: High Carbon Intensity Trajectory (1 = High, 0 = Low/Moderate)
# Global benchmark threshold = 5.0 t CO2/person
THRESHOLD = 5.0
df['Emission_Class'] = np.where(df['co2_per_capita'] >= THRESHOLD, "High", "Low")
df['Target_Binary'] = (df['Emission_Class'] == "High").astype(int)

# Check class balance
counts = df['Emission_Class'].value_counts()
print(f"Target Distribution:\n{counts}")
print(f"Percentages:\n{(counts / len(df) * 100).round(2)}")

# ===========================================================================
# STAGE 3: FILTER / DATA QUALITY & IQR OUTLIER DETECTION
# ===========================================================================
print("\n" + "="*70)
print("STAGE 3: FILTER & DATA QUALITY AUDIT")
print("="*70)

print(f"Duplicate rows: {df.duplicated().sum()}")
cont_cols = ["co2", "co2_per_capita", "gdp_per_capita", "coal_co2", "oil_co2", "gas_co2"]

print("\n--- Outlier Detection via Tukey IQR Fences ---")
for c in cont_cols:
    q1, q3 = df[c].quantile([0.25, 0.75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    n_out = ((df[c] < lo) | (df[c] > hi)).sum()
    pct_out = (n_out / len(df)) * 100
    print(f"{c:16s} | IQR: {iqr:8.2f} | Bounds: [{lo:8.2f}, {hi:8.2f}] | Outliers: {n_out:4d} ({pct_out:5.2f}%)")

# Descriptive moments
summary = df[cont_cols].describe().T
summary["skewness"] = df[cont_cols].skew()
summary["kurtosis"] = df[cont_cols].kurt()
print("\nDescriptive Summary of Continuous Variables:")
print(summary.round(2))

# ===========================================================================
# PREPROCESSING & STRATIFIED SPLIT
# ===========================================================================
feature_cols = [
    'gdp_per_capita', 'population', 'coal_co2', 'oil_co2', 'gas_co2',
    'cement_co2', 'flaring_co2', 'share_global_co2', 'cumulative_co2',
    'year', 'Region'
]

X_raw = df[feature_cols].copy()
X = pd.get_dummies(X_raw, columns=['Region'], drop_first=True).astype(float)
y = df['Target_Binary'].values

print(f"\nModel input dimensions: {X.shape[1]} features")

# Stratified 70 / 15 / 15 Train/Validation/Test Split
X_tmp, X_test, y_tmp, y_test = train_test_split(
    X, y, test_size=0.15, stratify=y, random_state=SEED
)
X_train, X_val, y_train, y_val = train_test_split(
    X_tmp, y_tmp, test_size=0.15 / 0.85, stratify=y_tmp, random_state=SEED
)

print(f"Training partition  : {len(X_train)} rows | Low: {np.sum(y_train == 0)} | High: {np.sum(y_train == 1)}")
print(f"Validation partition: {len(X_val)} rows | Low: {np.sum(y_val == 0)} | High: {np.sum(y_val == 1)}")
print(f"Testing partition   : {len(X_test)} rows | Low: {np.sum(y_test == 0)} | High: {np.sum(y_test == 1)}")

scaler = StandardScaler()
scale_cols = [c for c in X.columns if not c.startswith('Region_')]

X_train_sc = X_train.copy()
X_val_sc = X_val.copy()
X_test_sc = X_test.copy()

X_train_sc[scale_cols] = scaler.fit_transform(X_train[scale_cols])
X_val_sc[scale_cols] = scaler.transform(X_val[scale_cols])
X_test_sc[scale_cols] = scaler.transform(X_test[scale_cols])

# ===========================================================================
# STAGES 5-7: DATA VISUALIZATIONS (FIGURES 1-6)
# ===========================================================================
print("\n" + "="*70)
print("GENERATING EXPLORATORY FIGURES (FIG 1-6)")
print("="*70)

# Figure 1: Discrete Probability Distribution
fig, ax = plt.subplots(1, 2, figsize=(12, 5))
ax[0].bar(["Low/Moderate (No)", "High Carbon (Yes)"], [counts["Low"], counts["High"]],
          color=[PAL["Low"], PAL["High"]], edgecolor="black")
for i, v in enumerate([counts["Low"], counts["High"]]):
    ax[0].text(i, v / 2, f"{v:,}\n({v / len(df):.1%})", ha="center",
               color="white", fontweight="bold", fontsize=11)
ax[0].set(title="Discrete Emission Trajectory Distribution", ylabel="Country-Year Count")

ax[1].pie([counts["Low"], counts["High"]], labels=["Low/Moderate (No)", "High Carbon (Yes)"],
          colors=[PAL["Low"], PAL["High"]], autopct="%1.1f%%", startangle=90,
          pctdistance=0.8, wedgeprops=dict(width=0.4, edgecolor="black"))
ax[1].set_title("Proportion of High vs Moderate Carbon Intensity")
fig.suptitle("Target Class Distribution Analysis", fontweight="bold", fontsize=14)
fig.savefig("figures/01_target_distribution.png", dpi=300, bbox_inches="tight")
plt.close(fig)
print("✔ Figure 1 saved.")

# Figure 2: Continuous Probability Distributions (KDE + Histograms)
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
plot_cont_cols = ["co2_per_capita", "gdp_per_capita", "co2"]
plot_colors = ["#1f77b4", "#2ca02c", "#9467bd"]

for ax, c, col in zip(axes, plot_cont_cols, plot_colors):
    val_clip = df[c].clip(upper=df[c].quantile(0.98))
    sns.histplot(val_clip, bins=30, stat="density", kde=True, color=col, ax=ax)
    ax.axvline(val_clip.mean(), color="red", ls="--", label=f"Mean: {val_clip.mean():.1f}")
    ax.axvline(val_clip.median(), color="navy", ls=":", label=f"Median: {val_clip.median():.1f}")
    ax.set_title(f"{c}\nSkewness: {df[c].skew():.2f} | Kurtosis: {df[c].kurt():.2f}", fontweight="bold")
    ax.legend()
fig.suptitle("Continuous Probability Density Functions (KDE & Histograms)", fontweight="bold", fontsize=14)
fig.savefig("figures/02_univariate_continuous_kde.png", dpi=300, bbox_inches="tight")
plt.close(fig)
print("✔ Figure 2 saved.")

# Figure 3: Bivariate Boxplots with Mann-Whitney U Hypothesis Tests
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
for ax, c in zip(axes, plot_cont_cols):
    a = df.loc[df["Emission_Class"] == "Low", c]
    b = df.loc[df["Emission_Class"] == "High", c]
    p_val = stats.mannwhitneyu(a, b, alternative="two-sided").pvalue
    sns.boxplot(data=df, x="Emission_Class", y=c, palette=PAL, ax=ax, width=0.5, showfliers=False)
    ax.set_title(f"{c} by Emission Class\nMW-U p-value: {p_val:.2e}", fontweight="bold")
    ax.text(0.5, 0.92, f"Median Low: {a.median():.1f}\nMedian High: {b.median():.1f}",
            transform=ax.transAxes, ha="center", va="top",
            bbox=dict(boxstyle="round", fc="lightyellow"))
fig.suptitle("Bivariate Boxplots with Non-Parametric Mann-Whitney U Hypothesis Tests", fontweight="bold", fontsize=14)
fig.savefig("figures/03_bivariate_boxplots.png", dpi=300, bbox_inches="tight")
plt.close(fig)
print("✔ Figure 3 saved.")

# Figure 4: Geographic Region vs Emission Class (Chi-Square Test)
ct = pd.crosstab(df["Region"], df["Emission_Class"])
chi2, p_chi, dof, _ = stats.chi2_contingency(ct)
pct = ct.div(ct.sum(axis=1), axis=0) * 100

fig, ax = plt.subplots(1, 2, figsize=(16, 5))
ct.plot(kind="bar", color=[PAL["Low"], PAL["High"]], edgecolor="black", rot=15, ax=ax[0])
ax[0].set(title="Observations by Geographic Region and Carbon Class", ylabel="Country-Year Count")

pct.plot(kind="bar", stacked=True, color=[PAL["Low"], PAL["High"]], edgecolor="black", rot=15, ax=ax[1])
ax[1].set(title=f"Carbon Intensity Rate per Region\nChi-Square: {chi2:.1f} (p = {p_chi:.1e})", ylabel="Percentage (%)")
for i, v in enumerate(pct["High"]):
    ax[1].text(i, 50, f"High: {v:.1f}%", ha="center", color="white", fontweight="bold")
fig.suptitle("Geographic Region Dependency and Carbon Transition Risk (Chi-Square Test)", fontweight="bold", fontsize=14)
fig.savefig("figures/04_contract_churn_mosaic.png", dpi=300, bbox_inches="tight")
plt.close(fig)
print("✔ Figure 4 saved.")

# Figure 5: Multivariate Pearson Correlation Matrix (Lower-triangle)
corr_cols = [
    'gdp_per_capita', 'population', 'coal_co2', 'oil_co2', 'gas_co2',
    'cement_co2', 'flaring_co2', 'share_global_co2', 'cumulative_co2', 'Target_Binary'
]
corr_df = df[corr_cols].copy()
corr_df.rename(columns={'Target_Binary': 'High Carbon (Target)'}, inplace=True)
corr = corr_df.corr()
mask = np.triu(np.ones_like(corr, dtype=bool))

plt.figure(figsize=(11, 9))
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", vmin=-0.8, vmax=0.8,
            cmap=sns.diverging_palette(220, 10, as_cmap=True), linewidths=0.5,
            cbar_kws={"shrink": 0.7})
plt.title("Multivariate Pearson Correlation Matrix", fontweight="bold", fontsize=14)
plt.grid(False)
plt.savefig("figures/05_correlation_heatmap.png", dpi=300, bbox_inches="tight")
plt.close()
print("✔ Figure 5 saved.")

# Figure 6: Multivariate Feature Space Pairplot
pair_df = df[['co2_per_capita', 'gdp_per_capita', 'oil_co2', 'Emission_Class']].copy()
pair_df['co2_per_capita'] = pair_df['co2_per_capita'].clip(upper=pair_df['co2_per_capita'].quantile(0.97))
pair_df['gdp_per_capita'] = pair_df['gdp_per_capita'].clip(upper=pair_df['gdp_per_capita'].quantile(0.97))
pair_df['oil_co2'] = pair_df['oil_co2'].clip(upper=pair_df['oil_co2'].quantile(0.97))

g = sns.pairplot(pair_df, hue="Emission_Class", palette=PAL, corner=True,
                 diag_kind="kde", plot_kws={"alpha": 0.4, "s": 15})
g.figure.suptitle("Multivariate Pairwise Interactions and Carbon Class Separation", y=1.02, fontweight="bold", fontsize=14)
g.savefig("figures/06_pairplot_multivariate.png", dpi=300, bbox_inches="tight")
plt.close("all")
print("✔ Figure 6 saved.")

# ===========================================================================
# DEEP LEARNING: MULTI-LAYER PERCEPTRON (MLP) + TUNING (CO5)
# ===========================================================================
print("\n" + "="*70)
print("DEEP LEARNING MODEL BUILDING & HYPERPARAMETER TUNING (CO5)")
print("="*70)

def train_mlp(hidden, lr, alpha, epochs=30):
    mlp = MLPClassifier(hidden_layer_sizes=hidden, activation="relu", solver="adam",
                        alpha=alpha, learning_rate_init=lr, batch_size=64,
                        random_state=SEED)
    hist = {"loss": [], "val_loss": [], "acc": [], "val_acc": [], "val_auc": []}
    best_val, best_model, best_epoch = np.inf, None, 0
    for ep in range(1, epochs + 1):
        mlp.partial_fit(X_train_sc, y_train, classes=np.array([0, 1]))
        p_tr = mlp.predict_proba(X_train_sc)[:, 1]
        p_va = mlp.predict_proba(X_val_sc)[:, 1]
        hist["loss"].append(log_loss(y_train, p_tr))
        hist["val_loss"].append(log_loss(y_val, p_va))
        hist["acc"].append(100 * accuracy_score(y_train, p_tr >= 0.5))
        hist["val_acc"].append(100 * accuracy_score(y_val, p_va >= 0.5))
        hist["val_auc"].append(roc_auc_score(y_val, p_va))
        if hist["val_loss"][-1] < best_val:
            best_val, best_model, best_epoch = hist["val_loss"][-1], copy.deepcopy(mlp), ep
    return best_model, hist, best_epoch

configs = {
    "Config A (Shallow Fast)": ((64, 32), 0.005, 0.001),
    "Config B (Tuned Deep MLP) ★": ((64, 32, 16), 0.001, 0.0001),
    "Config C (Wide Deep MLP)": ((128, 64, 32), 0.0005, 0.0005),
}

rows, fitted = [], {}
for name, (hidden, lr, alpha) in configs.items():
    model, hist, best_ep = train_mlp(hidden, lr, alpha)
    n_params = (sum(w.size for w in model.coefs_) + sum(b.size for b in model.intercepts_))
    rows.append({
        "Configuration": name, "Hidden Layers": str(hidden), "Learning Rate": lr, "L2 Penalty (α)": alpha,
        "Best Val Loss": min(hist["val_loss"]),
        "Best Val AUC": hist["val_auc"][best_ep - 1],
        "Val Acc. (%)": hist["val_acc"][best_ep - 1],
        "Best Epoch": best_ep, "Params": n_params
    })
    fitted[name] = (model, hist, best_ep)

df_tuning = pd.DataFrame(rows)
print("\nHyperparameter Grid Results (Table 6):")
print(df_tuning.round(4).to_string(index=False))

# Selected production model: Config B
mlp, hist, best_ep = fitted["Config B (Tuned Deep MLP) ★"]
epochs = range(1, len(hist["loss"]) + 1)

# Figure 7: Training & Validation Loss vs Epoch Trajectory
plt.figure(figsize=(8, 5))
plt.plot(epochs, hist["loss"], "o-", label="Training Loss (BCE)")
plt.plot(epochs, hist["val_loss"], "s--", color="#D95F02", label="Validation Loss (BCE)")
plt.axvline(best_ep, color="green", ls=":", label=f"Optimal Epoch ({best_ep})")
plt.xlabel("Epoch Number")
plt.ylabel("Binary Cross-Entropy Loss")
plt.title("Step 5.1: Deep Learning Training & Validation Loss vs Epoch", fontweight="bold", pad=12)
plt.legend()
plt.savefig("figures/07_dl_loss_curve.png", dpi=300, bbox_inches="tight")
plt.close()
print("✔ Figure 7 saved.")

# Figure 8: Training & Validation Accuracy vs Epoch Trajectory
plt.figure(figsize=(8, 5))
plt.plot(epochs, hist["acc"], "o-", label="Training Accuracy (%)")
plt.plot(epochs, hist["val_acc"], "^--", color="green", label="Validation Accuracy (%)")
plt.xlabel("Epoch Number")
plt.ylabel("Classification Accuracy (%)")
plt.title("Step 5.2: Deep Learning Training & Validation Accuracy vs Epoch", fontweight="bold", pad=12)
plt.legend()
plt.savefig("figures/08_dl_accuracy_curve.png", dpi=300, bbox_inches="tight")
plt.close()
print("✔ Figure 8 saved.")

# ===========================================================================
# EVALUATION, BASELINE COMPARISON & FEATURE IMPORTANCE
# ===========================================================================
def report(y_true, prob):
    pred = (prob >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred).ravel()
    return {
        "Overall Accuracy": f"{accuracy_score(y_true, pred) * 100:.2f}%",
        "Precision (Positive)": f"{precision_score(y_true, pred) * 100:.2f}%",
        "Recall / Sensitivity": f"{recall_score(y_true, pred) * 100:.2f}%",
        "Specificity (True Negative)": f"{(tn / (tn + fp)) * 100:.2f}%",
        "F1-Score": f"{f1_score(y_true, pred):.4f}",
        "ROC-AUC Score": f"{roc_auc_score(y_true, prob):.4f}"
    }, (tn, fp, fn, tp)

prob_mlp = mlp.predict_proba(X_test_sc)[:, 1]

# Regularized Logistic Regression Baseline
base = LogisticRegression(C=1.0, class_weight="balanced", max_iter=2000, random_state=SEED)
base.fit(X_train_sc, y_train)
prob_lr = base.predict_proba(X_test_sc)[:, 1]

m_mlp, (tn, fp, fn, tp) = report(y_test, prob_mlp)
m_lr, _ = report(y_test, prob_lr)

bench_df = pd.DataFrame({"Deep Learning MLP": m_mlp, "Logistic Regression Baseline": m_lr})
print("\nTest Benchmark Table (Table 8):")
print(bench_df)

# Figure 9: Confusion Matrix
cm = np.array([[tn, fp], [fn, tp]])
cm_pct = cm / cm.sum(axis=1, keepdims=True) * 100
labels = np.array([
    [f"{cm[i, j]}\n({cm_pct[i, j]:.1f}%)\n[{t}]" for j, t in enumerate(row)]
    for i, row in enumerate([["TN", "FP"], ["FN", "TP"]])
])

plt.figure(figsize=(7, 6))
sns.heatmap(cm_pct, annot=labels, fmt="", cmap="Blues", cbar=False, linewidths=2,
            linecolor="gray", xticklabels=["Low/Mod (0)", "High Carbon (1)"],
            yticklabels=["Low/Mod (0)", "High Carbon (1)"], annot_kws={"fontweight": "bold", "size": 11})
plt.xlabel("Predicted Label", fontweight="bold")
plt.ylabel("True Label", fontweight="bold")
plt.title(f"Step 5.3: Test Set Confusion Matrix (n = {len(y_test):,})", fontweight="bold")
plt.savefig("figures/09_confusion_matrix.png", dpi=300, bbox_inches="tight")
plt.close()
print("✔ Figure 9 saved.")

# Figure 10: ROC Curves
plt.figure(figsize=(8, 6))
for prob, lab, st, col in [
    (prob_mlp, "Deep Learning MLP", "-", "#D95F02"),
    (prob_lr, "Logistic Regression Baseline", "--", "#1f77b4")
]:
    fpr, tpr, _ = roc_curve(y_test, prob)
    plt.plot(fpr, tpr, st, color=col, lw=2.5, label=f"{lab} (AUC = {roc_auc_score(y_test, prob):.4f})")
plt.plot([0, 1], [0, 1], ":", color="gray", label="Random Chance (AUC = 0.500)")
plt.xlabel("False Positive Rate (1 - Specificity)")
plt.ylabel("True Positive Rate (Sensitivity / Recall)")
plt.title("Step 5.4: Receiver Operating Characteristic (ROC) & AUC Comparison", fontweight="bold")
plt.legend(loc="lower right")
plt.savefig("figures/10_roc_auc_curve.png", dpi=300, bbox_inches="tight")
plt.close()
print("✔ Figure 10 saved.")

# Permutation Feature Importance
pi = permutation_importance(mlp, X_test_sc, y_test, scoring="roc_auc", n_repeats=5, random_state=SEED)
imp = (pd.DataFrame({
    "Feature Name": X.columns,
    "Test ROC-AUC Drop (Importance)": pi.importances_mean,
    "Standard Deviation": pi.importances_std
}).sort_values("Test ROC-AUC Drop (Importance)", ascending=False).head(10))

print("\nTop-10 Permutation Feature Importances (Table 7):")
print(imp.round(5).to_string(index=False))

# Copy generated figures into co2-emissions-eda folders
import shutil
for f in os.listdir("figures"):
    if f.endswith(".png"):
        shutil.copy(os.path.join("figures", f), os.path.join("co2-emissions-eda/visualizations", f))
        shutil.copy(os.path.join("figures", f), os.path.join("co2-emissions-eda/figures", f))

print("\n=============================================================================")
print("ALL PIPELINE COMPUTATIONS AND 10 FIGURES COMPLETED SUCCESSFULLY!")
print("=============================================================================")
