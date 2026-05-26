import httpx
import feedparser
import json
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from models.models import Opportunity, OpportunityType

logger = logging.getLogger(__name__)

FEDERAL_REGISTER_API = "https://www.federalregister.gov/api/v1/documents.json"

GRANT_SEARCH_TERMS = [
    "notice of funding opportunity",
    "nofo grant",
    "cooperative agreement funding",
    "grant announcement",
    "funding opportunity announcement",
]


def fetch_federal_register(db: Session):
    """Fetch grant notices from the Federal Register public API (no auth required)."""
    saved = 0
    try:
        for term in GRANT_SEARCH_TERMS[:3]:
            params = [
                ("per_page", "20"),
                ("order", "newest"),
                ("conditions[term]", term),
                ("fields[]", "title"),
                ("fields[]", "abstract"),
                ("fields[]", "agencies"),
                ("fields[]", "publication_date"),
                ("fields[]", "html_url"),
                ("fields[]", "document_number"),
                ("fields[]", "action"),
            ]
            resp = httpx.get(FEDERAL_REGISTER_API, params=params, follow_redirects=True, timeout=20)
            resp.raise_for_status()
            data = resp.json()

            for item in data.get("results", []):
                doc_num = item.get("document_number", "")
                external_id = f"federal-register-{doc_num}"
                if not doc_num:
                    continue
                existing = db.query(Opportunity).filter_by(external_id=external_id).first()
                if existing:
                    continue

                title = item.get("title", "")
                # Skip non-grant documents
                title_lower = title.lower()
                if not any(kw in title_lower for kw in ["grant", "funding opportunity", "nofo", "cooperative agreement", "notice of award"]):
                    continue

                agencies = item.get("agencies", [])
                agency_name = agencies[0].get("name", "") if agencies else ""

                posted_date = None
                if item.get("publication_date"):
                    try:
                        posted_date = datetime.strptime(item["publication_date"], "%Y-%m-%d")
                    except Exception:
                        pass

                opp = Opportunity(
                    external_id=external_id,
                    title=title[:500],
                    description=item.get("abstract") or item.get("action") or "",
                    opportunity_type=OpportunityType.grant,
                    source="Federal Register",
                    source_url=item.get("html_url", ""),
                    agency=agency_name,
                    posted_date=posted_date,
                )
                db.add(opp)
                saved += 1

        db.commit()
        logger.info(f"Federal Register: saved {saved} new opportunities")
        return saved
    except Exception as e:
        logger.error(f"Federal Register fetch error: {e}")
        db.rollback()
        return 0


def fetch_usaspending(db: Session):
    """Fetch recent federal awards/grants from USASpending.gov public API."""
    try:
        payload = {
            "filters": {
                "award_type_codes": ["02", "03", "04", "05"],  # grants
                "time_period": [{"start_date": "2026-01-01", "end_date": datetime.now().strftime("%Y-%m-%d")}],
            },
            "fields": ["Award ID", "Recipient Name", "Award Amount", "Awarding Agency", "Award Type", "Description", "Period of Performance Current End Date"],
            "page": 1,
            "limit": 20,
            "sort": "Award Amount",
            "order": "desc",
        }
        resp = httpx.post(
            "https://api.usaspending.gov/api/v2/search/spending_by_award/",
            json=payload,
            timeout=20,
            follow_redirects=True,
        )
        resp.raise_for_status()
        data = resp.json()

        saved = 0
        for item in data.get("results", []):
            award_id = item.get("Award ID", "")
            if not award_id:
                continue
            external_id = f"usaspending-{award_id}"
            existing = db.query(Opportunity).filter_by(external_id=external_id).first()
            if existing:
                continue

            close_date = None
            if item.get("Period of Performance Current End Date"):
                try:
                    close_date = datetime.strptime(item["Period of Performance Current End Date"], "%Y-%m-%d")
                except Exception:
                    pass

            amount = item.get("Award Amount")
            try:
                amount = float(amount) if amount else None
            except Exception:
                amount = None

            opp = Opportunity(
                external_id=external_id,
                title=f"Federal Grant — {item.get('Recipient Name', 'Unknown Recipient')}",
                description=item.get("Description") or "",
                opportunity_type=OpportunityType.grant,
                source="USASpending.gov",
                source_url=f"https://www.usaspending.gov/award/{award_id}",
                agency=item.get("Awarding Agency", ""),
                funding_amount_max=amount,
                close_date=close_date,
                posted_date=datetime.now(timezone.utc),
            )
            db.add(opp)
            saved += 1

        db.commit()
        logger.info(f"USASpending: saved {saved} new opportunities")
        return saved
    except Exception as e:
        logger.error(f"USASpending fetch error: {e}")
        db.rollback()
        return 0


def fetch_state_feeds(db: Session):
    """Fetch from state grant RSS/Atom feeds."""
    STATE_FEEDS = [
        {"state": "CA", "url": "https://www.grants.ca.gov/api/v1/grants/rss", "source": "CA Grants Portal"},
        {"state": "TX", "url": "https://comptroller.texas.gov/purchasing/contracts/rss.xml", "source": "TX Comptroller"},
        {"state": "NY", "url": "https://apps.cio.ny.gov/apps/cfa/rss", "source": "NY Funding"},
    ]

    total_saved = 0
    for feed_config in STATE_FEEDS:
        try:
            feed = feedparser.parse(feed_config["url"])
            saved = 0
            for entry in feed.entries[:20]:
                external_id = f"{feed_config['source']}-{entry.get('id', entry.get('link', ''))}"
                existing = db.query(Opportunity).filter_by(external_id=external_id[:255]).first()
                if existing:
                    continue

                opp = Opportunity(
                    external_id=external_id[:255],
                    title=entry.get("title", "")[:500],
                    description=entry.get("summary", ""),
                    opportunity_type=OpportunityType.grant,
                    source=feed_config["source"],
                    source_url=entry.get("link", ""),
                    state=feed_config["state"],
                    posted_date=datetime.now(timezone.utc),
                )
                db.add(opp)
                saved += 1

            db.commit()
            total_saved += saved
            logger.info(f"{feed_config['source']}: saved {saved} new opportunities")
        except Exception as e:
            logger.error(f"{feed_config['source']} fetch error: {e}")
            db.rollback()

    return total_saved


def run_full_crawl(db: Session):
    """Run all crawlers and return total saved."""
    total = 0
    total += fetch_federal_register(db)
    total += fetch_usaspending(db)
    total += fetch_state_feeds(db)
    logger.info(f"Full crawl complete: {total} new opportunities saved")
    return total
