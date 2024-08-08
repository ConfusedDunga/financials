import streamlit as st
import pandas as pd
from io import BytesIO

# Load data from a predefined Excel file path
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    return df

# Aggregate data
def aggregate_data(df):
    aggregated_data = df.groupby('Date').agg({
        'LOANS AND ADV': 'sum',
        'TOTAL ASSETS': 'sum',
        'DEPOSITS FROM CUSTOMERS': 'sum',
        'DEPOSITS FROM CUSTOMERS & BFI': 'sum',
        'DEBT SECURITIES': 'sum',
        'PAID UP CAPITAL': 'sum',
        'TOTAL EQUITY': 'sum',
        'INTEREST INCOME': 'sum',
        'INTEREST EXPENSES': 'sum',
        'NET INTEREST INCOME': 'sum',
        'NET FEE & COM INCOME': 'sum',
        'NET TRADING INCOME': 'sum',
        'OTHER OPERATING INCOME': 'sum',
        'TOTAL OPERATING INCOME': 'sum',
        'IMPAIRMENT CHARGE': 'sum',
        'PERSONNEL EXPENSES': 'sum',
        'BONUS': 'sum',
        'STAFF EXPENSES': 'sum',
        'OTHER OP EXP & DEP AMO': 'sum',
        'OPERATING PROFIT BEFORE IMP PR': 'sum',
        'NET NON OPERATING INCOME': 'sum',
        'OPERATING PROFIT AFTER IMP PR': 'sum',
        'PROFIT BEFORE INCOME TAX': 'sum',
        'INCOME TAX': 'sum',
        'PROFIT AFTER TAX (NET PROFIT)': 'sum',
        'DISTRIBUTABLE PROFIT': 'sum',
        'BASIC EPS': 'mean',
        'CAPITAL FUND TO RWA': 'mean',
        'NPL': 'mean',
        'COST OF FUNDS': 'mean',
        'ROE': 'mean',
        'CD RATIO': 'mean',
        'BASE RATE': 'mean',
        'SPREAD RATE': 'mean',
        'LIQUIDITY': 'mean',
        'NET WORTH PER SHARE': 'mean'
    }).reset_index()

    pivoted_data = aggregated_data.melt(id_vars=['Date'], var_name='Metric', value_name='Value')
    report = pivoted_data.pivot(index='Metric', columns='Date', values='Value')

    return report


balance_sheet_metrics = [
    'LOANS AND ADV', 'TOTAL ASSETS', 'DEPOSITS FROM CUSTOMERS', 'DEPOSITS FROM CUSTOMERS & BFI', 
    'DEBT SECURITIES', 'PAID UP CAPITAL', 'TOTAL EQUITY'
]
pl_metrics = [
    'INTEREST INCOME', 'INTEREST EXPENSES', 'NET INTEREST INCOME', 'NET FEE & COM INCOME', 
    'NET TRADING INCOME', 'OTHER OPERATING INCOME', 'TOTAL OPERATING INCOME', 'IMPAIRMENT CHARGE',
    'PERSONNEL EXPENSES', 'BONUS', 'STAFF EXPENSES', 'OTHER OP EXP & DEP AMO', 
    'OPERATING PROFIT BEFORE IMP PR', 'NET NON OPERATING INCOME', 'OPERATING PROFIT AFTER IMP PR',
    'PROFIT BEFORE INCOME TAX', 'INCOME TAX', 'PROFIT AFTER TAX (NET PROFIT)', 'DISTRIBUTABLE PROFIT'
]
ratios_metrics = [
    'CAPITAL FUND TO RWA', 'NPL', 'COST OF FUNDS', 'CD RATIO', 'BASE RATE', 'SPREAD RATE', 'ROE',
    'LIQUIDITY', 'NET WORTH PER SHARE','BASIC EPS'
]

# Define metrics order
metric_order = balance_sheet_metrics + pl_metrics + ratios_metrics

def filter_metrics(df, metrics):
    # Reorder metrics as per original order
    metric_ordered = [metric for metric in metric_order if metric in metrics]
    return df[df['Metric'].isin(metrics)].set_index('Metric').reindex(metric_ordered)

def calculate_changes(report, date1, date2):
    # Ensure the columns are ordered correctly
    if date1 not in report.columns or date2 not in report.columns:
        return report

    # Reorder columns
    report = report[[date1, date2]]
    
    # Calculate change and percentage change
    report['Change'] = report[date2] - report[date1]
    report['Percentage Change'] = (report['Change'] / report[date1]) * 100
    return report

