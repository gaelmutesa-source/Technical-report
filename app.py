import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import os

# --- PDF GENERATOR (UPDATED FOR NATIONAL SUMMARY) ---
def create_pdf(mode, lab_name, report_text, fig_bar, fig_line, fig_pie, funding_text):
    pdf = FPDF()
    pdf.add_page()
    title = f"National Metrology Impact Report (2025/26)" if mode == "National" else f"Lab Technical Report: {lab_name}"
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, title, ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "1. Executive Economic Summary", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 7, report_text)
    
    # Save chart 1
    tmp_bar = f"bar_{mode}.png"
    fig_bar.savefig(tmp_bar, bbox_inches='tight')
    pdf.image(tmp_bar, x=15, y=None, w=170)
    os.remove(tmp_bar)
    
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. Strategic Stakeholder Case", ln=True)
    pdf.set_font("Arial", "I", 11)
    pdf.multi_cell(0, 7, funding_text)
    
    tmp_pie = f"pie_{mode}.png"
    fig_pie.savefig(tmp_pie, bbox_inches='tight')
    pdf.image(tmp_pie, x=50, y=None, w=110)
    os.remove(tmp_pie)
        
    return pdf.output(dest='S').encode('latin-1')

def main():
    st.set_page_config(page_title="RSB National Metrology Portal", layout="wide")
    st.title("🇷🇼 RSB National Metrology Impact Portal")
    
    # --- NAVIGATION ---
    mode = st.sidebar.radio("Reporting Mode", ["Individual Lab", "National Summary"])
    
    if mode == "Individual Lab":
        target_lab = st.sidebar.selectbox("Select Laboratory", ["Dosimetry", "Mass", "Volume", "Thermometry"])
    else:
        target_lab = "National Metrology Division"

    uploaded_file = st.sidebar.file_uploader(f"Upload {target_lab} Data (Excel)", type=["xlsx"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        rev_2025 = df['Revenue_2025'].sum()
        rev_2024 = df['Revenue_2024'].sum()
        
        # Benchmarks
        logistics_saved = st.sidebar.number_input("Total Logistics Saved (RWF)", value=50000000.0 if mode=="National" else 15000000.0)
        infra_value = st.sidebar.number_input("Value of Assets Supported (RWF)", value=150000000000.0 if mode=="National" else 12500000000.0)
        sector_gdp = st.sidebar.number_input("Total Sector GDP (RWF)", value=500000000000.0 if mode=="National" else 80000000000.0)

        # Core Calculations
        dvr = ((rev_2025 + logistics_saved) / (rev_2025 + (logistics_saved * 1.5))) * 100
        growth = ((rev_2025 - rev_2024) / rev_2024) * 100
        criticality = (infra_value / sector_gdp) * 100

        # --- DASHBOARD ---
        st.subheader(f"{target_lab} Impact Dashboard")
        c1, c2, c3 = st.columns(3)
        c1.metric("Domestic Retention", f"{dvr:.1f}%")
        c2.metric("YoY Growth", f"{growth:.1f}%")
        c3.metric("GDP Criticality", f"{criticality:.1f}%")

        # --- VISUALS ---
        col_l, col_r = st.columns(2)
        with col_l:
            fig_bar, ax_bar = plt.subplots(figsize=(7, 4))
            # If National, show revenue by Lab. If Individual, show total.
            if mode == "National" and 'Lab_Name' in df.columns:
                lab_revs = df.groupby('Lab_Name')['Revenue_2025'].sum()
                lab_revs.plot(kind='bar', ax=ax_bar, color='#1f77b4')
                ax_bar.set_title("Revenue Contribution per Laboratory")
            else:
                ax_bar.bar(['2024', '2025'], [rev_2024, rev_2025], color=['#aec7e8', '#1f77b4'])
                ax_bar.set_title("Annual Revenue Momentum")
            st.pyplot(fig_bar)

        with col_r:
            fig_pie, ax_pie = plt.subplots(figsize=(5, 5))
            group_col = 'Lab_Name' if (mode == "National" and 'Lab_Name' in df.columns) else 'Client_Sector'
            sector_data = df.groupby(group_col)['Revenue_2025'].sum()
            ax_pie.pie(sector_data, labels=sector_data.index, autopct='%1.1f%%', colors=['#2ca02c', '#ff7f0e', '#d62728', '#9467bd'])
            ax_pie.set_title("Economic Distribution")
            st.pyplot(fig_pie)

        # --- WORLD BANK ARGUMENT ---
        funding_text = (
            f"The {target_lab} currently underpins {criticality:.1f}% of the sectors it serves. "
            f"By domesticating these standards, RSB prevents a 'Quality Leakage' where local firms "
            f"would otherwise spend foreign currency abroad. Our current Asset-to-Revenue ratio shows "
            f"that for every 1 RWF in lab fees, we protect {infra_value/rev_2025:.0f} RWF of Rwandan infrastructure."
        )
        st.info(funding_text)

        # PDF Download
        pdf_data = create_pdf(mode, target_lab, f"Summary of impact for {target_lab}.", fig_bar, fig_bar, fig_pie, funding_text)
        st.download_button("📥 Download PDF Report", pdf_data, f"RSB_{mode}_Report.pdf", "application/pdf")

if __name__ == "__main__":
    main()
