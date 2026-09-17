"""
Central application configuration.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ----------------------------------------------------------
    # Application
    # ----------------------------------------------------------

    app_name: str = "Court Cause List Agent"

    environment: str = "development"

    secret_key: str = (
        "insecure-dev-key-change-me"
    )

    access_token_expire_minutes: int = 60

    # ----------------------------------------------------------
    # Database
    # ----------------------------------------------------------

    database_url: str = (
        "sqlite:///./cause_list.db"
    )

    # ----------------------------------------------------------
    # Court Website
    # ----------------------------------------------------------

    court_base_url: str = (
        "https://aphc.gov.in"
    )

    search_page_url: str = (
        "https://aphc.gov.in/Hcdbs/"
        "searchtypeinput.action"
    )

    court_departments: str = (
        "Social Welfare"
    )

    # ----------------------------------------------------------
    # CAPTCHA
    # ----------------------------------------------------------
    #
    # CAPTCHA is handled MANUALLY in the visible browser.
    #
    # The program does NOT:
    # - solve CAPTCHA
    # - capture CAPTCHA
    # - email CAPTCHA
    # - create CAPTCHA bridge
    # - receive CAPTCHA answers
    #
    # The browser simply waits for the user to complete CAPTCHA.
    # ----------------------------------------------------------

    captcha_solver: str = "manual"

    captcha_max_retries: int = 3

    # ----------------------------------------------------------
    # Scheduler
    # ----------------------------------------------------------

    scheduler_start_time: str = "17:00"

    scheduler_end_time: str = "22:00"

    scheduler_poll_interval_minutes: int = 15

    # ----------------------------------------------------------
    # Email / SMTP
    # ----------------------------------------------------------

    smtp_host: str = "smtp.gmail.com"

    # Gmail SMTP SSL
    smtp_port: int = 465

    smtp_username: str = ""

    smtp_password: str = ""

    smtp_from_address: str = ""

    # STARTTLS is not used with Gmail SSL port 465.
    smtp_use_tls: bool = False

    # Direct SSL connection to Gmail.
    smtp_use_ssl: bool = True
    
    
    report_recipient_email: str = ""

    # ----------------------------------------------------------
    # File Storage
    # ----------------------------------------------------------

    pdf_storage_dir: str = (
        "./storage/pdfs"
    )

    # ----------------------------------------------------------
    # Departments
    # ----------------------------------------------------------

    @property
    def department_list(self) -> List[str]:

        return [
            d.strip()
            for d in self.court_departments.split(",")
            if d.strip()
        ]


# --------------------------------------------------------------
# Cached Settings
# --------------------------------------------------------------

@lru_cache
def get_settings() -> Settings:
    """
    Cached settings accessor.
    """

    return Settings()


settings = get_settings()