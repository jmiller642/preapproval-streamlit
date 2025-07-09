import streamlit as st
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
import os

# Loan officer dictionary
loan_officers = {
    "Danny Davis": {
        "title": "Sr. Loan Officer",
        "nmls": "115481",
        "phone": "(919) 447-3377 (Office)",
        "email": "ddavis@millerlending.com",
        "signature": "danny_signature.png"
    },
}

def generate_letter_pdf(data, logo_path):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=40
    )

    elements = []
    styles = getSampleStyleSheet()

    # Larger font for better page fill
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=11, leading=15)
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, leading=12)

    # --- Logo (refined proportions and spacing) ---
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=1.8*inch, height=0.7*inch)  # proportionally correct
        logo.hAlign = 'LEFT'
        elements.append(Spacer(1, -25))
        elements.append(logo)
        elements.append(Spacer(1, 18))

    # --- Letter Body ---
    elements.append(Paragraph(f"Dear <b>{data['borrower_name']},</b>", normal_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("<b>RE: Loan Pre-Approval</b>", normal_style))
    elements.append(Spacer(1, 12))

    intro = (
        "Congratulations! I am pleased to inform that based on your recently pulled credit report, "
        "a review of your income and asset documentation, you have been pre-approved for a mortgage loan "
        "subject to the following terms and conditions:"
    )
    elements.append(Paragraph(intro, normal_style))
    elements.append(Spacer(1, 12))

    loan_info = f"""
        Purchase Price:\t${data['purchase_price']:,.0f}<br/>
        Loan Type:\t{data['loan_type']}<br/>
        Down Payment:\t{data['down_payment']}%<br/>
        Interest Rate:\t{data['interest_rate']}%<br/>
        Property Address:\t{data['property_address']}
    """
    elements.append(Paragraph(loan_info, normal_style))
    elements.append(Spacer(1, 12))

    conditions = (
        "Final approval for the loan requires:<br/><br/>"
        "• Underwriter review and approval of all documentation and required information, including credit, income and assets, and a purchase contract;<br/>"
        "• Acceptable appraisal and title commitment;<br/>"
        "• Your financial status and credit report to remain substantially the same until the loan closes."
    )
    elements.append(Paragraph(conditions, normal_style))
    elements.append(Spacer(1, 12))

    closing = (
        "Thank you for allowing us to be a part of this important investment. "
        "My team and I look forward to working with you on this important transaction!"
    )
    elements.append(Paragraph(closing, normal_style))
    elements.append(Spacer(1, 18))

    # --- Signature Image ---
    if data.get("signature") and os.path.exists(data["signature"]):
        signature_img = Image(data["signature"], width=2.3*inch, height=0.6*inch)
        signature_img.hAlign = 'LEFT'
        elements.append(signature_img)
        elements.append(Spacer(1, 2))

    # Officer info
    elements.append(Paragraph(data['officer_name'], normal_style))
    elements.append(Paragraph(data['officer_title'], normal_style))
    elements.append(Paragraph(f"NMLS#: {data['nmls']}", normal_style))
    elements.append(Paragraph(f"Phone: {data['phone']}", normal_style))
    elements.append(Paragraph(f"Email: {data['email']}", normal_style))
    elements.append(Spacer(1, 25))  # More space before footer

    # --- Footer Disclaimer ---
    disclaimer = (
        "*** Your loan application has not yet been approved. This pre-approval expires in 90 days and is subject to change or cancellation if industry, "
        "regulatory or program guidelines change. This letter is not a commitment to lend. Any financial decision you make based on this preapproval "
        "is your responsibility and not the responsibility of MillerBros. Lending, LLC.***"
    )
    elements.append(Paragraph(disclaimer, footer_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# --- STREAMLIT UI ---
st.title("📄 Pre-Approval Letter Generator")

with st.form("letter_form"):
    officer_name = st.selectbox("Loan Officer", list(loan_officers.keys()))
    borrower_name = st.text_input("Borrower Name", "Sanjaya Regimi")
    property_address = st.text_input("Property Address", "26 Pisgah Forest Cir. Greensboro, NC 27455")
    purchase_price = st.number_input("Purchase Price", value=285000)
    loan_type = st.selectbox("Loan Type", ["Conventional", "FHA", "VA", "USDA"])
    down_payment = st.number_input("Down Payment (%)", value=30)
    interest_rate = st.number_input("Interest Rate (%)", value=7.0)
    submitted = st.form_submit_button("Generate Letter")

if submitted:
    officer_info = loan_officers[officer_name]
    input_data = {
        "officer_name": officer_name,
        "officer_title": officer_info["title"],
        "nmls": officer_info["nmls"],
        "phone": officer_info["phone"],
        "email": officer_info["email"],
        "signature": officer_info.get("signature", ""),
        "borrower_name": borrower_name,
        "property_address": property_address,
        "purchase_price": purchase_price,
        "loan_type": loan_type,
        "down_payment": down_payment,
        "interest_rate": interest_rate
    }

    logo_path = "miller_logo.png"  # Final cleaned version of your logo
    pdf_file = generate_letter_pdf(input_data, logo_path)

    st.success("✅ Letter created successfully!")
    st.download_button("📄 Download PDF", data=pdf_file, file_name="PreApproval_Letter.pdf", mime="application/pdf")
