from app.agents.email_agent import EmailAgent


def main():

    email_agent = EmailAgent()

    result = email_agent.send_captcha_link_email(
        advocate_name="Social Welfare",
        captcha_url="http://127.0.0.1:8000/captcha/test-token",
    )

    print("Email result:", result)


if __name__ == "__main__":
    main()