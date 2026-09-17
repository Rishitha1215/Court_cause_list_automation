from app.agents.navigator_agent import NavigatorAgent
from app.agents.captcha.ocr_solver import OCRCaptchaSolver
from app.agents.extractor_agent import ExtractorAgent
from app.agents.excel_agent import ExcelAgent
from app.agents.email_agent import EmailAgent


def main():
    # Create CAPTCHA Solver
    solver = OCRCaptchaSolver()

    # Create Navigator
    navigator = NavigatorAgent()

    # Navigate to website and fetch data
    html = navigator.run("Social Welfare")

    # Extract case details
    extractor = ExtractorAgent()
    cases = extractor.run(html)

    # Generate Excel Report
    excel = ExcelAgent()
    excel_path = excel.generate_report(
        cases,
        "Social_Welfare"
    )

    # Send Email
    email = EmailAgent()

    email.send_email(
        recipient_email="pujitha0307@gmail.com",   # Replace with your email
        advocate_name="Social Welfare",
        excel_file=excel_path,
        total_cases=len(cases),
    )

    # Display Results
    print("=" * 80)
    print("SUCCESS!")
    print("=" * 80)

    print(f"Total Cases: {len(cases)}")
    print(f"Excel Report: {excel_path}")
    print()

    print("First 5 Cases:")
    print("-" * 80)

    for case in cases[:5]:
        print(case)
        print("-" * 80)


if __name__ == "__main__":
    main()