#!/usr/bin/env python3
"""
Enhanced ARGO Data Points Visualization Script

This script creates multiple visualizations showing the growth of ARGO float data points
over time (2003-2025), broken down by parameter categories: Core, Extended Core,
Bio-Argo, and Deep Argo.

Features:
- Stacked area chart (absolute values)
- Percentage stacked area chart
- Line plot showing individual trends
- Pie chart for final year breakdown
- Summary statistics

Data source: Provided ARGO dataset statistics
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

# Data: ARGO data points in millions (M) by year and category
years = list(range(2003, 2026))

# Core parameters (T/S/P) - millions of data points
core = [
    11, 17, 26, 35, 43, 50, 56, 61, 65, 69, 73, 75, 78, 80, 82, 82, 84, 86,
    86, 86, 86, 86, 86
]

# Extended Core (O₂/tech vars) - millions of data points
extended_core = [
    0, 0, 0, 0, 0, 0, 0, 24, 26, 28, 30, 31, 32, 33, 34, 34, 35, 36,
    36, 36, 36, 36, 36
]

# Bio-Argo parameters - millions of data points
bio_argo = [
    0, 0, 2, 3, 4, 6, 8, 11, 13, 15, 18, 21, 24, 27, 30, 30, 31, 32,
    32, 32, 32, 32, 32
]

# Deep Argo parameters - millions of data points
deep_argo = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 8, 12, 14, 16, 18, 20, 22,
    22, 22, 22
]

# Colors for consistent theming
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # Blue, Orange, Green, Red
categories = ['Core (T/S/P)', 'Extended Core (O₂/tech)', 'Bio-Argo', 'Deep Argo']
data_arrays = [core, extended_core, bio_argo, deep_argo]

def create_separate_visualizations():
    """Create separate individual plots for each visualization type"""

    # 1. Absolute Stacked Area Chart
    plt.figure(figsize=(14, 8))
    plt.stackplot(years, core, extended_core, bio_argo, deep_argo,
                  labels=categories, colors=colors, alpha=0.8)
    plt.title('ARGO Data Points Growth (2003-2025)\nAbsolute Values by Parameter Category',
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Data Points (Millions)', fontsize=12)
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}M'))
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper left', fontsize=10, framealpha=0.9)

    # Add milestone annotations
    milestones = [(2010, "Extended Core Begins"), (2015, "Bio-Argo & Deep Argo Start"), (2020, "Mature System")]
    for year, label in milestones:
        if year in years:
            idx = years.index(year)
            total = sum(data[idx] for data in data_arrays)
            plt.annotate(label, xy=(year, total), xytext=(year-1, total+15),
                        arrowprops=dict(arrowstyle="->", color='red', alpha=0.7),
                        fontsize=9, ha='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.8))

    plt.tight_layout()
    plt.savefig('argo_absolute_stacked.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Absolute stacked area chart saved as 'argo_absolute_stacked.png'")

    # 2. Percentage Stacked Area Chart
    plt.figure(figsize=(14, 8))
    totals = np.array(core) + np.array(extended_core) + np.array(bio_argo) + np.array(deep_argo)
    core_pct = np.array(core) / totals * 100
    ext_pct = np.array(extended_core) / totals * 100
    bio_pct = np.array(bio_argo) / totals * 100
    deep_pct = np.array(deep_argo) / totals * 100

    plt.stackplot(years, core_pct, ext_pct, bio_pct, deep_pct,
                  labels=categories, colors=colors, alpha=0.8)
    plt.title('ARGO Data Points Growth (2003-2025)\nPercentage Composition by Category',
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Percentage (%)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper left', fontsize=10, framealpha=0.9)
    plt.tight_layout()
    plt.savefig('argo_percentage_stacked.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Percentage stacked area chart saved as 'argo_percentage_stacked.png'")

    # 3. Line Plot for Individual Trends
    plt.figure(figsize=(12, 8))
    for i, (data, color, label) in enumerate(zip(data_arrays, colors, categories)):
        plt.plot(years, data, color=color, linewidth=3, marker='o', markersize=6, label=label)
    plt.title('ARGO Parameter Category Trends (2003-2025)',
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Data Points (Millions)', fontsize=12)
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}M'))
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper left', fontsize=10, framealpha=0.9)
    plt.tight_layout()
    plt.savefig('argo_individual_trends.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Individual trends line plot saved as 'argo_individual_trends.png'")

    # 4. Pie Chart for Cumulative Data (2003-2025)
    plt.figure(figsize=(10, 8))
    cumulative_data = [sum(core), sum(extended_core), sum(bio_argo), sum(deep_argo)]
    wedges, texts, autotexts = plt.pie(cumulative_data, labels=categories, colors=colors,
                                       autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'white', 'linewidth': 2})
    plt.title('ARGO Data Points Breakdown (2003-2025)\nCumulative Contribution by Category',
              fontsize=16, fontweight='bold', pad=20)
    plt.setp(autotexts, size=12, weight="bold")
    plt.setp(texts, size=11)
    plt.tight_layout()
    plt.savefig('argo_cumulative_pie_chart.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Cumulative pie chart saved as 'argo_cumulative_pie_chart.png'")

    # Keep the 2025 snapshot as well
    plt.figure(figsize=(10, 8))
    final_year_data = [core[-1], extended_core[-1], bio_argo[-1], deep_argo[-1]]
    wedges, texts, autotexts = plt.pie(final_year_data, labels=categories, colors=colors,
                                       autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'white', 'linewidth': 2})
    plt.title('ARGO Data Points Breakdown - 2025 Snapshot',
              fontsize=16, fontweight='bold', pad=20)
    plt.setp(autotexts, size=12, weight="bold")
    plt.setp(texts, size=11)
    plt.tight_layout()
    plt.savefig('argo_2025_pie_chart.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ 2025 snapshot pie chart saved as 'argo_2025_pie_chart.png'")

    # 5. Growth Rate Analysis
    plt.figure(figsize=(14, 8))
    growth_rates = []
    for i in range(1, len(years)):
        prev_total = sum(data[i-1] for data in data_arrays)
        curr_total = sum(data[i] for data in data_arrays)
        if prev_total > 0:
            growth_rate = ((curr_total - prev_total) / prev_total) * 100
        else:
            growth_rate = 0
        growth_rates.append(growth_rate)

    bars = plt.bar(years[1:], growth_rates, color='#9467bd', alpha=0.8, width=0.8)
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=1)
    plt.title('Year-over-Year Growth Rate of ARGO Data Points (2003-2025)',
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Growth Rate (%)', fontsize=12)
    plt.grid(True, alpha=0.3, axis='y')

    # Add value labels on bars
    for bar, rate in zip(bars, growth_rates):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + (1 if height >= 0 else -3),
                f'{rate:+.1f}%', ha='center', va='bottom' if height >= 0 else 'top',
                fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.savefig('argo_growth_rates.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Growth rate analysis saved as 'argo_growth_rates.png'")

    # 6. Bonus: Total Data Points Over Time (Area Chart)
    plt.figure(figsize=(12, 8))
    totals = [sum(data[i] for data in data_arrays) for i in range(len(years))]
    plt.fill_between(years, totals, color='#1f77b4', alpha=0.6)
    plt.plot(years, totals, color='#1f77b4', linewidth=3, marker='o', markersize=6)

    plt.title('Total ARGO Data Points Over Time (2003-2025)',
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Total Data Points (Millions)', fontsize=12)
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}M'))
    plt.grid(True, alpha=0.3)

    # Add data point annotations for key years
    key_years = [2003, 2010, 2015, 2020, 2025]
    for year in key_years:
        if year in years:
            idx = years.index(year)
            total = totals[idx]
            plt.annotate(f'{total}M', xy=(year, total), xytext=(5, 10),
                        textcoords='offset points', fontsize=11, fontweight='bold',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9))

    plt.tight_layout()
    plt.savefig('argo_total_over_time.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Total data points over time saved as 'argo_total_over_time.png'")

def create_comprehensive_visualization():
    """Create the original multi-panel comprehensive visualization (kept for comparison)"""
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)

    # 1. Absolute Stacked Area Chart
    ax1 = fig.add_subplot(gs[0, :2])
    ax1.stackplot(years, core, extended_core, bio_argo, deep_argo,
                  labels=categories, colors=colors, alpha=0.8)
    ax1.set_title('ARGO Data Points Growth (2003-2025)\nAbsolute Values', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Data Points (Millions)')
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}M'))
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left')

    # 2. Percentage Stacked Area Chart
    ax2 = fig.add_subplot(gs[1, :2])
    totals = np.array(core) + np.array(extended_core) + np.array(bio_argo) + np.array(deep_argo)
    core_pct = np.array(core) / totals * 100
    ext_pct = np.array(extended_core) / totals * 100
    bio_pct = np.array(bio_argo) / totals * 100
    deep_pct = np.array(deep_argo) / totals * 100

    ax2.stackplot(years, core_pct, ext_pct, bio_pct, deep_pct,
                  labels=categories, colors=colors, alpha=0.8)
    ax2.set_title('ARGO Data Points Growth (2003-2025)\nPercentage Composition', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Percentage (%)')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper left')

    # 3. Line Plot for Individual Trends
    ax3 = fig.add_subplot(gs[0, 2])
    for i, (data, color, label) in enumerate(zip(data_arrays, colors, categories)):
        ax3.plot(years, data, color=color, linewidth=2, marker='o', markersize=4, label=label)
    ax3.set_title('Individual Category Trends', fontsize=12, fontweight='bold')
    ax3.set_xlabel('Year')
    ax3.set_ylabel('Data Points (Millions)')
    ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}M'))
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=8)

    # 4. Pie Chart for Final Year (2025)
    ax4 = fig.add_subplot(gs[1, 2])
    final_year_data = [core[-1], extended_core[-1], bio_argo[-1], deep_argo[-1]]
    wedges, texts, autotexts = ax4.pie(final_year_data, labels=categories, colors=colors,
                                       autopct='%1.1f%%', startangle=90)
    ax4.set_title('2025 Data Points Breakdown', fontsize=12, fontweight='bold')
    plt.setp(autotexts, size=8, weight="bold")
    plt.setp(texts, size=8)

    # 5. Growth Rate Analysis
    ax5 = fig.add_subplot(gs[2, :])
    growth_rates = []
    for i in range(1, len(years)):
        prev_total = core[i-1] + extended_core[i-1] + bio_argo[i-1] + deep_argo[i-1]
        curr_total = core[i] + extended_core[i] + bio_argo[i] + deep_argo[i]
        if prev_total > 0:
            growth_rate = ((curr_total - prev_total) / prev_total) * 100
        else:
            growth_rate = 0
        growth_rates.append(growth_rate)

    ax5.bar(years[1:], growth_rates, color='#9467bd', alpha=0.7)
    ax5.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax5.set_title('Year-over-Year Growth Rate of Total ARGO Data Points', fontsize=14, fontweight='bold')
    ax5.set_xlabel('Year')
    ax5.set_ylabel('Growth Rate (%)')
    ax5.grid(True, alpha=0.3)

    # Add milestone annotations
    milestones = [
        (2010, "Extended Core\nBegins"),
        (2015, "Bio-Argo &\nDeep Argo Start"),
        (2020, "Mature\nMulti-Parameter\nSystem")
    ]

    for year, label in milestones:
        if year in years:
            idx = years.index(year)
            total = core[idx] + extended_core[idx] + bio_argo[idx] + deep_argo[idx]
            ax1.annotate(label, xy=(year, total), xytext=(year-1, total+20),
                        arrowprops=dict(arrowstyle="->", color='red', alpha=0.7),
                        fontsize=8, ha='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.8))

    # Overall title
    fig.suptitle('ARGO Float Data Points Evolution (2003-2025)\nComprehensive Analysis', fontsize=16, fontweight='bold', y=0.98)

    # Save the figure
    plt.tight_layout()
    plt.savefig('argo_comprehensive_visualization.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("✓ Comprehensive multi-panel visualization saved as 'argo_comprehensive_visualization.png'")

def print_detailed_summary():
    """Print detailed summary statistics"""
    print("\n" + "="*70)
    print("COMPREHENSIVE ARGO DATA POINTS ANALYSIS (2003-2025)")
    print("="*70)

    # Calculate totals by category
    total_core = sum(core)
    total_extended = sum(extended_core)
    total_bio = sum(bio_argo)
    total_deep = sum(deep_argo)
    grand_total = total_core + total_extended + total_bio + total_deep

    print(f"\n📊 CUMULATIVE TOTALS (2003-2025):")
    print("-" * 40)
    print(f"Core Parameters (T/S/P):        {total_core:>4}M data points ({total_core/grand_total*100:>5.1f}%)")
    print(f"Extended Core (O₂/tech):       {total_extended:>4}M data points ({total_extended/grand_total*100:>5.1f}%)")
    print(f"Bio-Argo Parameters:           {total_bio:>4}M data points ({total_bio/grand_total*100:>5.1f}%)")
    print(f"Deep Argo Parameters:          {total_deep:>4}M data points ({total_deep/grand_total*100:>5.1f}%)")
    print(f"GRAND TOTAL:                   {grand_total:>4}M data points (100.0%)")

    # 2025 Analysis
    print(f"\n📅 2025 ANNUAL BREAKDOWN:")
    print("-" * 40)
    year_2025_total = core[-1] + extended_core[-1] + bio_argo[-1] + deep_argo[-1]
    print(f"Total for 2025: {year_2025_total}M data points")
    print(f"Core:         {core[-1]:>3}M ({core[-1]/year_2025_total*100:>5.1f}%)")
    print(f"Extended:     {extended_core[-1]:>3}M ({extended_core[-1]/year_2025_total*100:>5.1f}%)")
    print(f"Bio-Argo:     {bio_argo[-1]:>3}M ({bio_argo[-1]/year_2025_total*100:>5.1f}%)")
    print(f"Deep Argo:    {deep_argo[-1]:>3}M ({deep_argo[-1]/year_2025_total*100:>5.1f}%)")

    # Growth analysis
    print(f"\n📈 GROWTH ANALYSIS:")
    print("-" * 40)
    initial_total = core[0] + extended_core[0] + bio_argo[0] + deep_argo[0]
    final_total = year_2025_total
    total_growth = ((final_total - initial_total) / initial_total) * 100
    avg_annual_growth = total_growth / (2025 - 2003)

    print(f"2003 Total:     {initial_total}M data points")
    print(f"2025 Total:     {final_total}M data points")
    print(f"Total Growth:   {total_growth:+.1f}% over 22 years")
    print(f"Avg Annual:     {avg_annual_growth:+.1f}% per year")

    # Period analysis
    periods = {
        "Early (2003-2009)": (0, 7),
        "Transition (2010-2015)": (7, 13),
        "Mature (2016-2025)": (13, 23)
    }

    print(f"\n📊 PERIOD ANALYSIS:")
    print("-" * 40)
    for period_name, (start_idx, end_idx) in periods.items():
        period_total = sum(
            core[start_idx:end_idx] +
            extended_core[start_idx:end_idx] +
            bio_argo[start_idx:end_idx] +
            deep_argo[start_idx:end_idx]
        )
        period_years = end_idx - start_idx
        avg_per_year = period_total / period_years
        print(f"{period_name}: {period_total:>3}M total, {avg_per_year:>5.1f}M/year avg")

    print(f"\n🎯 KEY INSIGHTS:")
    print("-" * 40)
    print("• ARGO evolved from physical-only (2003-2009) to biogeochemical observing (2020s)")
    print("• Bio-Argo emerged in 2005, now represents 18.2% of 2025 data")
    print("• Deep Argo (2015+) adds complexity despite smaller volume")
    print("• Core parameters remain dominant but Extended/Bio categories growing rapidly")

def main():
    """Main function to run the enhanced visualization"""
    print("Creating separate ARGO data visualizations...")
    print("=" * 50)
    create_separate_visualizations()
    print("\n" + "=" * 50)
    print_detailed_summary()
    print("\n🎨 Separate visualizations complete!")
    print("📁 Generated files:")
    print("  • argo_absolute_stacked.png - Absolute values stacked area chart")
    print("  • argo_percentage_stacked.png - Percentage composition stacked area chart")
    print("  • argo_individual_trends.png - Individual category line trends")
    print("  • argo_cumulative_pie_chart.png - CUMULATIVE breakdown (2003-2025)")
    print("  • argo_2025_pie_chart.png - 2025 snapshot breakdown")
    print("  • argo_growth_rates.png - Year-over-year growth rate analysis")
    print("  • argo_total_over_time.png - Total data points over time (bonus)")

    # Optional: Also create comprehensive version
    print("\n🔄 Also creating comprehensive multi-panel visualization...")
    create_comprehensive_visualization()
    print("✓ Multi-panel dashboard saved as 'argo_comprehensive_visualization.png'")

if __name__ == "__main__":
    main()
