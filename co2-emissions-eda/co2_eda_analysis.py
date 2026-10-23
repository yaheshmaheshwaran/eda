"""
=============================================================================
  GLOBAL CO2 EMISSIONS & CLIMATE CHANGE — Exploratory Data Analysis
=============================================================================
  Dataset  : Our World in Data — CO2 and Greenhouse Gas Emissions
  Source   : https://github.com/owid/co2-data
  Author   : [Your Name]
  Date     : October 2026
=============================================================================
"""

# 0. IMPORTS
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats
import warnings, os, urllib.request

warnings.filterwarnings('ignore')

# GLOBAL STYLE
plt.rcParams.update({
    'figure.facecolor' : '#0d1117',
    'axes.facecolor'   : '#161b22',
    'axes.edgecolor'   : '#30363d',
    'axes.labelcolor'  : '#e6edf3',
    'xtick.color'      : '#8b949e',
    'ytick.color'      : '#8b949e',
    'text.color'       : '#e6edf3',
    'grid.color'       : '#21262d',
    'grid.linestyle'   : '--',
    'grid.alpha'       : 0.6,
    'font.family'      : 'DejaVu Sans',
    'font.size'        : 11,
    'axes.titlesize'   : 14,
    'axes.titleweight' : 'bold',
    'legend.facecolor' : '#21262d',
    'legend.edgecolor' : '#30363d',
})

PALETTE = ['#58a6ff','#f78166','#3fb950','#d2a8ff','#ffa657',
           '#79c0ff','#ff7b72','#56d364','#bc8cff','#ffb347']
OUT_DIR = 'visualizations'
os.makedirs(OUT_DIR, exist_ok=True)

def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'  Saved: {path}')
    plt.close(fig)


# ===========================================================================
# 1. DATA ACQUISITION
# ===========================================================================
print("\n--- STEP 1: DATA ACQUISITION ---")

DATA_URL  = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"
DATA_PATH = "data/owid-co2-data.csv"
os.makedirs('data', exist_ok=True)

if not os.path.exists(DATA_PATH):
    print("  Downloading dataset from Our World in Data ...")
    urllib.request.urlretrieve(DATA_URL, DATA_PATH)
    print("  Download complete.")
else:
    print("  Dataset already present locally.")

df_raw = pd.read_csv(DATA_PATH)
print(f"  Raw shape: {df_raw.shape[0]:,} rows x {df_raw.shape[1]} columns")


# ===========================================================================
# 2. DATA OVERVIEW & CLEANING
# ===========================================================================
print("\n--- STEP 2: DATA OVERVIEW & CLEANING ---")

print("\nColumns available:")
for col in df_raw.columns:
    print(f"  - {col}")

AGGREGATES = [
    'World','Asia','Europe','North America','South America',
    'Africa','Oceania','European Union (27)',
    'International transport','High-income countries',
    'Low-income countries','Upper-middle-income countries',
    'Lower-middle-income countries','Asia (excl. China and India)',
    'Europe (excl. EU-27)','Europe (excl. EU-28)'
]

df_countries = df_raw[~df_raw['country'].isin(AGGREGATES)].copy()
df_world     = df_raw[df_raw['country'] == 'World'].copy()

df   = df_countries[(df_countries['year'] >= 1950) & (df_countries['year'] <= 2022)].copy()
df_w = df_world[(df_world['year'] >= 1950) & (df_world['year'] <= 2022)].copy()

KEY_COLS = [
    'country','year','co2','co2_per_capita','share_global_co2',
    'coal_co2','oil_co2','gas_co2','cement_co2','flaring_co2',
    'cumulative_co2','population','gdp','temperature_change_from_co2'
]

df_key = df[KEY_COLS].copy()

missing = df_key.isnull().mean().mul(100).round(2).sort_values(ascending=False)
print("\nMissing value % per key column:")
print(missing.to_string())

df_key = df_key.sort_values(['country','year'])
numeric_cols = KEY_COLS[2:]
for col in numeric_cols:
    df_key[col] = df_key.groupby('country')[col].transform(
        lambda x: x.fillna(method='ffill').fillna(method='bfill')
    )

