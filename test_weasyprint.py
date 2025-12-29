
from weasyprint import HTML


html_content = """
<h1 style="color: red; text-align: center;">AIPentest v2.2 — WeasyPrint ТЕСТ</h1>
<p>Если видишь PDF — всё работает!</p>
"""


HTML(string=html_content).write_pdf("test_weasyprint.pdf")
print("PDF создан: test_weasyprint.pdf")