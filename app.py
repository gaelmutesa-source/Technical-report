import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import os

# --- 1. PDF GENERATOR (UPDATED FOR FUNDING ARGUMENT) ---
def create_pdf(lab_name, report_text, fig_bar, fig_line, fig_pie, funding_text):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Technical Report: {lab_name} Impact Analysis (2025-2026)", ln=True, align='C')
    pdf.ln(10)
    
    # Section 1: Economic Narrative
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "1. Economic Contribution Narrative", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 7, report_text)
    
    # Main Chart
    tmp_bar = "tmp_bar.png"
    fig_bar.savefig(tmp_bar, bbox_inches='tight')
    pdf.image(tmp_bar, x=15, y=None, w=170)
    os.remove(tmp_bar)
    
    # Section 2: Funding Justification (World Bank Focus)
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. Strategic Funding Justification (Stakeholder View)", ln=True)
    pdf.set_font("Arial", "I", 11)
    pdf.multi_cell(0, 7, funding_text)
    pdf.ln(5)
    
    # Secondary Charts
    tmp_line = "tmp_line.png"
    fig_line.savefig(tmp_line, bbox_inches='tight')
    pdf.image(tmp_line, x=10, y=None, w=90)
    os.remove(tmp_line)
    
    tmp_pie = "tmp_pie.png"
    fig_pie.savefig(tmp_pie, bbox_inches='tight')
    pdf.image(tmp_pie, x=110, y=105, w=85)
    os.remove(tmp_pie)
        
    return pdf.output(dest='S').encode('latin-1')

# --- 2. MAIN APP ---
def main():
    st.title("🇷🇼 RSB Metrology Economic Impact Portal")
    
    # --- SIDEBAR: NAVIGATION & LAB SELECTION ---
    st.sidebar.header("Global Configuration")
    target_lab = st.sidebar.selectbox("Select Target Laboratory", ["Dosimetry", "Mass", "Volume", "Thermometry"])
    
    uploaded_file = st.sidebar.file_uploader(f"Upload {target_lab} Lab Data (Excel)", type=["xlsx"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        rev_current = df['Revenue_2025'].sum()
        rev_previous = df['Revenue_2024'].sum()
        
        # Adjustable Benchmarks
        st.sidebar.subheader("Strategic Benchmarks")
        logistics_savings = st.sidebar.number_input("Logistics Savings (RWF)", value=15000000.0)
        assets_value = st.sidebar.number_input("Value of Supported Infrastructure (RWF)", value=12500000000.0)
        sector_gdp = st.sidebar.number_input("Sector GDP Contribution (RWF)", value=80000000000.0)
        certified_exports = st.sidebar.number_input("Export Value Enabled (RWF)", value=850000000.0)
        total_exports = st.sidebar.number_input("Total Sector Exports (RWF)", value=5000000000.0)

        # GDP Calculations
        dvr = ((rev_current + logistics_savings) / (rev_current + (logistics_savings * 1.5))) * 100
        ici = (assets_value / sector_gdp) * 100
        growth = ((rev_current - rev_previous) / rev_previous) * 100
        eef = (certified_exports / total_exports) * 100

        # --- DASHBOARD LAYOUT ---
        st.subheader(f"Dashboard: {target_lab} Laboratory Performance")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Domestic Retention", f"{dvr:.1f}%")
        m2.metric("Criticality Index", f"{ici:.1f}%")
        m3.metric("Growth Momentum", f"{growth:.1f}%", delta=f"{growth:.1f}%")
        m4.metric("Export Gatekeeper", f"{eef:.1f}%")

        st.divider()

        # Visuals
        col_main, col_side = st.columns([2, 1])
        with col_main:
            st.write("#### Total Economic Value Created")
            fig_bar, ax_bar = plt.subplots(figsize=(8, 4))
            ax_bar.bar(['Direct Rev', 'Logistics Saved', 'Export Enabled'], [rev_current, logistics_savings, certified_exports], color='#004C99')
            st.pyplot(fig_bar)

        with col_side:
            st.write("#### Revenue by Sector")
            fig_pie, ax_pie = plt.subplots(figsize=(5, 5))
            sector_data = df.groupby('Client_Sector')['Revenue_2025'].sum()
            ax_pie.pie(sector_data, labels=sector_data.index, autopct='%1.1f%%', colors=['#008080', '#DAA520', '#B22222'])
            st.pyplot(fig_pie)

        st.write("#### Historical Value Momentum")
        fig_line, ax_line = plt.subplots(figsize=(10, 2))
        ax_line.plot(["2024", "2025"], [rev_previous, rev_current], marker='s', color='#B22222')
        st.pyplot(fig_line)

        # --- FUNDING ARGUMENT (WORLD BANK LOGIC) ---
        report_text = f"The {target_lab} Lab provides a Domestic Value Retention of {dvr:.1f}%. It safeguards {assets_value:,.0f} RWF in infrastructure assets."
        
        funding_text = (
            f"STRATEGIC CASE FOR FUNDING: \n"
            f"The {target_lab} laboratory currently supports {ici:.1f}% of the targeted sector's national infrastructure. "
            f"Every 1 RWF invested in this lab protects approximately {assets_value/rev_current:.0f} RWF of active economic assets. "
            f"Lack of further investment will increase 'Quality Leakage' and force Rwandan industries to seek foreign alternatives, "
            f"harming the national Balance of Payments."
        )

        st.success("World Bank Funding Logic Generated Based on Data.")
        st.write(funding_text)

        # Download
        pdf_data = create_pdf(target_lab, report_text, fig_bar, fig_line, fig_pie, funding_text)
        st.download_button("📥 Download Technical Report + Funding Case", pdf_data, f"RSB_{target_lab}_Stakeholder_Report.pdf", "application/pdf")
    else:
        st.info(f"Please upload the {target_lab} Excel data file to generate analysis.")

if __name__ == "__main__":
    main()
