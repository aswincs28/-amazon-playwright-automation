import re

import pytest
from playwright.sync_api import Page, expect


AMAZON_URL = "https://www.amazon.in/"


def open_amazon_homepage(page: Page) -> None:
    """Open Amazon and detect whether its normal homepage is available."""
    response = page.goto(
        AMAZON_URL,
        wait_until="domcontentloaded",
        timeout=60000,
    )

    status = response.status if response else None
    print(f"HTTP status: {status}")
    print(f"Final URL: {page.url}")

    # Allow time for the page to render.
    page.wait_for_timeout(5000)

    body_text = page.locator("body").inner_text(timeout=10000)
    print(f"Page title: {page.title()}")
    print(f"Page text: {body_text[:1000]}")

    page.screenshot(
        path="amazon_debug.png",
        full_page=True,
    )

    # Detect the known Amazon security challenge.
    if (
        "Click the button below to continue shopping" in body_text
        or "Continue shopping" in body_text
    ):
        pytest.skip(
            "Amazon returned a security challenge instead of "
            "the normal homepage. Homepage checks were skipped."
        )

    # A non-challenge response is not sufficient by itself:
    # verify that the expected homepage element exists.
    if status == 202 and not page.title() and not body_text.strip():
     pytest.skip(
        "Amazon returned HTTP 202 with an empty page; "
        "homepage functionality could not be verified."
     )

    if not page.locator("#twotabsearchtextbox").is_visible():
        pytest.fail(
        "Amazon's normal homepage/search box was not available. "
        f"HTTP status: {status}; title: {page.title()!r}"
     )


def test_amazon_homepage(page: Page):
    """TC01: Verify that Amazon's homepage is available."""
    open_amazon_homepage(page)

    expect(page.locator("#twotabsearchtextbox")).to_be_visible()


def test_amazon_page_title(page: Page):
    """TC02: Verify the page title identifies Amazon."""
    open_amazon_homepage(page)

    expect(page).to_have_title(re.compile(r"Amazon", re.IGNORECASE))


def test_amazon_logo_visible(page: Page):
    """TC03: Verify the Amazon logo is visible."""
    open_amazon_homepage(page)

    expect(page.locator("#nav-logo-sprites")).to_be_visible()


def test_search_box_visible_and_enabled(page: Page):
    """TC04: Verify the search box is visible and enabled."""
    open_amazon_homepage(page)

    search_box = page.locator("#twotabsearchtextbox")
    expect(search_box).to_be_visible()
    expect(search_box).to_be_enabled()


def test_search_box_accepts_text(page: Page):
    """TC05: Verify that a product keyword can be entered."""
    open_amazon_homepage(page)

    search_box = page.locator("#twotabsearchtextbox")
    search_box.fill("laptop")

    expect(search_box).to_have_value("laptop")
