import concurrent.futures
from urllib.parse import quote


INSTALL_HINT = (
    "Playwright is not set up. Run: "
    "pip install playwright  then  playwright install chromium"
)


def normalize_url(url: str):

    if not url:
        return url

    if not url.startswith(("http://", "https://")):
        return "https://" + url

    return url


def _open_website(url: str):

    from playwright.sync_api import sync_playwright

    url = normalize_url(url)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(
                url,
                timeout=30000,
                wait_until="domcontentloaded",
            )
            return {
                "success": True,
                "url": url,
                "title": page.title(),
                "text": page.inner_text("body")[:3000],
            }
        finally:
            browser.close()


def _web_search(query: str):

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(
                "https://html.duckduckgo.com/html/?q=" + quote(query),
                timeout=30000,
                wait_until="domcontentloaded",
            )

            results = []

            for el in page.query_selector_all(".result")[:5]:

                link = el.query_selector(".result__a")
                snippet = el.query_selector(".result__snippet")

                if link:
                    results.append({
                        "title": link.inner_text(),
                        "url": link.get_attribute("href"),
                        "snippet": (
                            snippet.inner_text()
                            if snippet
                            else ""
                        ),
                    })

            return {
                "success": True,
                "query": query,
                "results": results,
            }
        finally:
            browser.close()


def _extract_data(url: str, selector: str = None):

    from playwright.sync_api import sync_playwright

    url = normalize_url(url)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(
                url,
                timeout=30000,
                wait_until="domcontentloaded",
            )

            if selector:
                elements = page.query_selector_all(selector)
                data = [
                    e.inner_text()
                    for e in elements
                ][:50]
                return {
                    "success": True,
                    "url": url,
                    "selector": selector,
                    "data": data,
                }

            return {
                "success": True,
                "url": url,
                "text": page.inner_text("body")[:3000],
            }
        finally:
            browser.close()


def run_in_browser(fn, *args):

    # Playwright's sync API cannot run inside an asyncio loop, so we
    # always run it in a dedicated worker thread (which has no loop).
    try:
        import playwright  # noqa: F401
    except ImportError:
        return {
            "success": False,
            "message": INSTALL_HINT,
        }

    try:
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=1
        ) as executor:
            return executor.submit(fn, *args).result()
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "hint": INSTALL_HINT,
        }


class BrowserService:

    @staticmethod
    def open_website(url: str):
        return run_in_browser(_open_website, url)

    @staticmethod
    def web_search(query: str):
        return run_in_browser(_web_search, query)

    @staticmethod
    def extract_data(url: str, selector: str = None):
        return run_in_browser(_extract_data, url, selector)
