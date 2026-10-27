
import re

import pytest
from playwright.sync_api import Page, expect

AMAZON_URL = "https://www.amazon.in/"


def open_amazon(page: Page):
    """Open Amazon and detect security challenges."""
    response = page.goto(
        AMAZON_URL,
        wait_until="domcontentloaded",
        timeout=60000,
    )

    print("HTTP status:", response.status if response else "No response")

    page.wait_for_timeout(5000)
    body_text = page.locator("body").inner_text(timeout=10000)

    print("Page title:", page.title())
    print("Page text:", body_text[:1000])

    if (
        "Click the button below to continue shopping" in body_text
        or "Continue shopping" in body_text
    ):
        pytest.skip(
            "Amazon returned a security challenge. "
            "Search functionality could not be tested."
        )

    search_box = page.locator("#twotabsearchtextbox")

    if response and response.status == 202 and not page.title() and not body_text.strip():
        pytest.skip(
        "Amazon returned HTTP 202 with an empty page; "
        "product search could not be verified."
    )

    if not search_box.is_visible():
        pytest.fail(
        "Amazon's normal homepage/search box was unavailable."
    )

    return search_box


def test_amazon_product_search(page: Page):
    """TC06: Search for a laptop and verify the response."""
    search_box = open_amazon(page)

    search_box.fill("laptop")
    search_box.press("Enter")

    expect(page).to_have_url(
        re.compile("laptop", re.IGNORECASE),
        timeout=20000,
    )

    body_text = page.locator("body").inner_text(timeout=10000)

    if (
       "Oops! It's rush hour" in body_text
       or "traffic is piling up" in body_text.lower()
    ):
        pytest.skip(
        "Amazon returned its temporary traffic-error page; "
        "product search could not be verified."
    )

    results = page.locator("[data-component-type='s-search-result']")
    expect(results.first).to_be_visible(timeout=15000)


def test_search_box_accepts_different_keywords(page: Page):
    """TC07: Verify the search box accepts different keywords."""
    search_box = open_amazon(page)

    for keyword in ["phone", "headphones", "keyboard"]:
        search_box.fill(keyword)
        expect(search_box).to_have_value(keyword)


def test_search_box_can_be_cleared(page: Page):
    """TC08: Verify the search box can be cleared."""
    search_box = open_amazon(page)

    search_box.fill("laptop")
    expect(search_box).to_have_value("laptop")

    search_box.clear()
    expect(search_box).to_have_value("")


def test_search_box_accepts_spaces(page: Page):
    """TC09: Verify a multi-word search phrase can be entered."""
    search_box = open_amazon(page)

    keyword = "wireless headphones"
    search_box.fill(keyword)

    expect(search_box).to_have_value(keyword)


def test_search_url_contains_submitted_keyword(page: Page):
    """TC10: Verify the search URL contains the submitted keyword."""
    search_box = open_amazon(page)

    keyword = "computer mouse"
    search_box.fill(keyword)
    search_box.press("Enter")

    expect(page).to_have_url(
        re.compile("computer", re.IGNORECASE),
        timeout=20000,
    )
