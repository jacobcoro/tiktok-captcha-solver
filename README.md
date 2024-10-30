Install Playwright:

```
python -m playwright install chromium
```

Make sure Chrome is installed in your WSL environment. If it's not:

```
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f  # Install dependencies if needed
```