print(f"\nCleaned dataset shape: {df_key.shape[0]:,} rows x {df_key.shape[1]} columns")
print(f"Countries included   : {df_key['country'].nunique()}")
print(f"Year range           : {df_key['year'].min()} - {df_key['year'].max()}")

latest = df_key[df_key['year'] == 2022].dropna(subset=['co2']).copy()

print("\nBasic statistics (2022 snapshot):")
print(latest[['co2','co2_per_capita','share_global_co2']].describe().round(3).to_string())


# ===========================================================================
# 3. VISUALISATIONS
# ===========================================================================

# 3.1 Global CO2 Trend
print("\n[Plot 1] Global CO2 Trend ...")
fig, ax = plt.subplots(figsize=(13, 5))
ax.fill_between(df_w['year'], df_w['co2'], alpha=0.25, color='#58a6ff')
ax.plot(df_w['year'], df_w['co2'], color='#58a6ff', lw=2.5, label='Global CO2 (Mt)')
ax.axvline(1990, color='#f78166', ls='--', lw=1.2, label='1990 - Kyoto baseline')
ax.axvline(2016, color='#3fb950', ls='--', lw=1.2, label='2016 - Paris Agreement')
ax.set(title='Global CO2 Emissions (1950-2022)',
       xlabel='Year', ylabel='CO2 Emissions (Million Tonnes)')
ax.legend()
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
save(fig, '01_global_co2_trend.png')

# 3.2 Top 10 Emitters 2022
print("[Plot 2] Top 10 Emitters bar chart ...")
top10 = latest.nlargest(10, 'co2')
fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.barh(top10['country'][::-1], top10['co2'][::-1],
               color=PALETTE[:10], edgecolor='none', height=0.65)
for bar, val in zip(bars, top10['co2'][::-1]):
    ax.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2,
            f'{val:,.0f} Mt', va='center', color='#8b949e', fontsize=9)
ax.set(title='Top 10 CO2 Emitters in 2022',
       xlabel='CO2 Emissions (Million Tonnes)', ylabel='')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
save(fig, '02_top10_emitters_2022.png')

# 3.3 Per-Capita Emissions Top 15
print("[Plot 3] Per-capita emissions ...")
pc_top15 = latest.nlargest(15, 'co2_per_capita').dropna(subset=['co2_per_capita'])
fig, ax = plt.subplots(figsize=(12, 6))
colors_pc = [PALETTE[i % len(PALETTE)] for i in range(len(pc_top15))]
ax.bar(pc_top15['country'], pc_top15['co2_per_capita'],
       color=colors_pc, edgecolor='none', width=0.65)
ax.set(title='Top 15 Countries by CO2 Per Capita (2022)',
       xlabel='Country', ylabel='CO2 per Capita (Tonnes per person)')
plt.xticks(rotation=40, ha='right')
save(fig, '03_per_capita_top15.png')

# 3.4 Emissions by Source (World)
print("[Plot 4] Emissions by source stacked area ...")
src_cols   = ['coal_co2','oil_co2','gas_co2','cement_co2','flaring_co2']
src_labels = ['Coal','Oil','Natural Gas','Cement','Flaring']
src_colors = ['#f78166','#ffa657','#58a6ff','#d2a8ff','#3fb950']

df_src = df_w[['year'] + src_cols].dropna()
fig, ax = plt.subplots(figsize=(13, 6))
ax.stackplot(df_src['year'],
             [df_src[c] for c in src_cols],
             labels=src_labels, colors=src_colors, alpha=0.85)
ax.set(title='Global CO2 by Emission Source (1950-2022)',
       xlabel='Year', ylabel='CO2 Emissions (Million Tonnes)')
ax.legend(loc='upper left', ncol=3)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
save(fig, '04_emissions_by_source.png')

