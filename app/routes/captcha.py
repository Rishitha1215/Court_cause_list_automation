"""
CAPTCHA web routes.

Displays the CAPTCHA captured by NavigatorAgent and allows
the administrator to manually submit the CAPTCHA answer.
"""

import base64
import html

from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse

from app.services.captcha_bridge import captcha_bridge


router = APIRouter(
    prefix="/captcha",
    tags=["captcha"],
)


# ==========================================================
# CAPTCHA PAGE
# ==========================================================

@router.get(
    "/{token}",
    response_class=HTMLResponse,
)
def captcha_page(token: str):

    challenge = captcha_bridge.get_challenge(token)

    # ------------------------------------------------------
    # Invalid / expired token
    # ------------------------------------------------------

    if challenge is None:
        return HTMLResponse(
            content="""
<!DOCTYPE html>
<html>
<head>
    <title>CAPTCHA Expired</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }

        .container {
            background: white;
            padding: 35px;
            border-radius: 10px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.15);
            text-align: center;
            max-width: 500px;
        }

        h2 {
            color: #b00020;
        }
    </style>
</head>

<body>

<div class="container">

    <h2>CAPTCHA Link Expired</h2>

    <p>
        This CAPTCHA request is no longer available.
    </p>

    <p>
        Please wait for the Court Cause List Agent
        to generate a new CAPTCHA request.
    </p>

</div>

</body>
</html>
""",
            status_code=404,
        )

    # ------------------------------------------------------
    # CAPTCHA already submitted
    # ------------------------------------------------------

    if challenge.submitted:
        return HTMLResponse(
            content="""
<!DOCTYPE html>
<html>
<head>
    <title>CAPTCHA Submitted</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }

        .container {
            background: white;
            padding: 35px;
            border-radius: 10px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.15);
            text-align: center;
            max-width: 500px;
        }

        h2 {
            color: #198754;
        }
    </style>
</head>

<body>

<div class="container">

    <h2>CAPTCHA Already Submitted</h2>

    <p>
        The CAPTCHA answer has already been submitted.
    </p>

    <p>
        The browser automation should continue automatically.
    </p>

</div>

</body>
</html>
""",
            status_code=200,
        )

    # ------------------------------------------------------
    # CAPTCHA image
    # ------------------------------------------------------

    captcha_image = challenge.captcha_image

    if not captcha_image:
        return HTMLResponse(
            content="""
<!DOCTYPE html>
<html>
<head>
    <title>CAPTCHA Unavailable</title>
</head>

<body>

<h2>CAPTCHA image unavailable</h2>

<p>
Please wait for the agent to generate a new CAPTCHA request.
</p>

</body>
</html>
""",
            status_code=500,
        )

    # ------------------------------------------------------
    # Convert image to Base64
    # ------------------------------------------------------

    image_base64 = base64.b64encode(
        captcha_image
    ).decode("utf-8")

    advocate_name = html.escape(
        challenge.advocate_name
    )

    # ------------------------------------------------------
    # CAPTCHA form
    # ------------------------------------------------------

    page_html = f"""
<!DOCTYPE html>

<html>

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>AP High Court CAPTCHA</title>

    <style>

        body {{
            font-family: Arial, sans-serif;
            background: #f5f5f5;

            display: flex;
            justify-content: center;
            align-items: center;

            min-height: 100vh;

            margin: 0;
        }}

        .container {{
            background: white;

            width: 90%;
            max-width: 500px;

            padding: 30px;

            border-radius: 12px;

            box-shadow:
                0 2px 15px rgba(0,0,0,0.15);

            text-align: center;
        }}

        h1 {{
            margin-bottom: 10px;
        }}

        .info {{
            color: #555;
            margin-bottom: 20px;
        }}

        .captcha-image {{
            display: block;

            margin: 20px auto;

            max-width: 100%;

            border: 1px solid #ccc;

            padding: 5px;

            background: white;
        }}

        input[type="text"] {{
            width: 90%;

            padding: 12px;

            font-size: 18px;

            text-align: center;

            border: 1px solid #aaa;

            border-radius: 6px;

            margin-top: 10px;
        }}

        button {{
            margin-top: 20px;

            padding: 12px 30px;

            font-size: 16px;

            background: #0d6efd;

            color: white;

            border: none;

            border-radius: 6px;

            cursor: pointer;
        }}

        button:hover {{
            background: #0b5ed7;
        }}

        .warning {{
            margin-top: 20px;

            padding: 10px;

            background: #fff3cd;

            border-radius: 6px;

            color: #664d03;
        }}

    </style>

</head>

<body>

<div class="container">

    <h1>
        AP High Court CAPTCHA
    </h1>

    <div class="info">

        <p>
            Advocate / Department:
        </p>

        <strong>
            {advocate_name}
        </strong>

    </div>

    <p>
        Enter the CAPTCHA shown below.
    </p>

    <img
        class="captcha-image"
        src="data:image/png;base64,{image_base64}"
        alt="AP High Court CAPTCHA"
    >

    <form
        method="post"
        action="/captcha/{token}"
    >

        <input
            type="text"
            name="captcha_answer"
            placeholder="Enter CAPTCHA"
            autocomplete="off"
            required
            autofocus
        >

        <br>

        <button type="submit">
            Submit CAPTCHA
        </button>

    </form>

    <div class="warning">

        After submitting the CAPTCHA,
        the Court Cause List Agent will continue
        automatically.

    </div>

</div>

</body>

</html>
"""

    return HTMLResponse(
        content=page_html,
        status_code=200,
    )


