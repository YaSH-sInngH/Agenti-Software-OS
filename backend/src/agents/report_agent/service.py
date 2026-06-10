from src.core.llm.claude import llm
from src.core.utils.workspace import get_workspace_path


def safe_name(title: str):

    cleaned = [
        c if (c.isalnum() or c in (" ", "-", "_")) else "_"
        for c in (title or "report")
    ]

    name = "".join(cleaned).strip().replace(" ", "_")

    return name or "report"


def write_markdown(path, content):
    path.write_text(content, encoding="utf-8")


def write_pdf(path, content):

    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)

    for line in content.split("\n"):
        safe = line.encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 8, safe)

    pdf.output(str(path))


def write_excel(path, content):

    from openpyxl import Workbook

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Report"

    for line in content.split("\n"):
        sheet.append([line])

    workbook.save(str(path))


class ReportService:

    @staticmethod
    def create(title: str, content: str, fmt: str = "markdown"):

        workspace = get_workspace_path()
        name = safe_name(title)
        fmt = (fmt or "markdown").lower()

        try:
            if fmt in ("markdown", "md"):
                path = workspace / f"{name}.md"
                write_markdown(path, content)

            elif fmt == "pdf":
                path = workspace / f"{name}.pdf"
                write_pdf(path, content)

            elif fmt in ("excel", "xlsx"):
                path = workspace / f"{name}.xlsx"
                write_excel(path, content)

            else:
                return {
                    "success": False,
                    "message": f"Unsupported format: {fmt}",
                }

        except ImportError:
            hint = {
                "pdf": "pip install fpdf2",
                "excel": "pip install openpyxl",
                "xlsx": "pip install openpyxl",
            }.get(fmt, "")
            return {
                "success": False,
                "message": f"Missing library for {fmt} reports. Run: {hint}",
            }

        return {
            "success": True,
            "title": title,
            "format": fmt,
            "path": str(path),
        }

    @staticmethod
    def generate(topic: str, fmt: str = "markdown", title: str = None):

        title = title or topic

        prompt = f"""
Write a clear, well-structured report about the topic below.
Use Markdown headings and bullet points.

Topic:

{topic}
"""

        result = llm.invoke(prompt)

        return ReportService.create(
            title,
            result.content,
            fmt,
        )
