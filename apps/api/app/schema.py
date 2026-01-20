from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class SocialLinks(BaseModel):
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    github: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    other: List[str] = Field(default_factory=list)

class ContactInfo(BaseModel):
    emails: List[str] = Field(default_factory=list)
    phones: List[str] = Field(default_factory=list)
    address: Optional[str] = None

class SEOData(BaseModel):
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    og_image: Optional[str] = None

class ScrapedPage(BaseModel):
    url: str
    domain: str
    scraped_at: datetime = Field(default_factory=datetime.utcnow)

    title: str = "No Title"
    summary: Optional[str] = None
    markdown: str

    company_name: Optional[str] = None
    contacts: ContactInfo = Field(default_factory=ContactInfo)
    socials: SocialLinks = Field(default_factory=SocialLinks)

    language: Optional[str] = None
    status_code: int = 200
    screenshot_path: Optional[str] = None
    seo: SEOData = Field(default_factory=SEOData)
