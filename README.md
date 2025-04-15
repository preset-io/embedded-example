# embedded-example

Sample (and extremely simple) Flask app that can be used to test the Preset Embedding experience!
**_Note that this app is solely intended to demonstrate the embedded implementation, and shouldn't be used in a Production environment._**

## How to use it

This project uses Python to run a Flask app. We strongly encourage using a [Python Virtual environment](https://docs.python.org/3/library/venv.html) to install it (this tutorial won't cover this part).

### Implementation actions

Start by cloning the repository to your local environment. Then, duplicate the `.env-example` file, and save it as `.env` in the root folder (the file is automatically git-ignored). This file is responsible for providing the app with your credentials, team and dashboard information. Replace template values in there accordingly (you might need to add quotes if the values have special characters).

Let's take a look on how to fill it:

#### Authentication details _(optional)_

**DISCLAIMER:** Your API token and secret are **only stored in this local file** — this information is not processed or synced anywhere else. It's also possible to run this app without providing your credentials, however you would have to generate the Guest Token on your end (for example, using Postman), and then provide the Guest Token to the SDK. Additionally, the Guest Token is only valid for 5 minutes, so after that you might start facing errors when interacting with the embedded dashboard.

If you would like to avoid adding your credentials to this file, feel free to just skip this step, and [provide the guest token directly](https://github.com/preset-io/embedded-example?tab=readme-ov-file#providing-the-sdk-with-a-guest-token-directly) OR [authenticate using a PEM key](https://github.com/preset-io/embedded-example?tab=readme-ov-file#pem-key-authentication).

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
4. Run `pip install -r requirements/requirements.txt` to install all dependencies for this project.

### Running the application

1. Run `flask --app app run --port=8080 --debug` in the terminal (inside the root folder). This would start the Flask app. Feel free to change the `--port` accordingly in case `8080` is already in use. The `--debug` flag ensures the server automatically reloads when changes are saved to the `app.py` file.
2. Access `http://127.0.0.1:8080/` on the browser. You should see an `iframe` in the full browser size, which would load the dashboard in embedded mode.

### Stopping the app

1. Once testing is done, press <kbd>control + C</kbd> in the terminal to stop the Flask app.
2. Deactivate the virtual environment.

## Changing the app configurations

### Authentication

Since the Guest Token is only valid for 5 minutes, the SDK automatically refreshes it (when a function to generate a Guest Token is provided). This is configured with the `fetchGuestToken` parameter. By default, this test app is configured pointing to the `fetchGuestTokenFromBackend()` function.

```javascript
const myLightDashboard = presetSdk.embedDashboard({
  id: dashboardId,
  supersetDomain: supersetDomain,
  mountPoint: document.getElementById("dashboard-container"),
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
  mountPoint: document.getElementById("dashboard-container"),
  fetchGuestToken: () => "{{myGuestToken}}", // Replace `{{myGuestToken}}` with the generated token
  dashboardUiConfig: {},
});
```

_Refer to [this API endpoint documentation](https://api-docs.preset.io/#b1a9877e-958d-4957-8939-a6d0d3f10e70) to check how to generate a guest token._

Note that the token is **only valid for 5 minutes**, so since the SDK won't be able to refresh it, you'll start facing errors when trying to interact with the dashboard after that time.

#### PEM Key authentication

**Note: You must have `OpenSSL` installed to be able to generate the keys.**

To authenticate the guest user, two API calls are needed:
* One to authenticate your API credentials and retrieve a `JWT` token.
* Another one that uses this `JWT` to generate a `guest_token`.

It's possible to use a set of public and private PEM keys to generate the `guest_token` locally and avoid these two calls. Refer to [this section](https://docs.preset.io/docs/step-2-deployment#1-create-guest-tokens-backend) if you want to generate the PEM keys on your end, or alternatively run below command to automatically create a key pair:

``` bash
flask generate-keys
```

Then, use below command to copy the public key:

``` bash
pbcopy < keys/embedded-example-public-key.pem
```

Access [Preset Manager](https://manage.app.preset.io/app/), click on the three ellipses for your Workspace and select **Edit Workspace Settings**. Then navigate to the **Embedded** tab, and paste the public key content. Finally, copy the **Key Id** visible in the UI, and add it to your `.env` file.

Then access `http://localhost:8081/?auth_type=pem` in the browser to load the embedded dashboard using a guest token that's encoded locally.

### `dashboardUiConfig` parameters

The Preset SDK has configurations that can be modified to change the embedding experience. These can be configured using the `dashboardUiConfig` parameter. In this test app, this configuration is currently implemented in the `templates/index.html` file ([line 40](https://github.com/preset-io/embedded-example/blob/master/templates/index.html#L40)):

```javascript
const myLightDashboard = presetSdk.embedDashboard({
  id: dashboardId,
  supersetDomain: supersetDomain,
  mountPoint: document.getElementById("dashboard-container"),
  fetchGuestToken: async () => fetchGuestTokenFromBackend(),
  dashboardUiConfig: {
    // dashboard UI config: hideTitle, hideChartControls (optional)
    hideTitle: false, // change it to `true` to hide the dashboard title
    hideChartControls: false, // change it to `true` to hide the chart controls (ellipses menu)
    filters: {
      expanded: true, // change it to `false` so that dashboard filters are collapsed (for vertical filter bar)
    },
    urlParams: { // URL parameters to be used with the ``{{url_param()}}`` Jinja macro
      param_name: "value",
      other_param: "value",
    }
  },
});
```

### Managing the dashboard filter state

By default, a dashboard is loaded in Embedded mode with its default filter configuration. It's possible to pass a `permalink_key` to load the dashboard with a particular filter configuration:

```javascript
const myLightDashboard = presetSdk.embedDashboard({
  id: dashboardId,
  supersetDomain: supersetDomain,
  mountPoint: document.getElementById("dashboard-container"),
  fetchGuestToken: async () => fetchGuestTokenFromBackend(),
  dashboardUiConfig: {
    urlParams: {
      "permalink_key": "aE6zJGOJK3k" // Key generated via the API with the desired filter state
    }
  }
});
```

It's also possible to retrieve the current data mask configuration (which includes the filter state) at any time using the `getDataMask()` method:

``` javascript
const dashboardElement = await myLightDashboard; // `myLightDashboard` is a promise that resolves to the dashboard instance
...
const currentDataMaskConfig = await dash.dashboardElement();
console.log('The current data mask configuration for the dashboard is: ', datamask);
```

Alternatively, you can configure the dashboard to automatically emit data mask changes to a method. This is specially useful if you want to monitor filter usage:

```javascript
const myLightDashboard = presetSdk.embedDashboard({
  id: dashboardId,
  supersetDomain: supersetDomain,
  mountPoint: document.getElementById("dashboard-container"),
  fetchGuestToken: async () => fetchGuestTokenFromBackend(),
  dashboardUiConfig: {
    emitDataMasks: true, // When set to true, the dashboard emits filter state changes
  }
});

function processDataMaskChange(dataMaskConfig) {
  console.log("Received a data mask change from the dashboard:");
  console.log(dataMaskConfig);
}

myLightDashboard.then(dashboardElement => {
  dashboardElement.observeDataMask(processDataMaskChange);
});
```

### Using a custom `iframeTitle`

By default, the `iframe` element is created with its title set to `Embedded Dashboard`. It's possible to specify a custom title through the `iframeTitle` parameter:

```javascript
const myLightDashboard = presetSdk.embedDashboard({
  id: dashboardId,
  supersetDomain: supersetDomain,
  mountPoint: document.getElementById("dashboard-container"),
  fetchGuestToken: async () => fetchGuestTokenFromBackend(),
  iframeTitle: "Preset Embedded Dashboard", // optional: title for the iframe
});
```

### Custom iframe Sandbox attributes

Sandbox attributes allow you to change restrictions applied to the `iframe` element. For example, links clicked in the `iframe` (even when configured to open in a new tab) are blocked by default. To allow links to successfully load in a new tab, you can include the `allow-popups-to-escape-sandbox` sandbox property:

```javascript
const myLightDashboard = presetSdk.embedDashboard({
  id: dashboardId,
  supersetDomain: supersetDomain,
  mountPoint: document.getElementById("dashboard-container"),
  fetchGuestToken: async () => fetchGuestTokenFromBackend(),
  iframeSandboxExtras: ['allow-popups-to-escape-sandbox'],
});
```

### Enforce a specific referrerPolicy value for the `iframe`

Your hosting app might specify a `referrerPolicy` value for `iframes`. The Referrer header needs to be included in the `iframe` request so that the allowed domains are vaildated. The example code in the `app.py` file already enforces the `strict-origin-when-cross-origin` value for the `referrerPolicy`:

```javascript
const myLightDashboard = presetSdk.embedDashboard({
  id: dashboardId,
  supersetDomain: supersetDomain,
  mountPoint: document.getElementById("dashboard-container"),
  fetchGuestToken: async () => fetchGuestTokenFromBackend(),
  referrerPolicy: "strict-origin-when-cross-origin",
});
```

### Customizing the Guest Token permissions

By default, the Guest Token is generated with **no RLS applied**, and access is only granted to the **Dashboard ID** specified previously. You can customize the Guest Token configuration in the `app.py` file, according to the authentication method used:

For guest tokens generated via the API ([line 207](https://github.com/preset-io/embedded-example/blob/master/app.py#L207)):

```python
{
    "user": {
        "username": "test_user",
        "first_name": "test",
        "last_name": "user"
    },
    "resources": [
        {
            "type": "dashboard",
            "id": dashboard_id,
        }
    ],
    "rls": [
        # Apply an RLS to a specific dataset
        # { "dataset": dataset_id, "clause": "column = 'filter'" },
        # Apply an RLS to all datasets
        # { "clause": "column = 'filter'" },
    ]
}
```

For guest tokens generated using a PEM key ([line 254](https://github.com/preset-io/embedded-example/blob/master/app.py#L254)):


``` python
{
    "user": {
        "username": "test_user",
        "first_name": "test",
        "last_name": "user"
    },
    "resources": [
        {
            "type": "dashboard",
            "id": dashboard_id
        }
    ],
    "rls_rules": [
        # Apply an RLS to a specific dataset
        # { "dataset": dataset_id, "clause": "column = 'filter'" },
        # Apply an RLS to all datasets
        # { "clause": "column = 'filter'" },
    ],
    "type": "guest",
    "aud": workspace_slug,
}
```
