import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib
import numpy as np
from scipy import stats

# CJK font support on Windows
for _fn in ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']:
    try:
        matplotlib.rcParams['font.family'] = _fn
        break
    except Exception:
        continue
matplotlib.rcParams['axes.unicode_minus'] = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATASETS = {
    'data5':  os.path.join(BASE_DIR, 'data5'),
    'data30': os.path.join(BASE_DIR, 'data30'),
}
OUTPUT_DIRS = {
    'data5':  os.path.join(BASE_DIR, 'image5'),
    'data30': os.path.join(BASE_DIR, 'image30'),
}

METRICS = ['Temp', 'Humid', 'Light']
METRIC_TITLES = {
    'Temp':  'Temperature (°C) over Time',
    'Humid': 'Humidity (%) over Time',
    'Light': 'Light Level over Time',
}
METRIC_YLABELS = {
    'Temp':  'Temperature (°C)',
    'Humid': 'Humidity (%)',
    'Light': 'Light Level',
}
BAR_TITLES = {
    'Temp':  'Average Temperature (°C) with Standard Deviation',
    'Humid': 'Average Humidity (%) with Standard Deviation',
    'Light': 'Average Light Level with Standard Deviation',
}
BAR_YLABELS = {
    'Temp':  'Temperature (°C)',
    'Humid': 'Humidity (%)',
    'Light': 'Light Level',
}

# Guitar safe-storage thresholds (from dissertation)
TEMP_ALERT   = 30.0   # °C
HUMID_MIN    = 40.0   # % RH – lower safe bound
HUMID_MAX    = 60.0   # % RH – upper safe bound

# Colors per location (consistent across all charts)
LOCATION_COLORS = [
    '#E07B6A',  # Bedroom Far  – salmon
    '#6BAED6',  # Bedroom Mid  – steel blue
    '#74C476',  # Kitchen Far  – green
    '#FDD835',  # Kitchen Mid  – yellow
    '#FB8072',  # Hallway End  – coral
    '#BC80BD',  # Hallway Mid  – purple
]

# Canonical display names (order matches bar chart in reference)
DISPLAY_ORDER = [
    'Bedroom (Far from Door)',
    'Bedroom (Middle)',
    'Kitchen (Far from Door)',
    'Kitchen (Middle)',
    'Hallway (End)',
    'Hallway (Middle)',
]
OPTIMAL_LOCATION = 'Bedroom (Far from Door)'