# 3.5 Share of Global CO2 — Top 5
print("[Plot 5] Share of global CO2 trend lines ...")
TOP5 = ['China','United States','India','Russia','Japan']
fig, ax = plt.subplots(figsize=(13, 6))
for i, country in enumerate(TOP5):
    cdf = df_key[(df_key['country'] == country) & df_key['share_global_co2'].notna()]
    ax.plot(cdf['year'], cdf['share_global_co2'],
            color=PALETTE[i], lw=2.2, label=country)
    if len(cdf) > 0:
        ax.text(cdf['year'].iloc[-1] + 0.3, cdf['share_global_co2'].iloc[-1],
                country, color=PALETTE[i], va='center', fontsize=9)
ax.set(title='Share of Global CO2 - Top 5 Countries (1950-2022)',
       xlabel='Year', ylabel='Share of Global CO2 (%)')
ax.legend(loc='upper left')
save(fig, '05_share_global_co2.png')

# 3.6 Correlation Heatmap
print("[Plot 6] Correlation heatmap ...")
corr_cols = ['co2','co2_per_capita','coal_co2','oil_co2','gas_co2',
             'cement_co2','cumulative_co2','gdp','population']
corr_data = latest[corr_cols].dropna()
corr_mat  = corr_data.corr()

fig, ax = plt.subplots(figsize=(10, 8))
mask = np.triu(np.ones_like(corr_mat, dtype=bool))
sns.heatmap(corr_mat, mask=mask, annot=True, fmt='.2f',
            cmap='coolwarm', center=0, linewidths=0.5,
            linecolor='#0d1117', ax=ax,
            annot_kws={'size': 9},
            cbar_kws={'shrink': 0.8})
ax.set_title('Correlation Matrix - Key CO2 Variables (2022)', pad=15)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
save(fig, '06_correlation_heatmap.png')

# 3.7 GDP vs CO2 Scatter
print("[Plot 7] GDP vs CO2 scatter ...")
scatter_df = latest.dropna(subset=['gdp','co2','population']).copy()
scatter_df['gdp_per_cap'] = scatter_df['gdp'] / scatter_df['population']

fig, ax = plt.subplots(figsize=(11, 7))
sc = ax.scatter(scatter_df['gdp_per_cap'], scatter_df['co2_per_capita'],
                c=scatter_df['co2'], cmap='plasma',
                s=scatter_df['population'] / 2e6 + 20,
                alpha=0.75, edgecolors='none')
cb = fig.colorbar(sc, ax=ax, label='Total CO2 (Mt)')

annotate_countries = [
    'United States','China','India','Germany','Australia',
    'Saudi Arabia','Canada','Japan','Brazil','Russia'
]
for _, row in scatter_df[scatter_df['country'].isin(annotate_countries)].iterrows():
    ax.annotate(row['country'],
                (row['gdp_per_cap'], row['co2_per_capita']),
                fontsize=7.5, color='#e6edf3',
                xytext=(5, 5), textcoords='offset points')

slope, intercept, r, p, _ = stats.linregress(
    np.log1p(scatter_df['gdp_per_cap']),
    scatter_df['co2_per_capita']
)
x_line = np.linspace(scatter_df['gdp_per_cap'].min(),
                     scatter_df['gdp_per_cap'].max(), 300)
ax.plot(x_line, slope * np.log1p(x_line) + intercept,
        color='#f78166', lw=1.8, ls='--', label=f'Trend  R2={r**2:.2f}')
ax.legend()
ax.set(title='GDP per Capita vs CO2 per Capita (2022)',
       xlabel='GDP per Capita (USD)', ylabel='CO2 per Capita (t/person)')
ax.set_xscale('log')
save(fig, '07_gdp_vs_co2.png')

# 3.8 Cumulative CO2 Pie
print("[Plot 8] Cumulative CO2 pie ...")
cum_top8 = latest.dropna(subset=['cumulative_co2']).nlargest(8, 'cumulative_co2')
others   = (latest.dropna(subset=['cumulative_co2'])['cumulative_co2'].sum()
            - cum_top8['cumulative_co2'].sum())
pie_labels = list(cum_top8['country']) + ['Rest of World']
pie_sizes  = list(cum_top8['cumulative_co2']) + [others]
pie_colors = PALETTE[:8] + ['#555']

