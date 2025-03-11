# Author: Miles Baird (https://github.com/kilometers)
# Portfolio analysis module

import os

# Portfolio configuration
tmp_directory = "results"
template_pdf_url = "https://sites.google.com/possiblezone.org/student-portfolio-empty/"
compare_blank_template = False
template_data_path = "src/portfolio/data/blank_template.json"
use_all_competencies = True

# Portfolio paths configuration
raw_portfolio_paths = [
    "/",
    "/my-toolkit/sewing/beginner-sewing",
    "/my-toolkit/sewing/intermediate-sewing",
    "/my-toolkit/sewing/advanced-sewing",
    "/my-toolkit/3d-printing/beginner-3d-printing",
    "/my-toolkit/3d-printing/intermediate-3d-printing",
    "/my-toolkit/3d-printing/advanced-3d-printing",
    "/my-toolkit/2d-design/beginner-2d-design",
    "/my-toolkit/2d-design/intermediate-2d-design",
    "/my-toolkit/2d-design/advanced-2d-design",
    "/my-toolkit/coding/beginner-coding",
    "/my-toolkit/coding/intermediate-coding",
    "/my-toolkit/coding/advanced-coding",
    "/my-business",
    "/my-business/business-plan",
    "/my-business/brand-identity",
    "/my-business/product-development",
    "/resume-work-experience",
]

# Environment variables
PDF_HOST = os.environ.get("PDF_HOST", "https://html2pdf-u707.onrender.com")