# Short x-tick labels for bar charts
SHORT_NAMES = {
    'Bedroom (Far from Door)': 'Bedroom (Far)',
    'Bedroom (Middle)':        'Bedroom (Mid)',
    'Kitchen (Far from Door)': 'Kitchen (Far)',
    'Kitchen (Middle)':        'Kitchen (Mid)',
    'Hallway (End)':           'Hallway (End)',
    'Hallway (Middle)':        'Hallway (Mid)',
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def infer_display_name(raw_name: str) -> str:
    n = raw_name.lower()
    if 'bedroom' in n or '卧室' in n:
        return 'Bedroom (Far from Door)' if ('far' in n or '远' in n) else 'Bedroom (Middle)'
    if 'kitchen' in n or '厨房' in n:
        return 'Kitchen (Far from Door)' if ('far' in n or '远' in n) else 'Kitchen (Middle)'
    if 'hallway' in n or 'hall' in n or '走廊' in n:
        return 'Hallway (End)' if ('end' in n or '端' in n) else 'Hallway (Middle)'
    return raw_name


def find_csv_files(data_dir):
    entries = {}
    for root, dirs, files in os.walk(data_dir):
        for f in files:
            if f.endswith('.csv'):
                raw     = os.path.splitext(f)[0]
                display = infer_display_name(raw)
                df      = pd.read_csv(os.path.join(root, f))
                df.columns = df.columns.str.strip()
                df = df.dropna()
                df['Time (hours)'] = df['Time (seconds)'] / 3600.0
                entries[display] = df

    ordered = []
    for name in DISPLAY_ORDER:
        if name in entries:
            ordered.append((name, entries[name]))
    for name, df in entries.items():
        if name not in DISPLAY_ORDER:
            ordered.append((name, df))
    return ordered


def cohens_d(a, b):
    """Cohen's d effect size between two arrays."""
    pooled_std = np.sqrt((np.std(a, ddof=1) ** 2 + np.std(b, ddof=1) ** 2) / 2)
    return (np.mean(a) - np.mean(b)) / pooled_std if pooled_std > 0 else 0.0


# ---------------------------------------------------------------------------
# 1. Line chart  (with safe-threshold annotations)
# ---------------------------------------------------------------------------

def plot_line_chart(location_data, output_dir):
    fig, axes = plt.subplots(3, 1, figsize=(11, 12))
    fig.subplots_adjust(hspace=0.45, right=0.78)

    for ax_idx, metric in enumerate(METRICS):
        ax = axes[ax_idx]

        # Plot each location
        for loc_idx, (name, df) in enumerate(location_data):
            color = LOCATION_COLORS[loc_idx % len(LOCATION_COLORS)]
            ax.plot(df['Time (hours)'], df[metric],
                    color=color, linewidth=0.9, alpha=0.9, label=name)

        # --- Safe threshold annotations ---
        if metric == 'Temp':
            ax.axhline(TEMP_ALERT, color='red', linestyle='--', linewidth=1.2, alpha=0.8)
            ax.text(ax.get_xlim()[1] if ax.get_xlim()[1] > 0 else 12,
                    TEMP_ALERT + 0.3, f'Alert ≥{TEMP_ALERT:.0f}°C',
                    color='red', fontsize=7.5, ha='right', va='bottom')

        if metric == 'Humid':
            ax.axhspan(HUMID_MIN, HUMID_MAX, color='green', alpha=0.08, label='Safe zone (40–60%)')
            ax.axhline(HUMID_MIN, color='green', linestyle='--', linewidth=1.2, alpha=0.7)
            ax.axhline(HUMID_MAX, color='green', linestyle='--', linewidth=1.2, alpha=0.7)
            x_right = ax.get_xlim()[1] if ax.get_xlim()[1] > 0 else 12
            ax.text(x_right, HUMID_MIN - 1.5, f'Safe min {HUMID_MIN:.0f}%',
                    color='green', fontsize=7.5, ha='right', va='top')
            ax.text(x_right, HUMID_MAX + 0.5, f'Safe max {HUMID_MAX:.0f}%',
                    color='green', fontsize=7.5, ha='right', va='bottom')

        ax.set_title(METRIC_TITLES[metric], fontsize=11, pad=6)
        ax.set_ylabel(METRIC_YLABELS[metric], fontsize=9)
        ax.set_xlabel('Time (hours)', fontsize=9)
        ax.grid(True, linestyle='--', alpha=0.35)
        ax.legend(fontsize=7.5, loc='upper left',
                  bbox_to_anchor=(1.01, 1), borderaxespad=0, framealpha=0.8)

    out_path = os.path.join(output_dir, 'linechart.png')
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'  Saved: {out_path}')


# ---------------------------------------------------------------------------
# 2. Bar chart  (with Bedroom Far highlighted as optimal)
# ---------------------------------------------------------------------------

def plot_bar_chart(location_data, output_dir):
    names       = [name for name, _ in location_data]
    short_names = [SHORT_NAMES.get(n, n) for n in names]
    x           = np.arange(len(names))
    bar_width   = 0.55

    fig, axes = plt.subplots(3, 1, figsize=(10, 13))
    fig.subplots_adjust(hspace=0.55)

    for ax_idx, metric in enumerate(METRICS):
        ax    = axes[ax_idx]
        means = [df[metric].mean() for _, df in location_data]
        stds  = [df[metric].std()  for _, df in location_data]

        for i, (mean, std, name) in enumerate(zip(means, stds, names)):
            color    = LOCATION_COLORS[i % len(LOCATION_COLORS)]
            edgecolor = '#1A1A1A' if name == OPTIMAL_LOCATION else 'none'
            lw        = 2.0       if name == OPTIMAL_LOCATION else 0.0
            ax.bar(x[i], mean, width=bar_width,
                   color=color, alpha=0.85,
                   edgecolor=edgecolor, linewidth=lw,
                   yerr=std, capsize=6,
                   error_kw=dict(ecolor='#333333', elinewidth=1.5, capthick=1.5))
            ax.text(x[i], mean + std + max(means) * 0.03,
                    f'{mean:.1f}±{std:.1f}',
                    ha='center', va='bottom', fontsize=7.5, color='#222222')

        # Highlight optimal location with annotation arrow
        opt_idx = names.index(OPTIMAL_LOCATION) if OPTIMAL_LOCATION in names else None
        if opt_idx is not None:
            opt_top = means[opt_idx] + stds[opt_idx] + max(means) * 0.03
            arrow_y = opt_top + max(means) * 0.18
            ax.annotate('Optimal\nLocation',
                        xy=(x[opt_idx], opt_top + max(means) * 0.02),
                        xytext=(x[opt_idx], arrow_y),
                        fontsize=7.5, ha='center', color='#1A1A1A',
                        arrowprops=dict(arrowstyle='->', color='#1A1A1A', lw=1.2))

        ax.set_title(BAR_TITLES[metric], fontsize=10, pad=6)
        ax.set_ylabel(BAR_YLABELS[metric], fontsize=9)
        ax.set_xticks(x)
        ax.set_xticklabels(short_names, fontsize=8.5)
        ax.set_ylim(bottom=0)
        ax.grid(True, axis='y', linestyle='--', alpha=0.35)

    out_path = os.path.join(output_dir, 'barchart.png')
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'  Saved: {out_path}')


