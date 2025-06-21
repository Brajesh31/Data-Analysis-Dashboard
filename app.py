import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_data():
    """Prompt user for Excel file path and load data."""
    while True:
        file_path = input("Enter Excel file path (.xlsx): ").strip()
        try:
            df = pd.read_excel(file_path)
            print("File loaded successfully.")
            return df, file_path
        except FileNotFoundError:
            print("Error: File not found. Please try again.")
        except Exception as e:
            print(f"Error loading file: {str(e)}")

def handle_nulls(df):
    """Handle null values in the DataFrame with user-selected method."""
    null_counts = df.isnull().sum()
    print("\nNull values per column:")
    print(null_counts[null_counts > 0] if null_counts.any() else "No null values found")
    
    if null_counts.sum() > 0:
        choice = input("\nDo you want to handle null values? (yes/no): ").lower()
        if choice == 'yes':
            print("\nFill methods: 0) Zero fill 1) Mean 2) Median 3) Forward fill 4) Backward fill")
            method = input("Select fill method (0-4): ")
            
            try:
                if method == '0':
                    df = df.fillna(0)
                elif method == '1':
                    df = df.fillna(df.select_dtypes(include='number').mean())
                elif method == '2':
                    df = df.fillna(df.select_dtypes(include='number').median())
                elif method == '3':
                    df = df.ffill()
                elif method == '4':
                    df = df.bfill()
                else:
                    print("Invalid selection. No changes made.")
            except Exception as e:
                print(f"Error filling nulls: {str(e)}")
    return df

def basic_understanding(df):
    """Provide basic data exploration and statistics."""
    print("\n=== Basic Data Understanding ===")
    print(f"Dataset shape: {df.shape}")
    
    print("\nFirst 5 rows:")
    print(df.head())
    
    print("\nData types:")
    print(df.dtypes)
    
    print("\nSummary statistics:")
    print(df.describe(include='all'))
    
    df = handle_nulls(df)
    return df

def select_columns(df):
    """Interactive column selection for visualization."""
    print("\nAvailable columns:")
    print(df.columns.tolist())
    
    id_col = input("Select ID column: ").strip()
    while id_col not in df.columns:
        print("Invalid column. Try again.")
        id_col = input("Select ID column: ").strip()
    
    value_cols = []
    while not value_cols:
        selected = input("Select value columns (comma-separated): ").split(',')
        value_cols = [col.strip() for col in selected if col.strip() in df.columns]
        if not value_cols:
            print("No valid columns selected. Try again.")
    
    return id_col, value_cols

def create_visualizations(df, id_col, value_cols):
    """Generate various visualizations based on user input."""
    df = df.copy()
    df['Total'] = df[value_cols].sum(axis=1)
    
    try:
        n = int(input("Number of top entries to display (default 4): ") or 4)
    except ValueError:
        n = 4
    top_df = df.nlargest(n, 'Total')

    print("\nVisualization options:")
    print("1. Subplots      2. Grouped Bars")
    print("3. Horizontal Bars 4. Pie Chart")
    choice = input("Select visualization (1-4): ").strip()

    plt.figure(figsize=(12, 7))
    sns.set_theme(style="whitegrid")
    palette = sns.color_palette("husl", len(value_cols))

    try:
        if choice == '1':
            rows = (n + 1) // 2
            fig, axes = plt.subplots(rows, 2, figsize=(14, rows*5))
            axes = axes.flatten()
            
            for idx, (_, row) in enumerate(top_df.iterrows()):
                ax = axes[idx]
                row[value_cols].plot(kind='bar', ax=ax, color=palette)
                ax.set_title(f"{id_col}: {row[id_col]}")
                ax.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plt.suptitle("Top Entries - Individual Breakdown", y=1.02)
            plt.savefig('subplots.png', bbox_inches='tight')

        elif choice == '2':
            melted_df = top_df.melt(id_vars=id_col, value_vars=value_cols)
            sns.barplot(x=id_col, y='value', hue='variable', data=melted_df, palette=palette)
            plt.title("Top Entries - Grouped Comparison")
            plt.ylabel("Values")
            plt.legend(title='Metrics', bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.savefig('grouped_bars.png', bbox_inches='tight')

        elif choice == '3':
            top_df.set_index(id_col)[value_cols].plot(kind='barh', stacked=True, color=palette)
            plt.title("Top Entries - Horizontal Breakdown")
            plt.xlabel("Total Values")
            plt.savefig('horizontal_bars.png', bbox_inches='tight')

        elif choice == '4':
            plt.pie(top_df['Total'], labels=top_df[id_col], autopct='%1.1f%%', 
                    startangle=90, colors=palette, wedgeprops={'edgecolor': 'white'})
            plt.title("Top Entries - Total Distribution")
            plt.savefig('pie_chart.png', bbox_inches='tight')

        else:
            print("Invalid choice. No visualization created.")
            return

        plt.show()

    except Exception as e:
        print(f"Visualization error: {str(e)}")

def main():
    """Main application workflow."""
    df = None
    current_file = None
    
    while True:
        print("\n=== Data Analysis Dashboard ===")
        if df is not None:
            print(f"Loaded: {current_file} ({df.shape[0]} rows)")
        print("1. Load Data")
        print("2. Basic Analysis")
        print("3. Create Visualizations")
        print("4. Exit")

        choice = input("Select option (1-4): ").strip()

        if choice == '1':
            new_df, new_file = load_data()
            if new_df is not None:
                df = new_df
                current_file = new_file
                
        elif choice == '2':
            if df is not None:
                df = basic_understanding(df)
            else:
                print("Please load data first!")
                
        elif choice == '3':
            if df is not None:
                id_col, value_cols = select_columns(df)
                create_visualizations(df, id_col, value_cols)
            else:
                print("Please load data first!")
                
        elif choice == '4':
            print("Exiting program. Goodbye!")
            break
            
        else:
            print("Invalid selection. Please try again.")

if __name__ == "__main__":
    main()