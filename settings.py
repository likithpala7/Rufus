# settings.py
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

PLAYWRIGHT_BROWSER_TYPE = "chromium"  # or "firefox" / "webkit"
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True  # set to False if you want to see the browser during development
}
