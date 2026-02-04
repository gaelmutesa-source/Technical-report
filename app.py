import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import io

# --- CONFIGURATION ---
st.set_page_config(page_title="RSB Metrology Economic Impact Reporter", layout="wide")

def create_pdf(year, report_text, fig_bar, fig_line, fig_pie):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Technical Report: Dosimetry Laboratory Impact ({year})", ln=True, align='C')
    pdf.ln(10)
    
    # Executive Summary
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Economic Contribution Narrative", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 8, report_text)
    pdf.ln(5)
    
    # Add Visuals - Page 1
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp1:
        fig_bar.savefig(tmp1.name, format="png", bbox_inches='tight')
        pdf.image(tmp1.name, x=10, y=None, w=180)
    
    # Add Visuals - Page 2
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Growth Momentum & Sectoral Distribution", ln=True)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp2:
        fig_line.savefig(tmp2.name, format="png", bbox_inches='tight')
        pdf.image(tmp2.name, x=10, y=None, w=100)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp3:
        fig_pie.savefig(tmp3.name, format="png", bbox_inches='tight')
        pdf.image(tmp3.name, x=110, y=None, w=90)
        
    return pdf.output(dest='S').encode('latin-1')

def main():
    st.title("📊 RSB Metrology Economic Impact Reporter")
    st.markdown("### Pilot Phase: Dosimetry Laboratory")

    # --- SIDEBAR: DATA SOURCE ---
    st.sidebar.header("Data Management")
    uploaded_file = st.sidebar.file_uploader("Upload Lab Data (Excel)", type=["xlsx"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        
        # Calculate Revenues from Sheet
        rev_current = df['Revenue_2025'].sum()
        rev_previous = df['Revenue_2024'].sum()
        
        # Economic Benchmarks
        st.sidebar.subheader("Economic Benchmarks")
        logistics_savings = st.sidebar.number_input("Logistics Savings (RWF)", value=15000000.0)
        assets_value = st.sidebar.number_input("Value of Calibrated Assets (RWF)", value=12500000000.0)
        sector_gdp = st.sidebar.number_input("National Sector GDP (RWF)", value=80000000000.0)
        certified_exports = st.sidebar.number_input("Certified Export Value (RWF)", value=850000000.0)
        total_exports = st.sidebar.number_input("Total Sector Exports (RWF)", value=5000000000.0)

        # --- GDP FORMULAS (CONSISTENT) ---
        dvr = ((rev_current + logistics_savings) / (rev_current + (logistics_savings * 1.5))) * 100
        ici = (assets_value / sector_gdp) * 100
        growth = ((rev_current - rev_previous) / rev_previous) * 100
        eef = (certified_exports / total_exports) * 100

        # --- KEY METRICS ---
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Domestic Retention", f"{dvr:.1f}%")
        m2.metric("Criticality Index", f"{ici:.1f}%")
        m3.metric("Revenue Growth", f"{growth:.1f}%", delta=f"{growth:.1f}%")
        m4.metric("Export Enablement", f"{eef:.1f}%")

        st.divider()

        # --- VISUALIZATIONS ---
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.write("#### Economic Value Added (RWF)")
            fig_bar, ax_bar = plt.subplots(figsize=(8, 5))
            ax_bar.bar(['Direct Revenue', 'Logistics Saved', 'Export Support'], 
                       [rev_current, logistics_savings, certified_exports], 
                       color=['#003366', '#2E8B57', '#CD7F32'])
            st.pyplot(fig_bar)

        with col2:
            st.write("#### Lab Momentum")
            fig_line, ax_line = plt.subplots(figsize=(5, 5))
            ax_line.plot(["2024", "2025"], [rev_previous, rev_current], marker='o', color='#003366', linewidth=3)
            st.pyplot(fig_line)

        with col3:
            st.write("#### Sector Breakdown")
            fig_pie, ax_pie = plt.subplots(figsize=(5, 5))
            sector_data = df.groupby('Client_Sector')['Revenue_2025'].sum()
            ax_pie.pie(sector_data, labels=sector_data.index, autopct='%1.1f%%', startangle=140, colors=['#5DADE2', '#48C9B0', '#F4D03F'])
            st.pyplot(fig_pie)

        # --- REPORT GENERATION ---
        report_text = (
            f"The Dosimetry Lab achieved a {growth:.1f}% growth in revenue for 2025. "
            f"By localizing these services, RSB ensures a Domestic Value Retention of {dvr:.1f}%, "
            f"protecting assets worth {assets_value:,.0f} RWF and supporting {certified_exports:,.0f} RWF in exports."
        )

        st.info(report_text)

        pdf_data = create_pdf(2025, report_text, fig_bar, fig_line, fig_pie)
        st.download_button("📥 Download Technical Report (PDF)", pdf_data, "RSB_Dosimetry_Report.pdf", "application/pdf")
    else:
        st.warning("Please upload 'rsb_dosimetry_data.xlsx' to view analysis.")

if __name__ == "__main__":
    main()
