import io
import datetime

from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
pdfmetrics.registerFont(TTFont('VeraBd', 'VeraBd.ttf'))
pdfmetrics.registerFont(TTFont('VeraIt', 'VeraIt.ttf'))
pdfmetrics.registerFont(TTFont('VeraBI', 'VeraBI.ttf'))


def downloader(routine, student):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont('Vera', 10)

    can.drawString(275, 522, routine.name)
    can.drawString(275, 498, student.get_name)
    can.drawString(275, 474, student.student_id)
    can.drawString(275, 450, str(routine.session))
    can.drawString(275, 426, "Dr. M. A. Wazed Building")

    # image = "Sample/Sign/sign2.png"
    # can.drawImage(image, 300, 400)

    can.save()

    # move to the beginning of the StringIO buffer
    packet.seek(0)

    # create a new PDF with Reportlab
    new_pdf = PdfFileReader(packet)

    # file name
    sample_name = "Sample/Admit/Admit.pdf"

    # read your existing PDF
    existing_pdf = PdfFileReader(open(sample_name, "rb"))
    output = PdfFileWriter()

    # add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)

    # finally, write "output" to a real file
    outputStream = open("Sample/Admit.pdf", "wb")
    output.write(outputStream)
    outputStream.close()
