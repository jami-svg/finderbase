import re
import trafilatura
import extruct
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from urllib.parse import urlparse

from .schema import ScrapedPage, ContactInfo, SocialLinks, SEOData
from .settings import settings

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"\+?\d{1,4}[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}")

def domain_from_url(url: str) -> str:
    return urlparse(url).netloc

def extract_socials(soup: BeautifulSoup) -> SocialLinks:
    links = SocialLinks()
    mapping = {
        "linkedin.com": "linkedin",
        "twitter.com": "twitter",
        "x.com": "twitter",
        "github.com": "github",
        "facebook.com": "facebook",
        "instagram.com": "instagram",
    }
    for a in soup.find_all("a", href=True):
        href = a["href"]
        for dom, field in mapping.items():
            if dom in href and getattr(links, field) is None:
                setattr(links, field, href)
    return links

def extract_seo(url: str, html: str, soup: BeautifulSoup) -> tuple[str | None, SEOData]:
    data = extruct.extract(html, base_url=url, syntaxes=["json-ld"])
    company_name = None
    for item in data.get("json-ld", []):
        t = item.get("@type")
        if t in ["Organization", "Corporation"]:
            company_name = item.get("name")
            break

    seo = SEOData(
        meta_title=(soup.title.string.strip() if soup.title and soup.title.string else None),
        meta_description=(soup.find("meta", {"name": "description"})["content"]
                          if soup.find("meta", {"name": "description"}) else None),
        og_image=(soup.find("meta", {"property": "og:image"})["content"]
                  if soup.find("meta", {"property": "og:image"}) else None),
    )
    return company_name, seo

def extract_contacts(html: str, text: str) -> ContactInfo:
    emails = sorted(set(EMAIL_RE.findall(text)))
    phones = sorted(set(PHONE_RE.findall(text[:2000])))
    return ContactInfo(emails=emails, phones=phones)

async def fetch_rendered(url: str) -> tuple[int, str, bytes]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"])
        page = await browser.new_page()
        resp = await page.goto(url, wait_until="domcontentloaded", timeout=settings.SCRAPE_TIMEOUT_MS)
        await page.wait_for_timeout(800)
        html = await page.content()
        screenshot = await page.screenshot(full_page=True, type="png")
        status = resp.status if resp else 200
        await browser.close()
        return status, html, screenshot

def html_to_markdown(html: str) -> tuple[str, str]:
    bare = trafilatura.extract(html, include_comments=False) or ""
    md = trafilatura.extract(html, output_format="markdown", include_tables=True) or ""
    return bare, md

async def scrape_one(url: str) -> tuple[ScrapedPage, bytes]:
    status, html, screenshot = await fetch_rendered(url)
    if len(html.encode("utf-8")) > settings.MAX_HTML_BYTES:
        raise RuntimeError("HTML too large")

    bare, md = html_to_markdown(html)
    soup = BeautifulSoup(html, "html.parser")

    company_name, seo = extract_seo(url, html, soup)
    contacts = extract_contacts(html, bare)
    socials = extract_socials(soup)

    title = (soup.title.string.strip() if soup.title and soup.title.string else "No Title")
    page = ScrapedPage(
        url=url,
        domain=domain_from_url(url),
        title=title,
        markdown=md,
        company_name=company_name,
        contacts=contacts,
        socials=socials,
        seo=seo,
        status_code=status,
    )
    return page, screenshot
