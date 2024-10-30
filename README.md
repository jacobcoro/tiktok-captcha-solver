Install Playwright:

```bash
python -m playwright install chromium
```

Make sure Chrome is installed in your WSL environment. If it's not:

```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f  # Install dependencies if needed
```

Run in headless by default, uncomment these lines to run with GUI

```python
    browser = playwright.chromium.launch(
        # headless=False,  # Show the browser
        # slow_mo=100,     # Slow down actions for debugging
    )
```

and this to keep the browser open after finish

```
# Keep the browser open for inspection
# input("Press Enter to close the browser...")
```