# ==========================================================
# CAPTCHA SUBMISSION
# ==========================================================

@router.post(
    "/{token}",
    response_class=HTMLResponse,
)
def submit_captcha(
    token: str,
    captcha_answer: str = Form(...),
):

    answer = captcha_answer.strip()

    if not answer:
        return HTMLResponse(
            content="""
<!DOCTYPE html>
<html>
<body>

<h2>CAPTCHA answer is required.</h2>

<p>
Please go back and enter the CAPTCHA.
</p>

</body>
</html>
""",
            status_code=400,
        )

    # ------------------------------------------------------
    # Check challenge
    # ------------------------------------------------------

    challenge = captcha_bridge.get_challenge(token)

    if challenge is None:
        return HTMLResponse(
            content="""
<!DOCTYPE html>
<html>
<body>

<h2>CAPTCHA link expired.</h2>

<p>
Please wait for the agent to generate a new CAPTCHA.
</p>

</body>
</html>
""",
            status_code=404,
        )

    # ------------------------------------------------------
    # Submit answer to bridge
    # ------------------------------------------------------

    success = captcha_bridge.submit_solution(
        token=token,
        answer=answer,
    )

    if not success:
        return HTMLResponse(
            content="""
<!DOCTYPE html>
<html>
<body>

<h2>Unable to submit CAPTCHA.</h2>

<p>
The CAPTCHA request may have expired.
Please wait for a new CAPTCHA request.
</p>

</body>
</html>
""",
            status_code=400,
        )

    # ------------------------------------------------------
    # Success
    # ------------------------------------------------------

    return HTMLResponse(
        content="""
<!DOCTYPE html>

<html>

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>CAPTCHA Submitted</title>

    <style>

        body {
            font-family: Arial, sans-serif;

            background: #f5f5f5;

            display: flex;

            justify-content: center;

            align-items: center;

            min-height: 100vh;
        }

        .container {
            background: white;

            padding: 35px;

            border-radius: 12px;

            box-shadow:
                0 2px 15px rgba(0,0,0,0.15);

            text-align: center;

            max-width: 500px;
        }

        h2 {
            color: #198754;
        }

    </style>

</head>

<body>

<div class="container">

    <h2>
        CAPTCHA Submitted Successfully
    </h2>

    <p>
        Your CAPTCHA answer has been sent to
        the Court Cause List Agent.
    </p>

    <p>
        The browser automation will now continue.
    </p>

    <p>
        You can close this page.
    </p>

</div>

</body>

</html>
""",
        status_code=200,
    )