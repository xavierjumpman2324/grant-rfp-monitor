import json
import logging
from anthropic import Anthropic
from config import get_settings
from models.models import Opportunity, User

logger = logging.getLogger(__name__)
settings = get_settings()


def get_client():
    if not settings.anthropic_api_key:
        return None
    return Anthropic(api_key=settings.anthropic_api_key)


def analyze_opportunity(opportunity: Opportunity, user: User) -> dict:
    """Use Claude to analyze an opportunity for relevance to a specific user."""
    client = get_client()
    if not client:
        return {
            "relevance_score": 0.5,
            "summary": "AI analysis unavailable — add ANTHROPIC_API_KEY to enable.",
            "match_reason": "API key not configured",
            "action_items": [],
            "severity": "medium",
        }

    focus_areas = json.loads(user.focus_areas) if user.focus_areas else []
    states = json.loads(user.states) if user.states else []

    prompt = f"""You are an expert grant and RFP analyst helping {user.organization_name or "an organization"}
({user.organization_type or "unknown type"}) find relevant funding opportunities.

Their focus areas: {", ".join(focus_areas) if focus_areas else "not specified"}
Their states of interest: {", ".join(states) if states else "any"}

Analyze this opportunity:

TITLE: {opportunity.title}
TYPE: {opportunity.opportunity_type}
AGENCY: {opportunity.agency or "Unknown"}
SOURCE: {opportunity.source}
FUNDING: ${opportunity.funding_amount or 0:,.0f} - ${opportunity.funding_amount_max or 0:,.0f}
CLOSE DATE: {opportunity.close_date.strftime("%B %d, %Y") if opportunity.close_date else "Not specified"}
DESCRIPTION: {(opportunity.description or "")[:1500]}

Respond in JSON with exactly these fields:
{{
  "relevance_score": <float 0.0-1.0>,
  "summary": "<2-3 sentence plain-English summary>",
  "match_reason": "<one sentence: why this matches or doesn't match their focus>",
  "action_items": ["<specific step 1>", "<specific step 2>"],
  "severity": "<high|medium|low based on relevance and urgency>"
}}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception as e:
        logger.error(f"AI analysis error for opportunity {opportunity.id}: {e}")
        return {
            "relevance_score": 0.5,
            "summary": opportunity.description[:300] if opportunity.description else "No description available.",
            "match_reason": "Analysis unavailable",
            "action_items": ["Review opportunity details", "Check eligibility requirements"],
            "severity": "medium",
        }


def chat_with_ai(user: User, message: str, history: list) -> str:
    """AI compliance Q&A chatbot for grant/RFP questions."""
    client = get_client()
    if not client:
        return "AI chat is unavailable — an Anthropic API key is required. Add it to your .env file."

    focus_areas = json.loads(user.focus_areas) if user.focus_areas else []

    system = f"""You are a helpful grant and RFP advisor for {user.organization_name or "an organization"}
({user.organization_type or "organization"}). Their focus areas: {", ".join(focus_areas) if focus_areas else "various areas"}.

Help them find opportunities, understand grant requirements, write stronger applications, and navigate the federal
procurement process. Be specific and actionable. Always note that for legal or official guidance they should
consult a grants professional or attorney."""

    messages = []
    for msg in history[-10:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            system=system,
            messages=messages,
        )
        return response.content[0].text
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return "Sorry, I encountered an error. Please try again."


def generate_weekly_digest(user: User, opportunities: list) -> str:
    """Generate a weekly digest email body summarizing top opportunities."""
    client = get_client()
    if not client or not opportunities:
        return ""

    opp_list = "\n".join([
        f"- {o.title} | {o.source} | Closes: {o.close_date.strftime('%b %d') if o.close_date else 'TBD'} | ${o.funding_amount_max or 0:,.0f} max"
        for o in opportunities[:10]
    ])

    focus_areas = json.loads(user.focus_areas) if user.focus_areas else []

    prompt = f"""Write a concise weekly funding digest email for {user.organization_name or "our organization"}.
Focus areas: {", ".join(focus_areas) if focus_areas else "general"}

Top opportunities this week:
{opp_list}

Write 3-4 sentences highlighting the best opportunities and any urgent deadlines.
Be specific, professional, and encouraging. No subject line needed."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except Exception as e:
        logger.error(f"Digest generation error: {e}")
        return ""
