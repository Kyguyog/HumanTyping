from playwright.sync_api import sync_playwright

from humantyping import HumanTyper


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://google.com")

        typer = HumanTyper(wpm=70)
        search_box = page.locator("[name='q']")
        search_box.click()
        typer.type_sync(search_box, "Playwright sync with human typing")

        page.wait_for_timeout(2000)
        browser.close()


if __name__ == "__main__":
    main()
