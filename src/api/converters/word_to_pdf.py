import os
import win32com.client

def word_to_pdf(input_path: str, output_path: str):
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False

    doc = word.Documents.Open(os.path.abspath(input_path))
    doc.SaveAs(os.path.abspath(output_path), FileFormat=17)  # 17 = PDF
    doc.Close()

    word.Quit()