# ---------------------------------------------------------------------------
# 3. Statistical tests  (ANOVA, Welch t-test, Levene, Cohen's d)
# ---------------------------------------------------------------------------

def run_statistical_tests(location_data, output_dir):
    names = [name for name, _ in location_data]
    rows  = []

    # ---------- One-Way ANOVA ----------
    for metric in METRICS:
        groups  = [df[metric].values for _, df in location_data]
        F, p    = stats.f_oneway(*groups)
        rows.append({'Test': 'One-Way ANOVA', 'Metric': metric, 'Group A': 'All locations',
                     'Group B': '—', 'Statistic': round(F, 2), 'p-value': f'{p:.3e}',
                     'Effect Size (d)': '—',
                     'Significant': 'Yes' if p < 0.05 else 'No'})

    # ---------- Levene's test ----------
    for metric in ['Temp', 'Humid']:
        groups = [df[metric].values for _, df in location_data]
        W, p   = stats.levene(*groups)
        rows.append({'Test': "Levene's Test", 'Metric': metric, 'Group A': 'All locations',
                     'Group B': '—', 'Statistic': round(W, 2), 'p-value': f'{p:.3e}',
                     'Effect Size (d)': '—',
                     'Significant': 'Yes' if p < 0.05 else 'No'})

    # ---------- Welch's t-tests & Cohen's d (Bedroom Far vs others) ----------
    opt_data = {name: df for name, df in location_data}
    if OPTIMAL_LOCATION in opt_data:
        ref_df = opt_data[OPTIMAL_LOCATION]
        for metric in ['Temp', 'Humid']:
            for name, df in location_data:
                if name == OPTIMAL_LOCATION:
                    continue
                t, p = stats.ttest_ind(ref_df[metric].values, df[metric].values,
                                       equal_var=False)
                d    = cohens_d(ref_df[metric].values, df[metric].values)
                rows.append({'Test': "Welch's t-test", 'Metric': metric,
                             'Group A': 'Bedroom (Far)', 'Group B': SHORT_NAMES.get(name, name),
                             'Statistic': round(t, 2), 'p-value': f'{p:.3e}',
                             'Effect Size (d)': round(abs(d), 2),
                             'Significant': 'Yes' if p < 0.05 else 'No'})

    results_df = pd.DataFrame(rows)

    # Save CSV
    csv_path = os.path.join(output_dir, 'stats_results.csv')
    results_df.to_csv(csv_path, index=False)
    print(f'  Saved: {csv_path}')

    # Save as PNG table
    fig, ax = plt.subplots(figsize=(14, 0.45 * len(results_df) + 1.5))
    ax.axis('off')
    col_labels = results_df.columns.tolist()
    cell_text  = results_df.values.tolist()

    tbl = ax.table(cellText=cell_text, colLabels=col_labels,
                   cellLoc='center', loc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8)
    tbl.auto_set_column_width(col=list(range(len(col_labels))))

    # Colour header row
    for j in range(len(col_labels)):
        tbl[(0, j)].set_facecolor('#2C3E50')
        tbl[(0, j)].set_text_props(color='white', fontweight='bold')

    # Highlight significant results
    for i, row in enumerate(cell_text):
        if row[-1] == 'Yes':
            for j in range(len(col_labels)):
                tbl[(i + 1, j)].set_facecolor('#FDEBD0')

    ax.set_title('Statistical Analysis Results', fontsize=12, fontweight='bold', pad=10)
    plt.tight_layout()
    png_path = os.path.join(output_dir, 'stats_table.png')
    plt.savefig(png_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'  Saved: {png_path}')


# ---------------------------------------------------------------------------
# 4. Cross-phase comparison chart
# ---------------------------------------------------------------------------

