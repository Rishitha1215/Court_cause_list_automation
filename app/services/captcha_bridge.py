"""
CAPTCHA Bridge

Provides a shared CAPTCHA challenge between the Navigator process
and the FastAPI web server.

The challenge is stored in SQLite so that the Navigator process
and FastAPI process can communicate even when they are running
as separate Python processes.
"""

import sqlite3
import time

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from secrets import token_urlsafe
from typing import Optional


# ==========================================================
# CAPTCHA Challenge
# ==========================================================

@dataclass
class CaptchaChallenge:

    token: str

    advocate_name: str

    captcha_image: bytes

    created_at: datetime

    expires_at: datetime

    answer: Optional[str] = None


# ==========================================================
# CAPTCHA Bridge
# ==========================================================

class CaptchaBridge:

    def __init__(
        self,
        expiry_seconds: int = 600,
        database_path: str = "./storage/captcha_bridge.db",
    ):

        self.expiry_seconds = expiry_seconds

        self.database_path = Path(database_path)

        # Create storage directory
        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize_database()

    # ======================================================
    # Database Initialization
    # ======================================================

    def _get_connection(self):

        connection = sqlite3.connect(
            self.database_path,
            timeout=30,
            check_same_thread=False,
        )

        return connection

    def _initialize_database(self):

        with self._get_connection() as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS captcha_challenges (

                    token TEXT PRIMARY KEY,

                    advocate_name TEXT NOT NULL,

                    captcha_image BLOB NOT NULL,

                    created_at TEXT NOT NULL,

                    expires_at TEXT NOT NULL,

                    answer TEXT,

                    submitted INTEGER NOT NULL DEFAULT 0
                )
                """
            )

            connection.commit()

    # ======================================================
    # Create Challenge
    # ======================================================

    def create_challenge(
        self,
        advocate_name: str,
        captcha_image: bytes,
    ) -> CaptchaChallenge:

        now = datetime.now(timezone.utc)

        expires_at = (
            now
            + timedelta(
                seconds=self.expiry_seconds
            )
        )

        token = token_urlsafe(32)

        with self._get_connection() as connection:

            # Remove expired challenges first
            connection.execute(
                """
                DELETE FROM captcha_challenges
                WHERE expires_at <= ?
                """,
                (
                    expires_at.isoformat(),
                ),
            )

            connection.execute(
                """
                INSERT INTO captcha_challenges (
                    token,
                    advocate_name,
                    captcha_image,
                    created_at,
                    expires_at,
                    answer,
                    submitted
                )
                VALUES (?, ?, ?, ?, ?, NULL, 0)
                """,
                (
                    token,
                    advocate_name,
                    sqlite3.Binary(captcha_image),
                    now.isoformat(),
                    expires_at.isoformat(),
                ),
            )

            connection.commit()

        return CaptchaChallenge(

            token=token,

            advocate_name=advocate_name,

            captcha_image=captcha_image,

            created_at=now,

            expires_at=expires_at,

            answer=None,
        )

    # ======================================================
    # Get Challenge
    # ======================================================

    def get_challenge(
        self,
        token: str,
    ) -> Optional[CaptchaChallenge]:

        with self._get_connection() as connection:

            row = connection.execute(
                """
                SELECT
                    token,
                    advocate_name,
                    captcha_image,
                    created_at,
                    expires_at,
                    answer,
                    submitted
                FROM captcha_challenges
                WHERE token = ?
                """,
                (token,),
            ).fetchone()

        if row is None:

            return None

        (
            token,
            advocate_name,
            captcha_image,
            created_at,
            expires_at,
            answer,
            submitted,
        ) = row

        created_at_dt = datetime.fromisoformat(
            created_at
        )

        expires_at_dt = datetime.fromisoformat(
            expires_at
        )

        challenge = CaptchaChallenge(

            token=token,

            advocate_name=advocate_name,

            captcha_image=bytes(captcha_image),

            created_at=created_at_dt,

            expires_at=expires_at_dt,

            answer=answer,
        )

        # Check expiration
        if self._is_expired(challenge):

            self.remove_challenge(token)

            return None

        return challenge

    # ======================================================
    # Submit CAPTCHA Answer
    # ======================================================

    def submit_answer(
        self,
        token: str,
        answer: str,
    ) -> bool:

        answer = answer.strip()

        if not answer:

            return False

        now = datetime.now(timezone.utc)

        with self._get_connection() as connection:

            row = connection.execute(
                """
                SELECT expires_at
                FROM captcha_challenges
                WHERE token = ?
                """,
                (token,),
            ).fetchone()

            if row is None:

                return False

            expires_at = datetime.fromisoformat(
                row[0]
            )

            if now >= expires_at:

                connection.execute(
                    """
                    DELETE FROM captcha_challenges
                    WHERE token = ?
                    """,
                    (token,),
                )

                connection.commit()

                return False

            connection.execute(
                """
                UPDATE captcha_challenges

                SET
                    answer = ?,
                    submitted = 1

                WHERE token = ?
                """,
                (
                    answer,
                    token,
                ),
            )

            connection.commit()

        print("=" * 60)
        print("CAPTCHA ANSWER RECEIVED")
        print("Token:", token)
        print("=" * 60)

        return True

    # ======================================================
    # Wait For CAPTCHA Answer
    # ======================================================

    def wait_for_answer(
        self,
        token: str,
        timeout: Optional[int] = None,
    ) -> Optional[str]:

        if timeout is None:

            timeout = self.expiry_seconds

        start_time = time.monotonic()

        print("=" * 60)
        print("Waiting for CAPTCHA answer...")
        print("Token:", token)
        print("=" * 60)

        while True:

            challenge = self.get_challenge(
                token
            )

            if challenge is None:

                print(
                    "CAPTCHA challenge no longer exists."
                )

                return None

            # --------------------------------------------------
            # Check if answer has been submitted
            # --------------------------------------------------

            with self._get_connection() as connection:

                row = connection.execute(
                    """
                    SELECT answer, submitted
                    FROM captcha_challenges
                    WHERE token = ?
                    """,
                    (token,),
                ).fetchone()

            if row is not None:

                answer, submitted = row

                if submitted and answer:

                    print("=" * 60)
                    print("CAPTCHA ANSWER RECEIVED")
                    print("Answer:", answer)
                    print("=" * 60)

                    return answer.strip()

            # --------------------------------------------------
            # Timeout
            # --------------------------------------------------

            elapsed = (
                time.monotonic()
                - start_time
            )

            if elapsed >= timeout:

                print(
                    "CAPTCHA wait timeout reached."
                )

                self.remove_challenge(token)

                return None

            # --------------------------------------------------
            # Poll every half second
            # --------------------------------------------------

            time.sleep(0.5)

    # ======================================================
    # Remove Challenge
    # ======================================================

    def remove_challenge(
        self,
        token: str,
    ) -> None:

        with self._get_connection() as connection:

            connection.execute(
                """
                DELETE FROM captcha_challenges
                WHERE token = ?
                """,
                (token,),
            )

            connection.commit()

    # ======================================================
    # Check Expiration
    # ======================================================

    def _is_expired(
        self,
        challenge: CaptchaChallenge,
    ) -> bool:

        return (
            datetime.now(timezone.utc)
            >= challenge.expires_at
        )


# ==========================================================
# Shared Bridge Instance
# ==========================================================

captcha_bridge = CaptchaBridge()