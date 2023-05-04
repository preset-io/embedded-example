# ce-embedded
Sample (and extremely simple) Embedded app that can be used to reproduce/investigate embedded-related issues.

## How to use it

### One-time actions
1. Clone the repository.
2. Duplicate the `.env-example` file, and save it as `.env`. 
3. Replace all values in there accordingly (no need to add quotes etc):
    a) Replace `Your API Token` with a token created (and enabled) from Manager (line 1).
    b) Replace `Your API Secret` with its corresponding secret (line 2).
    c) Replace `WorkspaceSlug` and `WorkspaceRegion` in the URL (line 4).  
    d) Replace `Team Slug` with your Team Slug (line 5).
    e) Replace `Workspace Slug` with the Workspace Slug (line 6). 
4. Make sure you have `pyenv` installed, so you can properly create and manage Python virtual environments.
5. Create a new virtual environment for this project.
6. Run `pip install --upgrade pip` to update pip.
7. Run `pip install -r requirements.txt` to install all dependencies for this project. 

### Steps to be executed every time you want to run it
1. Replace the `Dashboard ID to be embedded` in the `.env` file (line 3) with the corresponding dashboard ID retrieved from Superset UI.
2. Activate the virtual environment created for this project.
3. Make sure you are inside this repository, and run `python app.py` in the terminal. This would start the flask app.
4. Access `http://127.0.0.1:8080/` on the browser.
5. Once testing is done, press `control + C` in the terminal to stop the flask app.
6. Deactivate the virtual environment.


### Modifying dashboard UI configurations
If you want to modify the dashboard configuration (`hideTitle`, etc), you can do it in the `templates/index.html` file (line 34). Example:
``` javascript
dashboardUiConfig: { // dashboard UI config: hideTitle, hideTab, hideChartControls (optional)
    hideTitle: false,
    hideTab: false,
    hideChartControls: false,
}
```