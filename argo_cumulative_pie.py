#!/usr/bin/env python3
"""
High-Quality ARGO Cumulative Pie Chart Script

Creates a presentation-ready pie chart showing cumulative ARGO data contribution
by parameter category (2003-2025) with transparent background.
"""

import matplotlib.pyplot as plt

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

colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # Blue, Orange, Green, Red
categories = ['Core (T/S/P)', 'Extended Core (O₂/tech)', 'Bio-Argo', 'Deep Argo']

def create_cumulative_pie_chart():
    """Create high-quality cumulative pie chart for presentation"""
    plt.figure(figsize=(14, 10))

    # Calculate cumulative data
    cumulative_data = [sum(core), sum(extended_core), sum(bio_argo), sum(deep_argo)]

    # Create pie chart with enhanced styling
    wedges, texts, autotexts = plt.pie(cumulative_data,
                                       labels=categories,
                                       colors=colors,
                                       autopct='%1.1f%%',
                                       startangle=90,
                                       wedgeprops={'edgecolor': 'white', 'linewidth': 3},
                                       textprops={'fontsize': 14, 'fontweight': 'bold'},
                                       pctdistance=0.75)  # Move percentage labels inside

    # Enhanced title
    plt.title('ARGO Data Points Contribution (2003-2025)\nCumulative Impact by Parameter Category',
              fontsize=18, fontweight='bold', pad=20)

    # Style the percentage labels
    plt.setp(autotexts, size=14, weight="bold", color="white")
    plt.setp(texts, size=12, weight="bold")

    # Add statistics annotation (bottom left)
    total_cumulative = sum(cumulative_data)
    stats_text = f'Total Dataset: {total_cumulative:,}M data points\n22-year period (2003-2025)'
    plt.text(-0.1, -1.3, stats_text,
             fontsize=12, verticalalignment='center', horizontalalignment='center',
             fontweight='bold',
             bbox=dict(boxstyle="round,pad=0.8", facecolor="white", edgecolor="black", alpha=0.9))

    # Create legend with values (positioned to the right of the pie chart)
    legend_labels = [f'{cat}\n({value:,}M)' for cat, value in zip(categories, cumulative_data)]
    plt.legend(wedges, legend_labels, title="Parameter Categories",
               loc="center left", bbox_to_anchor=(1.0, 0.5),
               fontsize=11, title_fontsize=13, borderaxespad=0.5)

    plt.tight_layout()

    # Save as high-quality PNG with transparent background
    plt.savefig('argo_cumulative_pie_presentation.png', dpi=600, bbox_inches='tight', facecolor='none', transparent=True)
    plt.savefig('argo_cumulative_pie_presentation.svg', bbox_inches='tight', facecolor='none', transparent=True)
    plt.close()

    print("✓ High-quality cumulative pie chart saved as:")
    print("  • PNG: 'argo_cumulative_pie_presentation.png' (600 DPI, transparent)")
    print("  • SVG: 'argo_cumulative_pie_presentation.svg' (vector, transparent)")

def print_cumulative_analysis():
    """Print detailed cumulative analysis"""
    print("\n" + "="*70)
    print("ARGO CUMULATIVE DATA CONTRIBUTION ANALYSIS (2003-2025)")
    print("="*70)

    # Calculate cumulative data
    cumulative_data = [sum(core), sum(extended_core), sum(bio_argo), sum(deep_argo)]
    total_cumulative = sum(cumulative_data)

    print(f"\n📊 CUMULATIVE DATA POINTS BY CATEGORY:")
    print("-" * 50)
    for cat, value in zip(categories, cumulative_data):
        percentage = (value / total_cumulative) * 100
        print(f"{cat:<25} {value:>6,}M ({percentage:>5.1f}%)")

    print(f"\n{'TOTAL DATASET':<25} {total_cumulative:>6,}M (100.0%)")

    print(f"\n🎯 KEY INSIGHTS:")
    print("-" * 50)
    print("• Core parameters (T/S/P) represent 57% of all ARGO data despite being surpassed in recent years")
    print("• Extended Core (oxygen) contributes 20% despite being available for only ~15 years")
    print("• Bio-Argo (16.5%) and Deep Argo (6.7%) show significant impact despite recent introduction")
    print("• This cumulative view shows true legacy contribution vs. current year snapshots")

    print(f"\n📈 COMPARISON WITH 2025 SNAPSHOT:")
    print("-" * 50)
    year_2025_total = core[-1] + extended_core[-1] + bio_argo[-1] + deep_argo[-1]
    for i, cat in enumerate(categories):
        cum_pct = (cumulative_data[i] / total_cumulative) * 100
        yr25_pct = ([core[-1], extended_core[-1], bio_argo[-1], deep_argo[-1]][i] / year_2025_total) * 100
        diff = cum_pct - yr25_pct
        print(".1f")

def main():
    """Main function"""
    print("Creating high-quality ARGO cumulative pie chart for presentation...")
    print("=" * 60)

    create_cumulative_pie_chart()
    print_cumulative_analysis()

    print("\n" + "=" * 60)
    print("🎯 Presentation-ready cumulative pie chart complete!")
    print("📁 Generated files:")
    print("  • argo_cumulative_pie_presentation.png - High-res PNG (600 DPI, transparent)")
    print("  • argo_cumulative_pie_presentation.svg - Vector SVG (transparent)")

if __name__ == "__main__":
    main()
