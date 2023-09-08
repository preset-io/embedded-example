# ce-embedded

Sample (and extremely simple) FLask app that can be used to test the Preset Embedding experience!
**_Note that this app is solely intended to demonstrate the embedded implementation, and shouldn't be used in a Production environment._**

## How to use it

This project uses Python to run a Flask app. We strongly encourage using a [Python Virtual environment](https://docs.python.org/3/library/venv.html) to install it (this tutorial won't cover this part).

### Implementation actions

Start by cloning the repository to your local environment. Then, duplicate the `.env-example` file, and save it as `.env` in the root folder (the file is automatically git-ignored). This file is responsible for providing the app with your credentials, team and dashboard information. Replace template values in there accordingly (no need to add quotes etc). Let's take a look on how to fill it:

#### Authentiation details _(optional)_

**DISCLAIMER:** Your API token and secret are **only stored in this local file** -- this information is not processed or synced anywhere else. It's also possible to run this app without providing your credentials, however you would have to generate the Guest Token on your end (for example, using Postman), and then provide the Guest Token to the SDK. Additionally, the Guest Token is only valid for 5 minutes, so after that you might start facing errors when interacting with the embedded dashboard.

If you would like to avoid adding your credentials to this file, feel free to just skip this step.

- Replace `your_api_token_here` with a token created (and enabled) from Manager (line 3).
- Replace `your_api_secret_here` with its corresponding secret (line 4).

_Refer to [this page](https://api-docs.preset.io/#intro) to check how to create your Preset API key/token._

#### Team, Workspace and Dashboard information

Make sure you have already enabled the **Embedded mode** for the dashboard you would like to use with this app. Refer to [this page](https://docs.preset.io/docs/step-1-preparation#collect-the-information) for further instructions. Replace these values with the information retrieved from the Embedded modal (from Preset):

- Replace `your_dashboard_id_here` with your **Embedded Dashboard ID** (line 8).
- Replace `your_superset_domain_here` with your **Superset Domain** (line 9).
- Replace `your_preset_team_here` with your **Team ID** (line 10).
- Replace `your_workspace_slug_here` with your **Workspace ID** (line 11).

#### Installing dependencies

1. Create a new virtual environment for this project.
2. Activate it.
3. Run `pip install --upgrade pip` to update pip.
4. Run `pip install -r requirements.txt` to install all dependencies for this project.

### Running the application

1. Run `python app.py` in the terminal (inside the root folder). This would start the Flask app.
2. Access `http://127.0.0.1:8080/` on the browser. You should see an `iframe` in the full browser size, which would load the dashboard in embedded mode.

### Stopping the app

1. Once testing is done, press `control + C` in the terminal to stop the Flask app.
2. Deactivate the virtual environment.

## Changing the app configurations

### Authentication

Since the Guest Token is only valid for 5 minutes, the SDK automatically refreshes it (when a function to generate a Guest Token is provided). This is configured with the `fetchGuestToken` parameter. By default, this test app is configured pointing to the `fetchGuestTokenFromBackend()` function.

```javascript
const myLightDashboard = presetSdk.embedDashboard({
  id: dashboardId,
  supersetDomain: supersetDomain,
  mountPoint: document.getElementById("dashboard-container"), // any html element that can contain an iframe
  fetchGuestToken: async () => fetchGuestTokenFromBackend(), // `fetchGuestTokenFromBackend()` is a function that returns a Guest Token
  dashboardUiConfig: {},
});
```

#### Providing the SDK with a Guest Token directly

If you don't want to add your API credentials to this example app, you can instead provide a Guest Token directly to the `fetchGuestToken` parameter:

```javascript
const myLightDashboard = presetSdk.embedDashboard({
  id: dashboardId,
  supersetDomain: supersetDomain,
  mountPoint: document.getElementById("dashboard-container"), // any html element that can contain an iframe
  fetchGuestToken: () => "{{myGuestToken}}", // Replace `{{myGuestToken}}` with the generated token
  dashboardUiConfig: {},
});
```

_Refer to [this API endpoint documentation](https://api-docs.preset.io/#b1a9877e-958d-4957-8939-a6d0d3f10e70) to check how to generate a guest token._

Note that the token is **only valid for 5 minutes**, so since the SDK won't be able to refresh it, you'll start facing errors when trying to interact with the dashboard after that time.

### `dashboardUiConfig` parameters

The Preset SDK has configurations that can be modified to change the embedding experience. These can be configured using the `dashboardUiConfig` parameter. In this test app, this configuration is currently implemented in the `templates/index.html` file ([line 40](https://github.com/preset-io/ce-embedded/blob/master/templates/index.html#L40)):

```javascript
const myLightDashboard = presetSdk.embedDashboard({
  id: dashboardId,
  supersetDomain: supersetDomain,
  mountPoint: document.getElementById("dashboard-container"), // any html element that can contain an iframe
  fetchGuestToken: async () => fetchGuestTokenFromBackend(),
  dashboardUiConfig: {
    // dashboard UI config: hideTitle, hideChartControls (optional)
    hideTitle: false, // change it to `true` to hide the dashboard title
    hideChartControls: false, // change it to `true` to hide the chart controls (ellipses menu)
    filters: {
      expanded: true, // change it to `false` so that dashboard filters are collapsed (for vertical filter bar)
    },
  },
});
```

### Customizing the Guest Token permissions

By default, the Guest Token is generated with **no RLS applied**, and access is only granted to the **Dashboard ID** specified previously. You can customize the Guest Token configuration in the `app.py` file ([line 103](https://github.com/preset-io/ce-embedded/blob/master/app.py#L103)):

```python
payload = json.dumps({
    "user": {
        "username": "test_user",
        "first_name": "test",
        "last_name": "user"
    },
    "resources": [{
        "type": "dashboard",
        "id": dashboard_id,
    }],
    "rls": [
        //Add RLS rules here
    ]
})
```
