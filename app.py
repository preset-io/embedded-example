"""
Main entry point for this example app
"""

import logging
import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template
from yarl import URL

load_dotenv()

app = Flask(__name__)

# Load environment variables from the .env file
app.config.from_mapping(
    {
        "API_TOKEN": os.environ.get("API_TOKEN"),
        "API_SECRET": os.environ.get("API_SECRET"),
        "DASHBOARD_ID": os.environ.get("DASHBOARD_ID"),
        "SUPERSET_DOMAIN": os.environ.get("SUPERSET_DOMAIN"),
        "PRESET_TEAM": os.environ.get("PRESET_TEAM"),
        "WORKSPACE_SLUG": os.environ.get("WORKSPACE_SLUG"),
        "PRESET_BASE_URL": URL("https://api.app.preset.io/"),
    },
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s",
    handlers=[logging.StreamHandler()],
)


@app.route("/")
def main_page():
    """
    Default route to load index.html (loads the Embedded SDK).
    """
    return render_template(
        "index.html",
        dashboardId=app.config["DASHBOARD_ID"],
        supersetDomain=app.config["SUPERSET_DOMAIN"],
    )


@app.route("/guest-token", methods=["GET"])
def guest_token_generator():
    """
    Route used by frontend to retrieve a Guest Token.
    """
    try:
        jwt_token = authenticate_with_preset()
        guest_token = jsonify(fetch_guest_token(jwt_token))
        return guest_token, 200
    except requests.exceptions.HTTPError as error:
        return jsonify({"error": str(error)}), 400


def authenticate_with_preset():
    """
    Authenticate with the Preset API to generate a JWT token.
    """
    url = app.config["PRESET_BASE_URL"] / "v1/auth/"
    payload = {"name": app.config["API_TOKEN"], "secret": app.config["API_SECRET"]}
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=7,
        )
        response.raise_for_status()
        return response.json()["payload"]["access_token"]
    except requests.exceptions.HTTPError as http_error:
        error_msg = http_error.response.text
        logging.error(
            "\nERROR: Unable to generate a JWT token.\nError details: %s",
            error_msg,
        )
        raise requests.exceptions.HTTPError(
            """Unable to generate a JWT token.
            Please make sure your API key is enabled.""",
        )


def fetch_guest_token(jwt):
    """
    Fetch and return a Guest Token for the embedded dashboard.
    """
    url = (
        app.config["PRESET_BASE_URL"]
        / "v1/teams"
        / app.config["PRESET_TEAM"]
        / "workspaces"
        / app.config["WORKSPACE_SLUG"]
        / "guest-token/"
    )
    payload = {
        "user": {"username": "test_user", "first_name": "test", "last_name": "user"},
        "resources": [{"type": "dashboard", "id": app.config["DASHBOARD_ID"]}],
        "rls": [
            # Apply an RLS to a specific dataset
            # { "dataset": dataset_id, "clause": "column = 'filter'" },
            # Apply an RLS to all datasets
            # { "clause": "column = 'filter'" },
        ],
    }

    headers = {
        "Authorization": f"Bearer {jwt}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=7,
        )
        response.raise_for_status()
        return response.json()["payload"]["token"]
    except requests.exceptions.HTTPError as http_error:
        error_msg = http_error.response.text
        logging.error(
            "\nERROR: Unable to fetch a Guest Token.\nError details: %s",
            error_msg,
        )
        raise requests.exceptions.HTTPError(
            """"Unable to generate a Guest token.
            Please make sure the API key has admin access and the payload is correct.""",
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0")
