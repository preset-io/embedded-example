import json
import os
import requests

from dotenv import load_dotenv
from flask import Flask, render_template, jsonify

load_dotenv()

# Load environment variables from the .env file
APIToken = os.environ.get("APIToken")
APISecret = os.environ.get("APISecret")
dashboard_id = os.environ.get("DashID")
superset_domain = os.environ.get("SupersetDomain")
preset_team = os.environ.get("PresetTeam")
workspace_slug = os.environ.get("WorkspaceSlug")

app = Flask(__name__)

# Serve the index.html page
@app.route('/')
def hello():
	return render_template('index.html', dashboardId = dashboard_id, supersetDomain = superset_domain)


# Authentication side
@app.route("/guest-token", methods=["GET"])
def guest_token():
	## 1. Authenticate with Preset API
	url = "https://manage.app.preset.io/api/v1/auth/"
	payload = json.dumps({
		"name": APIToken,
		"secret": APISecret
	})

	headers = {
		'Content-Type': 'application/json',
		'Accept': 'application/json'
	}

	response1 = requests.request("POST", url, headers=headers, data=payload)
	preset_access_token = json.loads(response1.text)['payload']['access_token']

	## 2. Fetch Guest Token for Embedded Dashboard
	payload = json.dumps({
		"user": {
			"username": "test_user",
			"first_name": "test",
			"last_name": "user"
		},
		"resources": [{
			"type": "dashboard",
			"id": f"{dashboard_id}"
		}],
		"rls": [
			#{ "dataset": dataset_id, "clause": "column = 'filter'" },
		]
	})

	bearer_token = "Bearer " + preset_access_token
	response2 = requests.post(
		f"https://manage.app.preset.io/api/v1/teams/{preset_team}/workspaces/{workspace_slug}/guest-token/",
		data=payload,
		headers={ "Authorization": bearer_token, 'Accept': 'application/json', 'Content-Type': 'application/json' })
	
	# Return guest_token as valid JSON to frontend
	return jsonify(response2.json()['payload']['token'])

if __name__ == "__main__":                                                                                                  # Settings to be applied when running locally
    app.run(host="0.0.0.0", port=8080, debug=True)