def plot_cross_phase_comparison(data5_locs, data30_locs, output_path):
    # Align by display name
    d5  = {name: df for name, df in data5_locs}
    d30 = {name: df for name, df in data30_locs}
    shared_names = [n for n in DISPLAY_ORDER if n in d5 and n in d30]

    x          = np.arange(len(shared_names))
    bar_width  = 0.35
    short      = [SHORT_NAMES.get(n, n) for n in shared_names]

    fig, axes = plt.subplots(3, 1, figsize=(12, 13))
    fig.subplots_adjust(hspace=0.55)
    fig.suptitle('Cross-Phase Comparison: Phase 1 (5 s) vs Phase 2 (30 s)',
                 fontsize=13, fontweight='bold', y=0.98)

    p1_patch = mpatches.Patch(color='#5B9BD5', label='Phase 1 (5 s sampling)')
    p2_patch = mpatches.Patch(color='#ED7D31', label='Phase 2 (30 s sampling)')

    for ax_idx, metric in enumerate(METRICS):
        ax = axes[ax_idx]

        means5  = [d5[n][metric].mean()  for n in shared_names]
        stds5   = [d5[n][metric].std()   for n in shared_names]
        means30 = [d30[n][metric].mean() for n in shared_names]
        stds30  = [d30[n][metric].std()  for n in shared_names]

        ax.bar(x - bar_width / 2, means5,  width=bar_width, color='#5B9BD5', alpha=0.85,
               yerr=stds5,  capsize=5,
               error_kw=dict(ecolor='#1A1A1A', elinewidth=1.2, capthick=1.2),
               label='Phase 1 (5 s)')
        ax.bar(x + bar_width / 2, means30, width=bar_width, color='#ED7D31', alpha=0.85,
               yerr=stds30, capsize=5,
               error_kw=dict(ecolor='#1A1A1A', elinewidth=1.2, capthick=1.2),
               label='Phase 2 (30 s)')

        # Annotate mean values
        for i, (m5, m30) in enumerate(zip(means5, means30)):
            ax.text(x[i] - bar_width / 2, m5  + stds5[i]  + max(means5  + means30) * 0.02,
                    f'{m5:.1f}',  ha='center', va='bottom', fontsize=7, color='#1A375A')
            ax.text(x[i] + bar_width / 2, m30 + stds30[i] + max(means5  + means30) * 0.02,
                    f'{m30:.1f}', ha='center', va='bottom', fontsize=7, color='#7B3000')

        # Safe threshold lines
        if metric == 'Temp':
            ax.axhline(TEMP_ALERT, color='red', linestyle='--', linewidth=1.0, alpha=0.7)
            ax.text(len(shared_names) - 0.5, TEMP_ALERT + 0.2,
                    f'Alert {TEMP_ALERT:.0f}°C', color='red', fontsize=7.5, ha='right')
        if metric == 'Humid':
            ax.axhspan(HUMID_MIN, HUMID_MAX, color='green', alpha=0.07)
            ax.axhline(HUMID_MIN, color='green', linestyle='--', linewidth=1.0, alpha=0.7)
            ax.axhline(HUMID_MAX, color='green', linestyle='--', linewidth=1.0, alpha=0.7)
            ax.text(len(shared_names) - 0.5, HUMID_MIN - 1.5,
                    'Safe min 40%', color='green', fontsize=7.5, ha='right', va='top')
            ax.text(len(shared_names) - 0.5, HUMID_MAX + 0.5,
                    'Safe max 60%', color='green', fontsize=7.5, ha='right', va='bottom')

        ax.set_title(f'Average {METRIC_YLABELS[metric]} — Phase Comparison', fontsize=10, pad=6)
        ax.set_ylabel(METRIC_YLABELS[metric], fontsize=9)
        ax.set_xticks(x)
        ax.set_xticklabels(short, fontsize=8.5)
        ax.set_ylim(bottom=0)
        ax.grid(True, axis='y', linestyle='--', alpha=0.35)
        ax.legend(handles=[p1_patch, p2_patch], fontsize=8, loc='upper right')

    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'  Saved: {output_path}')


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------

def process_dataset(dataset_key):
    data_dir   = DATASETS[dataset_key]
    output_dir = OUTPUT_DIRS[dataset_key]
    os.makedirs(output_dir, exist_ok=True)

    location_data = find_csv_files(data_dir)
    if not location_data:
        print(f'No CSV files found in {data_dir}')
        return location_data

    print(f'\n=== Processing {dataset_key} ({len(location_data)} locations) ===')
    for name, df in location_data:
        print(f'  {name}: {len(df)} rows')

    plot_line_chart(location_data, output_dir)
    plot_bar_chart(location_data, output_dir)
    run_statistical_tests(location_data, output_dir)
    print(f'Done. Charts saved to: {output_dir}')
    return location_data


if __name__ == '__main__':
    data5_locs  = process_dataset('data5')
    data30_locs = process_dataset('data30')

    # Cross-phase comparison saved to project root
    comparison_path = os.path.join(BASE_DIR, 'comparison_chart.png')
    print('\n=== Generating cross-phase comparison chart ===')
    plot_cross_phase_comparison(data5_locs, data30_locs, comparison_path)
