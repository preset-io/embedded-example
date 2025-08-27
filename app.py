"""
Main entry point for this example app
"""

import json
import logging
import os
import subprocess

import click
import jwt
import requests

from config import config
from flask import Flask, jsonify, render_template, request


def create_app(config_name=None):
    app = Flask(__name__)
    env = config_name or "production"
    app.config.from_object(config[env])
    app.config["ENV"] = env

    return app

app = create_app(os.environ.get('FLASK_CONFIG'))


# CLI command to generate public/private PEM keys
@app.cli.command("generate-keys")
@click.option(
    "--overwrite",
    is_flag=True,
    help="Overwrite existing keys if they exist.",
)
def generate_keys(overwrite=False):
    """Generate RSA private and public keys using OpenSSL."""

    # Check if OpenSSL is installed
    try:
        result = subprocess.run(
            ["openssl", "version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        print(f"OpenSSL version: {result.stdout.decode().strip()}")
    except FileNotFoundError as exc:
        raise RuntimeError(
            "OpenSSL is not installed or not available in PATH.",
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"Failed to execute OpenSSL: {exc.stderr.decode().strip()}",
        ) from exc

    # Ensure the output directory exists
    if not os.path.exists(app.config["KEY_DIR"]):
        os.makedirs(app.config["KEY_DIR"])

    # Check if the files already exist
    if (
        os.path.exists(app.config["PRIVATE_KEY_PATH"]) or os.path.exists(app.config["PUBLIC_KEY_PATH"])
    ) and not overwrite:
        raise Exception(  # pylint: disable=broad-exception-raised
            "Key files already exist. Use --overwrite to overwrite the existing files.",
        )
    print("Overwriting existing PEM keys.")

    # Generate the private key
    try:
        subprocess.run(
            [
                "openssl",
                "genpkey",
                "-algorithm",
                "RSA",
                "-out",
                app.config["PRIVATE_KEY_PATH"],
                "-pkeyopt",
                "rsa_keygen_bits:2048",
            ],
            check=True,
        )
        print(f"Private key generated at: {app.config['PRIVATE_KEY_PATH']}")
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Failed to generate private key: {exc}") from exc

    # Generate the public key
    try:
        subprocess.run(
            [
                "openssl",
                "rsa",
                "-pubout",
                "-in",
                app.config["PRIVATE_KEY_PATH"],
                "-out",
                app.config["PUBLIC_KEY_PATH"],
            ],
            check=True,
        )
        print(f"Public key generated at: {app.config['PUBLIC_KEY_PATH']}")
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Failed to generate private key: {exc}") from exc


@app.route("/")
def main_page():
    """
    Default route to load index.html (loads the Embedded SDK).
    """
    auth_type = request.args.get("auth_type", "api")
    if auth_type == "pem":
        if not os.path.exists(app.config["PRIVATE_KEY_PATH"]) or not os.path.exists(app.config["PUBLIC_KEY_PATH"]):
            raise FileNotFoundError("PEM key files not found.")
        if app.config["KEY_ID"] is None:
            raise KeyError("Key ID not defined in environment variables.")

    return render_template(
        "index.html",
        dashboard_id=app.config["DASHBOARD_ID"],
        superset_domain=app.config["SUPERSET_DOMAIN"],
        auth_type=auth_type,
        env=app.config["ENV"],
    )


@app.route("/guest-token", methods=["GET"])
def local_guest_token_generator():
    """
    Route used by frontend to retrieve a Guest Token.
    """
    try:
        jwt_token = (
            authenticate_with_preset()
            if app.config["ENV"] != "development"
            else authenticate_with_superset()
        )
        guest_token = (
            jsonify(fetch_guest_token(jwt_token))
            if app.config["ENV"] != "development"
            else jsonify(fetch_superset_guest_token(jwt_token))
        )
        return guest_token, 200
    except requests.exceptions.HTTPError as error:
        return jsonify({"error": str(error)}), 500


def authenticate_with_superset():
    """
    Authenticate with Superset to generate a JWT token.
    """
    url = "http://127.0.01:8088/api/v1/security/login"
    payload = {
        "username": "1",
        "password": "1",
        "provider": "db",
        "refresh": True,
    }
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=7,
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.exceptions.HTTPError as http_error:
        error_msg = http_error.response.text
        logging.error(
            "\nERROR: Unable to generate a JWT token.\nError details: %s",
            error_msg,
        )
        raise requests.exceptions.HTTPError(
            "Unable to generate a JWT token. "
            "Please make sure the data is accurate.",
        )


def fetch_superset_guest_token(jwt_key):
    """
    Fetch and return a Guest Token for the embedded dashboard in Superset.
    """
    url = "http://localhost:8088/api/v1/security/guest_token/"
    payload = {
        "user": {"username": "test_user", "first_name": "test", "last_name": "user"},
        "resources": [{"type": "dashboard", "id": app.config["DASHBOARD_ID"]}],
        "rls": [
            # Apply an RLS to a specific dataset
            # { "dataset": dataset_id, "clause": "column = 'filter'" },
            # Apply an RLS to all datasets
            # { "clause": "year=2003 /* Applied to all datasets*/" },
            # { "dataset": 23, "clause": "month=3 /* Applied to this one*/" },
        ],
    }

    headers = {
        "Authorization": f"Bearer {jwt_key}",
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
        return response.json()["token"]
    except requests.exceptions.HTTPError as http_error:
        error_msg = http_error.response.text
        logging.error(
            "\nERROR: Unable to fetch a Guest Token.\nError details: %s",
            error_msg,
        )
        raise requests.exceptions.HTTPError(
            "Unable to generate a Guest token. "
            "Please make sure the API key has admin access and the payload is correct.",
        )


def authenticate_with_preset():
    """
    Authenticate with the Preset API to generate a JWT token.
    """
    url = app.config["PRESET_BASE_URL"] / "api/v1/auth/"
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
            "Unable to generate a JWT token. "
            "Please make sure your API key is enabled.",
        )


def fetch_guest_token(jwt_key):
    """
    Fetch and return a Guest Token for the embedded dashboard.
    """
    url = (
        app.config["PRESET_BASE_URL"]
        / "api/v1/teams"
        / app.config["PRESET_TEAM_ID"]
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
            { "clause": "country = 'USA'" },
        ],
        # "enable_drilling": True,
    }

    headers = {
        "Authorization": f"Bearer {jwt_key}",
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
            "Unable to generate a Guest token. "
            "Please make sure the API key has admin access and the payload is correct.",
        )


@app.route("/pem-key", methods=["GET"])
def get_guest_token_using_pem_key():
    """
    Encode and return a Guest Token for the embedded dashboard.
    """
    with open(app.config["PRIVATE_KEY_PATH"], "r", encoding="utf-8") as file:
        private_key = file.read()

    # Payload to encode
    payload = {
        "user": {"username": "embedded_username", "first_name": "", "last_name": ""},
        "resources": [{"type": "dashboard", "id": app.config["DASHBOARD_ID"]}],
        "rls_rules": [
            # Apply an RLS to a specific dataset
            # { "dataset": dataset_id, "clause": "column = 'filter'" },
            # Apply an RLS to all datasets
            # { "clause": "column = 'filter'" },
        ],
        "type": "guest",
        "aud": app.config["WORKSPACE_SLUG"],
    }

    encoded_jwt = jwt.encode(
        payload,
        private_key,
        algorithm="RS256",
        headers={"kid": app.config["KEY_ID"]},
    )
    return json.dumps(encoded_jwt)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
