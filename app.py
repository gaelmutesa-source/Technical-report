import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import io
import tempfile

# --- CONFIGURATION ---
st.set_page_config(page_title="RSB Metrology Economic Impact Reporter", layout="wide")

def create_pdf(year, report_text, fig1, fig2):
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Technical Report: Dosimetry Laboratory Impact ({year})", ln=True, align='C')
    pdf.ln(10)
    
    # Executive Summary & Narrative
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Executive Summary & Economic Narrative", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 10, report_text)
    pdf.ln(5)
    
    # Save Matplotlib figures to temporary files to embed in PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp1:
        fig1.savefig(tmp1.name, format="png", bbox_inches='tight')
        pdf.image(tmp1.name, x=10, y=None, w=180)
    
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Economic Momentum & Growth Analysis", ln=True)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp2:
        fig2.savefig(tmp2.name, format="png", bbox_inches='tight')
        pdf.image(tmp2.name, x=10, y=None, w=180)
        
    return pdf.output(dest='S').encode('latin-1')

def generate_report():
    st.title("📊 Metrology Economic Impact Reporter")
    st.subheader("Pilot Lab: Dosimetry Laboratory (RSB)")

    with st.sidebar:
        st.header("1. Lab Data Input")
        year = st.selectbox("Select Reporting Year", [2024, 2025, 2026])
        rev_current = st.number_input("Current Year Revenue (RWF)", min_value=0.0, value=50000000.0)
        rev_previous = st.number_input("Previous Year Revenue (RWF)", min_value=0.0, value=42000000.0)
        logistics_savings = st.number_input("Logistics Savings (RWF)", value=15000000.0)
        assets_value = st.number_input("Value of Calibrated Assets (RWF)", value=1200000000.0)
        sector_gdp = st.number_input("Sector GDP (RWF)", value=8000000000.0)
        certified_exports = st.number_input("Certified Export Value (RWF)", value=300000000.0)
        total_exports = st.number_input("Total Sector Exports (RWF)", value=2500000000.0)

    # Formula Calculations
    dvr = ((rev_current + logistics_savings) / (rev_current + (logistics_savings * 1.5))) * 100
    ici = (assets_value / sector_gdp) * 100
    growth = ((rev_current - rev_previous) / rev_previous) * 100
    eef = (certified_exports / total_exports) * 100

    # Display Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Domestic Retention", f"{dvr:.1f}%")
    m2.metric("Criticality Index", f"{ici:.1f}%")
    m3.metric("Revenue Growth", f"{growth:.1f}%")
    m4.metric("Export Enablement", f"{eef:.1f}%")

    # Generate Figures for Display and PDF
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    ax1.bar(['Direct Revenue', 'Logistics Saved', 'Export Value Supported'], [rev_current, logistics_savings, certified_exports], color=['#1f77b4', '#2ca02c', '#ff7f0e'])
    ax1.set_title("Economic Value Added")

    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.plot([year-2, year-1, year], [rev_previous*0.8, rev_previous, rev_current], marker='o', color='green')
    ax2.set_title("Economic Impact Momentum")

    st.pyplot(fig1)
    st.pyplot(fig2)

    report_text = f"In {year}, the Dosimetry Lab achieved {growth:.1f}% revenue growth. By domesticating services, RSB ensures a Domestic Value Retention of {dvr:.1f}%, protecting assets worth {assets_value:,.0f} RWF ({ici:.1f}% of sector GDP) and enabling {certified_exports:,.0f} RWF in exports."

    # PDF Download Button
    pdf_data = create_pdf(year, report_text, fig1, fig2)
    st.download_button(
        label="📥 Download Technical Report (PDF)",
        data=pdf_data,
        file_name=f"RSB_Dosimetry_Report_{year}.pdf",
        mime="application/pdf"
    )

if __name__ == "__main__":
    generate_report()
