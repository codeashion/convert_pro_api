import os
import win32com.client


def ppt_to_pdf(input_path: str, output_path: str):
    powerpoint = win32com.client.Dispatch("PowerPoint.Application")
    powerpoint.Visible = 1

    presentation = powerpoint.Presentations.Open(
        os.path.abspath(input_path),
        WithWindow=False
    )

    presentation.SaveAs(os.path.abspath(output_path), 32)  # 32 = PDF format
    presentation.Close()

    powerpoint.Quit()
