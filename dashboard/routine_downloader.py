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


def downloader(exams, routine, room, shift):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont('Vera', 10)

    today = str(datetime.date.today())
    can.drawString(465, 675, today)  # done

    can.drawString(105, 629, routine.department.name)  # done

    can.drawString(127, 614, "B.Sc.")  # done

    can.drawString(105, 599, "Wazed Building")  # done

    can.drawString(105, 583, str(room))  # done

    shift = datetime.datetime.strptime(str(shift), "%H:%M:%S")
    can.drawString(98, 567, shift.strftime("%I:%M %p"))  # done

    k = 0
    for exam in exams:
        can.drawString(160, 530 - k, str(exam.exam_date))
        can.drawString(405, 530 - k, str(exam.course.code))
        k += 16

    can.save()

    # move to the beginning of the StringIO buffer
    packet.seek(0)

    # create a new PDF with Reportlab
    new_pdf = PdfFileReader(packet)

    # file name
    sample_name = f"Sample/Routine/Routine {len(exams)}.pdf"

    # read your existing PDF
    existing_pdf = PdfFileReader(open(sample_name, "rb"))
    output = PdfFileWriter()

    # add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)

    # finally, write "output" to a real file
    outputStream = open("Sample/output.pdf", "wb")
    output.write(outputStream)
    outputStream.close()
