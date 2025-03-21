from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

def Handler(xml):
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    c.setFont("Helvetica", 24)
    c.drawString(100, 750, "Ceci est un test") 
    c.save()
    pdf_buffer.seek(0)
    pdf_bytes = pdf_buffer.read()
    return pdf_bytes