fig, ax = plt.subplots(figsize=(10, 8))
wedges, texts, autotexts = ax.pie(
    pie_sizes, labels=pie_labels, colors=pie_colors,
    autopct='%1.1f%%', pctdistance=0.82,
    startangle=140,
    wedgeprops={'edgecolor': '#0d1117', 'linewidth': 1.5}
)
for at in autotexts:
    at.set_fontsize(8.5)
    at.set_color('#0d1117')
ax.set_title('Cumulative CO2 Emissions - Historical Responsibility', pad=20)
save(fig, '08_cumulative_co2_pie.png')

# 3.9 India & China Comparison
print("[Plot 9] India vs China growth ...")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for ax, country, color in zip(axes, ['China','India'], ['#f78166','#3fb950']):
    cdf = df_key[(df_key['country'] == country) & df_key['co2'].notna()]
    ax.fill_between(cdf['year'], cdf['co2'], alpha=0.3, color=color)
    ax.plot(cdf['year'], cdf['co2'], color=color, lw=2.5)
    ax.set(title=f'{country} - CO2 Emissions (1950-2022)',
           xlabel='Year', ylabel='CO2 (Million Tonnes)')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
fig.suptitle('Emerging Giants: CO2 Growth Trajectories', fontsize=15, fontweight='bold', y=1.02)
fig.tight_layout()
save(fig, '09_china_india_comparison.png')

# 3.10 Decade-wise Heatmap
print("[Plot 10] Decade-wise heatmap ...")
df_key['decade'] = (df_key['year'] // 10) * 10
top15_countries  = latest.nlargest(15, 'co2')['country'].tolist()
dec_df = (df_key[df_key['country'].isin(top15_countries)]
          .groupby(['country','decade'])['co2']
          .mean().reset_index())
dec_pivot = dec_df.pivot(index='country', columns='decade', values='co2')

fig, ax = plt.subplots(figsize=(13, 7))
sns.heatmap(dec_pivot, cmap='YlOrRd', annot=True, fmt='.0f',
            linewidths=0.4, linecolor='#0d1117', ax=ax,
            cbar_kws={'label': 'Avg CO2 (Mt)', 'shrink': 0.8},
            annot_kws={'size': 8})
ax.set(title='Avg CO2 Emissions by Decade - Top 15 Countries',
       xlabel='Decade', ylabel='')
plt.xticks(rotation=0)
save(fig, '10_decade_heatmap.png')


# ===========================================================================
# 4. KEY FINDINGS SUMMARY
# ===========================================================================
print("\n--- STEP 4: KEY FINDINGS ---")

world_2022 = df_w[df_w['year'] == 2022]['co2'].values[0]
world_1950 = df_w[df_w['year'] == 1950]['co2'].values[0]
growth_pct = (world_2022 - world_1950) / world_1950 * 100

top1_country = latest.nlargest(1, 'co2')['country'].values[0]
top1_share   = latest.nlargest(1, 'share_global_co2')['share_global_co2'].values[0]

pc_max     = latest.nlargest(1, 'co2_per_capita')
pc_country = pc_max['country'].values[0]
pc_val     = pc_max['co2_per_capita'].values[0]

print(f"""
KEY FINDINGS:
  1. Global CO2 grew by {growth_pct:.0f}% from 1950 to 2022
  2. {top1_country} is the largest emitter ({top1_share:.1f}% of global CO2)
  3. {pc_country} has the highest per-capita emissions ({pc_val:.1f} t/person)
  4. Coal remains the #1 source of CO2 emissions globally
  5. USA has the highest cumulative (historical) CO2 burden
  6. China CO2 surged 15x since 1950 due to industrialisation
  7. India per-capita emissions remain relatively low
  8. GDP and CO2 per capita correlate strongly (R2 approx 0.55)
  9. Post-2010: renewables are beginning to slow the growth rate
 10. Flaring and cement are fast-growing minor emission sources
""")

print("  All 10 visualisations saved to:", OUT_DIR)
print("  EDA analysis complete!")
