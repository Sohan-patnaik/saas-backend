from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# Mock / Sandbox storage for MVP billing simulation if keys are not set
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

try:
    import stripe
    if STRIPE_SECRET_KEY:
        stripe.api_key = STRIPE_SECRET_KEY
except ImportError:
    stripe = None

class CheckoutRequest(BaseModel):
    plan: str # 'starter', 'growth', 'agency'
    user_id: str = "default_user"

# In-memory subscription state for MVP demo
MOCK_USER_SUBSCRIPTION = {
    "user_id": "default_user",
    "tier": "Free Plan",
    "status": "active",
    "messages_used": 14,
    "messages_limit": 50,
    "can_whitelabel": False
}

PLAN_DETAILS = {
    "starter": {"name": "Starter Plan", "limit": 1000, "price": "$19/mo", "whitelabel": False},
    "growth": {"name": "Growth Pro", "limit": 5000, "price": "$49/mo", "whitelabel": True},
    "agency": {"name": "Agency Enterprise", "limit": 25000, "price": "$199/mo", "whitelabel": True}
}

@router.get("/status")
def get_billing_status(user_id: str = "default_user"):
    return MOCK_USER_SUBSCRIPTION

@router.post("/create-checkout-session")
def create_checkout_session(req: CheckoutRequest):
    plan_info = PLAN_DETAILS.get(req.plan.lower())
    if not plan_info:
        raise HTTPException(status_code=400, detail="Invalid plan selected")

    # If Stripe is configured and real secret key exists, create actual Stripe session
    if stripe and STRIPE_SECRET_KEY and not STRIPE_SECRET_KEY.startswith("sk_test_placeholder"):
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': plan_info['name']},
                        'unit_amount': int(plan_info['price'].replace('$', '').replace('/mo', '')) * 100,
                        'recurring': {'interval': 'month'},
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url='http://localhost:3000/dashboard?billing=success',
                cancel_url='http://localhost:3000/dashboard?billing=cancel',
            )
            return {"checkout_url": session.url, "mode": "stripe"}
        except Exception as e:
            print("Stripe session creation error:", e)

    # Fallback / MVP Simulation Mode for recruiter demos without live cards
    MOCK_USER_SUBSCRIPTION["tier"] = plan_info["name"]
    MOCK_USER_SUBSCRIPTION["messages_limit"] = plan_info["limit"]
    MOCK_USER_SUBSCRIPTION["can_whitelabel"] = plan_info["whitelabel"]

    return {
        "message": f"Successfully upgraded to {plan_info['name']} (MVP Sandbox Mode)",
        "mode": "sandbox",
        "subscription": MOCK_USER_SUBSCRIPTION
    }

@router.post("/webhook")
def stripe_webhook():
    return {"status": "success"}
