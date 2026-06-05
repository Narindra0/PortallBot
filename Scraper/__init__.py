# Module de scraping
from Scraper.asako import AsakoScraper, surveiller_asako
from Scraper.base import BaseScraper
from Scraper.portal import PortalScraper, surveiller_portal

__all__ = ['surveiller_portal', 'surveiller_asako', 'PortalScraper', 'AsakoScraper', 'BaseScraper']