def compare_banks(df):
    st.header("Compare Banks")

    # Select banks and date for comparison
    banks = df['Bank name'].unique()
    dates = df['Date'].unique()
    
    selected_date = st.selectbox("Select Date", dates)
    selected_banks = st.multiselect("Select Banks", banks)

    if selected_banks and selected_date:
        filtered_df = df[(df['Bank name'].isin(selected_banks)) & (df['Date'] == selected_date)]
        
        # Convert the DataFrame to long format with metrics as rows
        long_df = filtered_df.melt(
            id_vars=['Date', 'Bank name'],
            value_vars=metric_order,
            var_name='Metric',
            value_name='Value'
        )
        
        comparison_report = long_df.pivot(index='Metric', columns='Bank name', values='Value')
        st.dataframe(comparison_report, use_container_width=True)

        # Option to download the comparison report
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            comparison_report.to_excel(writer, index=True, sheet_name='Bank Comparison Report')
        st.download_button(
            label="Download Bank Comparison Report",
            data=excel_buffer.getvalue(),
            file_name="bank_comparison_report.xlsx"
        )

def metric_breakdown(df):
    st.header("Metric-wise Breakdown")

    # Select metric
    selected_metric = st.selectbox("Select Metric", metric_order)

    # Allow multiple date selections
    selected_dates = st.multiselect("Select Dates", df['Date'].unique())

    if selected_metric and selected_dates:
        # Filter data based on selected metric and dates
        filtered_df = df[df['Date'].isin(selected_dates)]
        metric_data = filtered_df.pivot_table(
            index='Bank name', 
            columns='Date', 
            values=selected_metric
        )

        if len(selected_dates) == 2:
            # Calculate change and percentage change
            comparison_report = calculate_changes(metric_data, selected_dates[0], selected_dates[1])
            st.dataframe(comparison_report, use_container_width=True)

            # Option to download the comparison report
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                comparison_report.to_excel(writer, index=True, sheet_name='Metric Breakdown Report')
            st.download_button(
                label="Download Metric Breakdown Report",
                data=excel_buffer.getvalue(),
                file_name="metric_breakdown_report.xlsx"
            )
        else:
            st.dataframe(metric_data, use_container_width=True)
            
            # Option to download the report
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                metric_data.to_excel(writer, index=True, sheet_name='Metric Breakdown Report')
            st.download_button(
                label="Download Metric Breakdown Report",
                data=excel_buffer.getvalue(),
                file_name="metric_breakdown_report.xlsx"
            )

# Main Streamlit app
def main():
    st.title("Banking Metrics Dashboard")

    # Load data
    file_path = "data.csv"  # Replace with your actual file path
    df = load_data(file_path)

    # Navigation
    page = st.sidebar.selectbox("Choose a page", ["Industry Overview", "Compare Banks", "Metric Breakdown"])

    if page == "Industry Overview":
        st.header("Industry Overview")

        # Filter by metrics type
        metric_type = st.selectbox("Select Metric Type", ["All", "Balance Sheet", "Profit and Loss", "Ratios"])
        if metric_type == "Balance Sheet":
            selected_metrics = balance_sheet_metrics
        elif metric_type == "Profit and Loss":
            selected_metrics = pl_metrics
        elif metric_type == "Ratios":
            selected_metrics = ratios_metrics
        else:  # "All" option
            selected_metrics = metric_order

        # Allow multiple date selections
        selected_dates = st.multiselect("Select Dates", df['Date'].unique())

        # Filter and display based on the number of selected dates
        if len(selected_dates) >= 1:
            filtered_df = df[df['Date'].isin(selected_dates)]
            aggregated_report = aggregate_data(filtered_df)
            filtered_report = filter_metrics(aggregated_report.reset_index(), selected_metrics)

            if len(selected_dates) == 2:
                # Calculate change and percentage change
                comparison_report = calculate_changes(filtered_report, selected_dates[0], selected_dates[1])
                st.dataframe(comparison_report, use_container_width=True)

                # Option to download the comparison report
                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    comparison_report.to_excel(writer, index=True, sheet_name='Comparison Report')
                st.download_button(
                    label="Download Comparison Report",
                    data=excel_buffer.getvalue(),
                    file_name="comparison_report.xlsx"
                )
            else:
                # Display filtered data without changes
                st.dataframe(filtered_report, use_container_width=True)
                
                # Option to download the report
                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    filtered_report.to_excel(writer, index=True, sheet_name='Filtered Report')
                st.download_button(
                    label="Download Filtered Report",
                    data=excel_buffer.getvalue(),
                    file_name="filtered_report.xlsx"
                )

    elif page == "Compare Banks":
        compare_banks(df)
    
    elif page == "Metric Breakdown":
        metric_breakdown(df)

if __name__ == "__main__":
    main()
