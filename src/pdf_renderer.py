import markdown
import pdfkit
import os
import platform

class PDFRenderer:
    def __init__(self):
        # Path to wkhtmltopdf executable.
        # If the user installs it to the default location and adds it to PATH,
        # pdfkit might find it automatically.
        # This configuration provides a fallback.
        self.config = None
        if platform.system() == "Windows":
            # Default installation path for wkhtmltopdf on Windows
            wkhtmltopdf_path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
            if os.path.exists(wkhtmltopdf_path):
                self.config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
            else:
                print("Warning: wkhtmltopdf.exe not found at default location. Please ensure it's in your system's PATH.")


    def render_markdown_to_pdf(self, markdown_string, output_filepath):
        """
        Converts a Markdown string to a PDF file using pdfkit.
        """
        # Convert Markdown to HTML
        html_string = markdown.markdown(markdown_string)

        # Basic HTML template for better rendering
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Resume</title>
            <style>
                body {{ font-family: sans-serif; margin: 1in; }}
                h1, h2, h3 {{ color: #333; }}
                h1 {{ font-size: 2em; border-bottom: 1px solid #ccc; padding-bottom: 5px; }}
                h2 {{ font-size: 1.5em; border-bottom: 1px solid #eee; padding-bottom: 3px; }}
                h3 {{ font-size: 1.2em; }}
                strong {{ font-weight: bold; }}
                ul {{ list-style-type: disc; margin-left: 20px; }}
                ul ul {{ list-style-type: circle; }}
                p {{ margin-bottom: 0.5em; }}
            </style>
        </head>
        <body>
            {html_string}
        </body>
        </html>
        """

        try:
            # Use pdfkit to write the HTML string to a PDF file
            options = {
                'page-size': 'Letter',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'enable-local-file-access': None
            }
            pdfkit.from_string(
                html_template, 
                output_filepath, 
                options=options, 
                configuration=self.config
            )
            return True, f"PDF successfully rendered to {output_filepath}"
        except FileNotFoundError:
             return False, "Error rendering PDF: 'wkhtmltopdf' not found. Please install it and ensure it's in your system's PATH, or configure the path in 'pdf_renderer.py'."
        except Exception as e:
            return False, f"Error rendering PDF: {e}"