import stripe
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models.database import get_db
from models.models import User, PlanType
from routers.auth import get_current_user
from config import get_settings

router = APIRouter(prefix="/billing", tags=["billing"])
settings = get_settings()

PLAN_PRICE_MAP = {
    "starter": settings.stripe_starter_price_id,
    "pro": settings.stripe_pro_price_id,
    "enterprise": settings.stripe_enterprise_price_id,
}

PLAN_NAMES = {
    "starter": PlanType.starter,
    "pro": PlanType.pro,
    "enterprise": PlanType.enterprise,
}


class CheckoutRequest(BaseModel):
    plan: str


@router.post("/checkout")
def create_checkout(req: CheckoutRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Billing not configured")

    stripe.api_key = settings.stripe_secret_key
    price_id = PLAN_PRICE_MAP.get(req.plan)
    if not price_id:
        raise HTTPException(status_code=400, detail="Invalid plan")

    customer_id = current_user.stripe_customer_id
    if not customer_id:
        customer = stripe.Customer.create(email=current_user.email, name=current_user.organization_name)
        customer_id = customer.id
        current_user.stripe_customer_id = customer_id
        db.commit()

    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        success_url=f"{settings.frontend_url}/dashboard.html?upgraded=1",
        cancel_url=f"{settings.frontend_url}/pricing.html",
        metadata={"user_id": str(current_user.id), "plan": req.plan},
    )
    return {"checkout_url": session.url}


@router.post("/portal")
def customer_portal(current_user: User = Depends(get_current_user)):
    if not settings.stripe_secret_key or not current_user.stripe_customer_id:
        raise HTTPException(status_code=503, detail="Billing not configured")

    stripe.api_key = settings.stripe_secret_key
    session = stripe.billing_portal.Session.create(
        customer=current_user.stripe_customer_id,
        return_url=f"{settings.frontend_url}/dashboard.html",
    )
    return {"portal_url": session.url}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=503, detail="Webhook not configured")

    stripe.api_key = settings.stripe_secret_key
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig, settings.stripe_webhook_secret)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("metadata", {}).get("user_id")
        plan_name = session.get("metadata", {}).get("plan")
        if user_id and plan_name:
            user = db.query(User).filter_by(id=int(user_id)).first()
            if user:
                user.plan = PLAN_NAMES.get(plan_name, PlanType.starter)
                user.stripe_subscription_id = session.get("subscription")
                db.commit()

    elif event["type"] == "customer.subscription.deleted":
        sub = event["data"]["object"]
        user = db.query(User).filter_by(stripe_subscription_id=sub["id"]).first()
        if user:
            user.plan = PlanType.starter
            db.commit()

    return {"ok": True}
