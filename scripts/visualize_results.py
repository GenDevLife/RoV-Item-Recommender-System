"""
Visualize GA Tuning Results (Text-based)
แสดงผลลัพธ์การ tune GA แบบกราฟ ASCII
"""
import pandas as pd
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(PROJECT_ROOT, 'results', 'ga_tuning_results.csv')

def create_bar_chart(values, labels, width=50, title=""):
    """สร้าง bar chart แบบ ASCII"""
    max_val = max(values)
    min_val = min(values)
    
    print(f"\n{title}")
    print("=" * 70)
    
    for i, (val, label) in enumerate(zip(values, labels)):
        # Normalize to width
        bar_len = int((val - min_val) / (max_val - min_val) * width) if max_val != min_val else width // 2
        bar = "█" * bar_len
        
        # Color coding (ถ้าสนับสนุน ANSI colors)
        if val == max_val:
            marker = "🏆 "
        elif val == min_val:
            marker = "⚡ "
        else:
            marker = "   "
        
        print(f"{marker}{label:20s} │{bar} {val:.2f}")
    
    print("=" * 70)

def main():
    if not os.path.exists(CSV_PATH):
        print(f"❌ Results file not found: {CSV_PATH}")
        print("Run 'python scripts/tune_ga.py' first!")
        return
    
    df = pd.read_csv(CSV_PATH)
    
    print("\n" + "="*70)
    print("📊 GA TUNING RESULTS VISUALIZATION")
    print("="*70)
    
    # 1. Fitness Comparison
    create_bar_chart(
        df['Avg Fitness'].tolist(),
        df['Config'].tolist(),
        width=40,
        title="🎯 FITNESS SCORE COMPARISON (Higher is Better)"
    )
    
    # 2. Speed Comparison (inverse for visualization)
    speeds = (1 / df['Avg Time (s)']).tolist()
    create_bar_chart(
        speeds,
        df['Config'].tolist(),
        width=40,
        title="⚡ SPEED COMPARISON (Higher is Faster, in ops/sec)"
    )
    
    # 3. Efficiency
    create_bar_chart(
        df['Efficiency'].tolist(),
        df['Config'].tolist(),
        width=40,
        title="⚖️  EFFICIENCY (Fitness/Time, Higher is Better)"
    )
    
    # 4. Summary Table
    print("\n📋 DETAILED COMPARISON TABLE")
    print("="*70)
    
    # Select key columns
    summary = df[['Config', 'Pop Size', 'Generations', 'Mutation', 
                  'Avg Fitness', 'Avg Time (s)', 'Efficiency']]
    
    # Round for readability
    summary['Avg Fitness'] = summary['Avg Fitness'].round(2)
    summary['Avg Time (s)'] = summary['Avg Time (s)'].round(3)
    summary['Efficiency'] = summary['Efficiency'].round(0)
    
    print(summary.to_string(index=False))
    
    # 5. Recommendations
    print("\n" + "="*70)
    print("💡 QUICK GUIDE")
    print("="*70)
    
    best_fitness_idx = df['Avg Fitness'].idxmax()
    fastest_idx = df['Avg Time (s)'].idxmin()
    most_efficient_idx = df['Efficiency'].idxmax()
    
    print(f"\n🏆 Best Fitness:   {df.loc[best_fitness_idx, 'Config']}")
    print(f"   Score: {df.loc[best_fitness_idx, 'Avg Fitness']:.2f}")
    
    print(f"\n⚡ Fastest:        {df.loc[fastest_idx, 'Config']}")
    print(f"   Time: {df.loc[fastest_idx, 'Avg Time (s)']:.3f}s")
    
    print(f"\n⚖️  Most Efficient: {df.loc[most_efficient_idx, 'Config']}")
    print(f"   Efficiency: {df.loc[most_efficient_idx, 'Efficiency']:.0f}")
    
    # Parameter insights
    print("\n" + "="*70)
    print("📈 PARAMETER INSIGHTS")
    print("="*70)
    
    # Population Size effect
    pop_configs = df[df['Generations'] == 100].sort_values('Pop Size')
    if len(pop_configs) >= 2:
        print(f"\n📊 Population Size Impact (at 100 generations):")
        for _, row in pop_configs.iterrows():
            print(f"   Pop {int(row['Pop Size']):3d}: {row['Avg Time (s)']:.3f}s")
    
    # Generation effect
    gen_configs = df[df['Pop Size'] == 50].sort_values('Generations')
    if len(gen_configs) >= 2:
        print(f"\n⏱️  Generation Impact (at Pop=50):")
        for _, row in gen_configs.iterrows():
            print(f"   Gen {int(row['Generations']):3d}: {row['Avg Time (s)']:.3f}s")
    
    print("\n" + "="*70)
    print("✅ Analysis Complete!")
    print(f"📁 Full data: {CSV_PATH}")
    print("="*70)

if __name__ == "__main__":
    main()
