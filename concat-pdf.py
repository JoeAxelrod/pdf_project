import io
from datetime import datetime
from reportlab.pdfgen import canvas
from flask import Flask, request, render_template
import PyPDF2
from reportlab.pdfgen import canvas
import webbrowser
import os


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/merge_pdfs', methods=['POST'])
def merge_pdfs():
    pdf_writer = PyPDF2.PdfWriter()
    page_offset = 0

    print("Number of files received:", len(request.files.getlist('pdfs')))  # Debug line

    for file in request.files.getlist('pdfs'):
        pdf_reader = PyPDF2.PdfReader(file.stream)
        for page_number, page in enumerate(pdf_reader.pages, start=1):
            pdf_writer.add_page(page)

            # Add page numbers
            text = f"{page_number + page_offset}"
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=page.mediabox[2:])
            can.drawString(100, 10, text)
            can.save()
            packet.seek(0)
            new_pdf = PyPDF2.PdfReader(packet)
            overlay_page = new_pdf.pages[0]
            page.merge_page(overlay_page)

        page_offset += len(pdf_reader.pages)

    output = io.BytesIO()
    pdf_writer.write(output)
    output.seek(0)

    # Create the file locally with a datetime stamp
    datetime_now = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"../merged_document_{datetime_now}.pdf"
    with open(file_name, 'wb') as f:
        f.write(output.getvalue())
        print(f"PDF merged successfully. File saved as: {file_name}")
        webbrowser.open(os.path.realpath(file_name))
    


    return {"message": "PDF merged successfully", "file": file_name}

if __name__ == '__main__':
    # Set a flag to prevent opening the browser multiple times in development mode
    if 'WERKZEUG_RUN_MAIN' not in os.environ:
        webbrowser.open('http://localhost:5000')
    app.run(debug=True)



