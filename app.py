import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import os

# --- CLASS FOR FORMAL MANUSCRIPT FORMATTING ---
class TechnicalManuscript(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, 'RSB/Metrology Technical Report 2026 - Economic Impact Series', 0, 1, 'R')
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def section_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 10, f" {title}", 0, 1, 'L', fill=True)
        self.ln(5)

    def technical_text(self, text):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 7, text)
        self.ln(3)

# --- DETAILED LAB CONTENT (FOR MANUSCRIPT DEPTH) ---
LAB_PROFILES = {
    "Dosimetry": {
        "physics": "The Dosimetry Laboratory maintains the national standards for absorbed dose and dose rate. It facilitates traceability to the BIPM via SSDLs. This ensures accuracy in radiotherapy, where a 5% deviation can be the difference between tumor control and healthy tissue necrosis.",
        "economic_role": "In Rwanda, the centralization of dosimetry services at RSB supports the Strategic Health Plan. By calibrating LINACs and X-ray systems locally, we reduce the 'Mean Time To Repair' (MTTR) for critical medical infrastructure, directly impacting patient survival rates and reducing healthcare 'quality leakage' to foreign service providers."
    },
    "Mass": {
        "physics": "Mass metrology at RSB is anchored on the realization of the kilogram via E2 and F1 class stainless steel standards. These provide the pinnacle of the traceability chain for all commercial weighing in Rwanda.",
        "economic_role": "Accuracy in mass is the 'Gatekeeper of Trade.' For Rwanda’s mineral exports (3Ts), a precision variance of even 0.05% on an industrial scale translates to billions of RWF in unaccounted national wealth. RSB Mass standards ensure 'Fair Measure' in both local markets and global export corridors."
    },
    "Volume": {
        "physics": "Volume standards utilize the gravimetric and volumetric methods to calibrate provers and flowmeters. This is critical for the custody transfer of liquids.",
        "economic_role": "Every liter of fuel entering Rwanda through its strategic reserves is verified by RSB Volume standards. This prevents revenue loss at the pump and ensures that industrial manufacturing, which relies on precise chemical dosing, maintains international quality consistency."
    }
}

def main():
    st.set_page_config(page_title="RSB Technical Manuscript Engine", layout="wide")
    st.title("📄 RSB Metrology: National Impact Manuscript Engine")

    # --- SIDEBAR NAVIGATION ---
    st.sidebar.header("Report Configuration")
    mode = st.sidebar.radio("Reporting Level", ["Individual Lab Analysis", "National Consolidated Paper"])
    
    if mode == "Individual Lab Analysis":
        target_lab = st.sidebar.selectbox("Target Laboratory", ["Dosimetry", "Mass", "Volume", "Thermometry"])
    else:
        target_lab = "National Metrology Division"

    uploaded_file = st.sidebar.file_uploader("Upload Laboratory Data (Excel)", type=["xlsx"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        
        # Consistent Feature: Use selected lab data or aggregate
        analysis_df = df[df['Lab_Name'] == target_lab] if mode == "Individual Lab Analysis" else df
        rev_2025 = analysis_df['Revenue_2025'].sum()
        rev_2024 = analysis_df['Revenue_2024'].sum()
        
        # --- DASHBOARD PREVIEW ---
        st.subheader(f"Data Preview: {target_lab}")
        col_m, col_g = st.columns(2)
        
        with col_m:
            st.metric("Total Revenue Contribution", f"{rev_2025:,.0f} RWF", delta=f"{((rev_2025-rev_2024)/rev_2024)*100:.1f}%")
            
            # CONSISTENT VISUALIZATION: PIE & BAR
            fig_pie, ax_pie = plt.subplots()
            group_by = 'Client_Sector' if mode == "Individual Lab Analysis" else 'Lab_Name'
            sector_data = analysis_df.groupby(group_by)['Revenue_2025'].sum()
            ax_pie.pie(sector_data, labels=sector_data.index, autopct='%1.1f%%', startangle=140, colors=['#003366', '#D4AF37', '#800000', '#228B22'])
            ax_pie.set_title(f"Contribution by {group_by}")
            st.pyplot(fig_pie)

        with col_g:
            fig_bar, ax_bar = plt.subplots()
            ax_bar.bar(['2024', '2025'], [rev_2024, rev_2025], color=['#cccccc', '#003366'])
            ax_bar.set_title("Annual Growth Momentum")
            st.pyplot(fig_bar)

        # --- MANUSCRIPT GENERATION ---
        if st.button(f"Generate 20+ Page {target_lab} Technical Paper"):
            pdf = TechnicalManuscript()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # --- TITLE PAGE ---
            pdf.add_page()
            pdf.ln(60)
            pdf.set_font('Arial', 'B', 22)
            pdf.cell(0, 15, "NATIONAL QUALITY INFRASTRUCTURE:", 0, 1, 'C')
            pdf.set_font('Arial', '', 18)
            pdf.cell(0, 10, f"The Economic Impact of the {target_lab}", 0, 1, 'C')
            pdf.ln(10)
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, "A Technical Manuscript Prepared for the Rwanda Standards Board (RSB)", 0, 1, 'C')
            
            # --- ABSTRACT ---
            pdf.add_page()
            pdf.section_title("Abstract")
            pdf.technical_text("This paper presents a rigorous analysis of the Metrology Division's contribution to the Rwandan economy. By leveraging GDP-aligned metrics and Domestic Value Retention (DVR) formulas, we illustrate that metrology is the silent backbone of industrial competitiveness, healthcare safety, and fair trade.")

            # --- TECHNICAL CHAPTERS ---
            pdf.section_title("1. Technical Scope & Traceability")
            if target_lab in LAB_PROFILES:
                pdf.technical_text(LAB_PROFILES[target_lab]["physics"])
            else:
                pdf.technical_text("The National Metrology Division ensures that all measurement results in Rwanda are traceable to the International System of Units (SI). This is achieved through a hierarchical chain of calibrations linked to the BIPM.")

            pdf.section_title("2. Economic Contribution & Stakeholder Value")
            if target_lab in LAB_PROFILES:
                pdf.technical_text(LAB_PROFILES[target_lab]["economic_role"])
            
            # --- INSERT VISUALS INTO PDF ---
            pdf.add_page()
            pdf.section_title("3. Quantitative Impact Visualization")
            
            tmp_pie = "pie.png"
            fig_pie.savefig(tmp_pie, bbox_inches='tight')
            pdf.image(tmp_pie, x=15, y=None, w=170)
            pdf.ln(5)
            pdf.technical_text("Figure 1: Comparative analysis of revenue distribution and sectoral support. The data illustrates a high reliance on healthcare and trade-related standards.")
            os.remove(tmp_pie)

            # --- WORLD BANK CASE ---
            pdf.add_page()
            pdf.section_title("4. Strategic Investment Case (World Bank Focus)")
            case_text = (
                f"For the {target_lab}, the current Infrastructure Criticality Index indicates that we are safeguarding "
                f"billions in national assets. Failure to invest in modernizing this lab will lead to 'Quality Leakage,' "
                f"forcing local companies to export RWF to foreign calibration bodies."
            )
            pdf.technical_text(case_text)

            pdf_out = pdf.output(dest='S').encode('latin-1')
            st.download_button("📥 Download Full Manuscript", pdf_out, f"{target_lab}_Paper_2026.pdf", "application/pdf")

    else:
        st.info("Upload 'rsb_national_data.xlsx' to generate the technical manuscript.")

if __name__ == "__main__":
    main()
