import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def send_email(to_email: str, subject: str, html_content: str) -> bool:
    if not settings.sendgrid_api_key:
        logger.warning("SendGrid API key not set — email not sent")
        return False
    try:
        message = Mail(
            from_email=settings.sendgrid_from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
        )
        sg = SendGridAPIClient(settings.sendgrid_api_key)
        sg.send(message)
        return True
    except Exception as e:
        logger.error(f"Email send error: {e}")
        return False


def send_alert_email(user_email: str, org_name: str, opportunities: list) -> bool:
    if not opportunities:
        return False

    opp_html = ""
    for opp in opportunities[:5]:
        badge_color = {"high": "#dc2626", "medium": "#d97706", "low": "#059669"}.get(
            opp.get("severity", "medium"), "#d97706"
        )
        close_date = opp.get("close_date", "TBD")
        funding = f"${opp.get('funding_max', 0):,.0f}" if opp.get("funding_max") else "Varies"

        opp_html += f"""
        <div style="border:1px solid #e5e7eb;border-radius:8px;padding:16px;margin-bottom:12px;">
            <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:8px;">
                <strong style="font-size:15px;color:#111827;">{opp.get("title", "")[:80]}</strong>
                <span style="background:{badge_color};color:white;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:600;white-space:nowrap;margin-left:8px;">
                    {opp.get("severity", "medium").upper()}
                </span>
            </div>
            <p style="color:#6b7280;font-size:13px;margin:4px 0;">{opp.get("source", "")} &bull; {opp.get("agency", "")}</p>
            <p style="color:#374151;font-size:13px;margin:8px 0;">{opp.get("summary", "")}</p>
            <div style="display:flex;gap:16px;margin-top:8px;">
                <span style="font-size:12px;color:#6b7280;">Closes: <strong>{close_date}</strong></span>
                <span style="font-size:12px;color:#6b7280;">Funding: <strong>{funding}</strong></span>
            </div>
            <a href="{opp.get("url", "#")}" style="display:inline-block;margin-top:10px;background:#2563eb;color:white;padding:6px 14px;border-radius:6px;font-size:12px;text-decoration:none;">View Opportunity →</a>
        </div>"""

    html = f"""
    <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:600px;margin:0 auto;padding:20px;">
        <div style="background:#2563eb;color:white;padding:20px;border-radius:8px 8px 0 0;text-align:center;">
            <h1 style="margin:0;font-size:20px;">Grant & RFP Monitor</h1>
            <p style="margin:4px 0 0;opacity:0.85;font-size:14px;">New matching opportunities for {org_name}</p>
        </div>
        <div style="background:#f9fafb;padding:20px;border:1px solid #e5e7eb;border-top:none;">
            <p style="color:#374151;margin:0 0 16px;">We found <strong>{len(opportunities)} new opportunities</strong> matching your profile:</p>
            {opp_html}
            <div style="text-align:center;margin-top:20px;">
                <a href="{settings.frontend_url}/dashboard.html" style="background:#2563eb;color:white;padding:10px 24px;border-radius:6px;text-decoration:none;font-weight:600;">View All in Dashboard →</a>
            </div>
        </div>
        <p style="text-align:center;color:#9ca3af;font-size:11px;margin-top:16px;">
            Grant & RFP Monitor &bull; For informational purposes only — always verify directly with the source.
        </p>
    </div>"""

    return send_email(
        user_email,
        f"🔔 {len(opportunities)} new grant/RFP matches for {org_name}",
        html,
    )


def send_welcome_email(user_email: str, org_name: str, trial_days: int = 14) -> bool:
    html = f"""
    <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:600px;margin:0 auto;padding:20px;">
        <div style="background:#2563eb;color:white;padding:24px;border-radius:8px 8px 0 0;text-align:center;">
            <h1 style="margin:0;font-size:22px;">Welcome to Grant & RFP Monitor</h1>
        </div>
        <div style="background:#ffffff;padding:24px;border:1px solid #e5e7eb;border-top:none;">
            <p style="font-size:16px;color:#111827;">Hi {org_name},</p>
            <p style="color:#374151;">Your free {trial_days}-day trial is now active. Here's what happens next:</p>
            <ul style="color:#374151;line-height:1.8;">
                <li>We crawl <strong>grants.gov, SAM.gov, and state portals</strong> every 6 hours</li>
                <li>AI matches opportunities to your focus areas and sends you alerts</li>
                <li>You get a <strong>weekly digest</strong> every Monday with top matches</li>
                <li>Ask our AI advisor any grant or RFP question 24/7</li>
            </ul>
            <div style="text-align:center;margin:24px 0;">
                <a href="{settings.frontend_url}/dashboard.html" style="background:#2563eb;color:white;padding:12px 28px;border-radius:6px;text-decoration:none;font-weight:600;font-size:15px;">Go to Dashboard →</a>
            </div>
            <p style="color:#6b7280;font-size:13px;">Questions? Reply to this email — we're here to help.</p>
        </div>
    </div>"""

    return send_email(user_email, f"Welcome to Grant & RFP Monitor — trial started", html)
