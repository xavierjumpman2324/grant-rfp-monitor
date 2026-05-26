import httpx
import feedparser
import json
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from models.models import Opportunity, OpportunityType

logger = logging.getLogger(__name__)

GRANTS_GOV_API = "https://api.grants.gov/v2/api/search"
SAM_GOV_API = "https://api.sam.gov/opportunities/v2/search"

STATE_RSS_FEEDS = [
    {"state": "CA", "url": "https://www.grants.ca.gov/rss/opportunities.xml", "source": "CA Grants Portal"},
    {"state": "NY", "url": "https://grantsreform.ny.gov/opportunities/rss", "source": "NY Grants"},
    {"state": "TX", "url": "https://comptroller.texas.gov/purchasing/contracts/rss.xml", "source": "TX Comptroller"},
]


def fetch_grants_gov(db: Session):
    """Fetch recent grants from grants.gov public API."""
    try:
        payload = {
            "keyword": "",
            "oppStatuses": "forecasted|posted",
            "rows": 50,
            "sortBy": "openDate|desc",
        }
        resp = httpx.post(GRANTS_GOV_API, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        saved = 0
        for item in data.get("oppHits", []):
            external_id = f"grants.gov-{item.get('id')}"
            existing = db.query(Opportunity).filter_by(external_id=external_id).first()
            if existing:
                continue

            close_date = None
            if item.get("closeDate"):
                try:
                    close_date = datetime.strptime(item["closeDate"], "%m%d%Y")
                except Exception:
                    pass

            posted_date = None
            if item.get("openDate"):
                try:
                    posted_date = datetime.strptime(item["openDate"], "%m%d%Y")
                except Exception:
                    pass

            opp = Opportunity(
                external_id=external_id,
                title=item.get("title", "")[:500],
                description=item.get("synopsis", ""),
                opportunity_type=OpportunityType.grant,
                source="grants.gov",
                source_url=f"https://www.grants.gov/search-results-detail/{item.get('id')}",
                agency=item.get("agencyName", ""),
                funding_amount=item.get("awardFloor"),
                funding_amount_max=item.get("awardCeiling"),
                posted_date=posted_date,
                close_date=close_date,
                category=item.get("oppCategory", {}).get("cat", ""),
                cfda_number=item.get("cfdaList", [""])[0] if item.get("cfdaList") else "",
            )
            db.add(opp)
            saved += 1

        db.commit()
        logger.info(f"grants.gov: saved {saved} new opportunities")
        return saved
    except Exception as e:
        logger.error(f"grants.gov fetch error: {e}")
        db.rollback()
        return 0


def fetch_sam_gov(db: Session, api_key: str = "DEMO_KEY"):
    """Fetch recent RFPs/contracts from SAM.gov public API."""
    try:
        params = {
            "api_key": api_key,
            "limit": 50,
            "offset": 0,
            "postedFrom": datetime.now().strftime("%m/%d/%Y"),
            "ptype": "o,p,r,s",  # solicitations, presolicitations, sources sought, special notices
        }
        resp = httpx.get(SAM_GOV_API, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        saved = 0
        for item in data.get("opportunitiesData", []):
            external_id = f"sam.gov-{item.get('noticeId')}"
            existing = db.query(Opportunity).filter_by(external_id=external_id).first()
            if existing:
                continue

            opp_type = OpportunityType.rfp
            ptype = item.get("type", "").lower()
            if "rfq" in ptype or "quote" in ptype:
                opp_type = OpportunityType.rfq
            elif "rfi" in ptype or "information" in ptype:
                opp_type = OpportunityType.rfi
            elif "contract" in ptype:
                opp_type = OpportunityType.contract

            close_date = None
            if item.get("responseDeadLine"):
                try:
                    close_date = datetime.fromisoformat(item["responseDeadLine"].replace("Z", "+00:00"))
                except Exception:
                    pass

            posted_date = None
            if item.get("postedDate"):
                try:
                    posted_date = datetime.fromisoformat(item["postedDate"].replace("Z", "+00:00"))
                except Exception:
                    pass

            opp = Opportunity(
                external_id=external_id,
                title=item.get("title", "")[:500],
                description=item.get("description", ""),
                opportunity_type=opp_type,
                source="sam.gov",
                source_url=item.get("uiLink", ""),
                agency=item.get("departmentName", "") or item.get("subtierName", ""),
                posted_date=posted_date,
                close_date=close_date,
                naics_code=item.get("naicsCode", ""),
                state=item.get("placeOfPerformance", {}).get("state", {}).get("code", ""),
            )
            db.add(opp)
            saved += 1

        db.commit()
        logger.info(f"sam.gov: saved {saved} new opportunities")
        return saved
    except Exception as e:
        logger.error(f"sam.gov fetch error: {e}")
        db.rollback()
        return 0


def fetch_state_feeds(db: Session):
    """Fetch from state grant RSS feeds."""
    total_saved = 0
    for feed_config in STATE_RSS_FEEDS:
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
    total += fetch_grants_gov(db)
    total += fetch_sam_gov(db)
    total += fetch_state_feeds(db)
    logger.info(f"Full crawl complete: {total} new opportunities saved")
    return total
