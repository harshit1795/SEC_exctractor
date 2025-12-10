# Deployment Alternatives & Billing System Architecture

## 🚀 Part 1: Deployment Alternatives to Railway

### Option 1: Render (Recommended - Easy Migration) ⭐

**Why Render:**
- ✅ **IPv4 Support**: Full IPv4 support, no IPv6 issues
- ✅ **Free Tier**: 750 hours/month free
- ✅ **Easy Setup**: Similar to Railway, GitHub integration
- ✅ **PostgreSQL**: Built-in PostgreSQL option
- ✅ **Auto-deploy**: Automatic deployments from GitHub

**Setup Steps:**
1. Go to: https://render.com
2. Sign up with GitHub
3. **New** → **Web Service**
4. Connect your repository
5. **Settings:**
   - **Root Directory**: `finq-backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. **Environment Variables:**
   - `DATABASE_URL`: Your Supabase connection string
   - `GEMINI_API_KEY`: Your API key
   - `CORS_ORIGINS`: Your Vercel URLs
7. Deploy!

**Pricing:**
- **Free Tier**: $0/month (750 hours, sleeps after inactivity)
- **Starter**: $7/month (always on, no sleep)

### Option 2: Fly.io (Great for Global Scale)

**Why Fly.io:**
- ✅ **IPv4/IPv6**: Supports both
- ✅ **Global**: Deploy close to users
- ✅ **Free Tier**: 3 shared VMs free
- ✅ **PostgreSQL**: Built-in or external

**Setup:**
1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Login: `fly auth login`
3. Launch: `fly launch` (in `finq-backend/`)
4. Set secrets: `fly secrets set DATABASE_URL=... GEMINI_API_KEY=...`

**Pricing:**
- **Free**: 3 shared VMs, 3GB storage
- **Paid**: Pay-as-you-go, ~$1.94/month per VM

### Option 3: AWS (Most Scalable, More Complex)

**Why AWS:**
- ✅ **Enterprise-grade**: Most reliable
- ✅ **Full Control**: Complete infrastructure control
- ✅ **Billing Integration**: Native AWS billing APIs
- ✅ **Scalable**: Auto-scaling, load balancing

**Options:**
- **AWS Elastic Beanstalk**: Easiest (similar to Railway)
- **AWS App Runner**: Serverless containers
- **AWS ECS/Fargate**: Container orchestration
- **AWS Lambda**: Serverless functions

**Pricing:**
- **Free Tier**: 12 months free, then pay-as-you-go
- **Estimated**: $10-50/month for small app

### Option 4: Google Cloud Run (Serverless)

**Why Cloud Run:**
- ✅ **Serverless**: Pay only for requests
- ✅ **Auto-scaling**: Scales to zero
- ✅ **Easy**: Simple container deployment
- ✅ **IPv4**: Full IPv4 support

**Setup:**
1. Build container: `gcloud builds submit --tag gcr.io/PROJECT/finq-backend`
2. Deploy: `gcloud run deploy --image gcr.io/PROJECT/finq-backend`
3. Set env vars in Cloud Run console

**Pricing:**
- **Free Tier**: 2 million requests/month
- **Paid**: $0.40 per million requests

### Option 5: DigitalOcean App Platform

**Why DigitalOcean:**
- ✅ **Simple**: Easy deployment
- ✅ **PostgreSQL**: Built-in managed database
- ✅ **Predictable Pricing**: Fixed monthly costs
- ✅ **IPv4**: Full support

**Pricing:**
- **Basic**: $5/month (512MB RAM)
- **Professional**: $12/month (1GB RAM)

## 🎯 Recommendation: Render

**Best for your use case:**
- ✅ Easiest migration from Railway
- ✅ Free tier to start
- ✅ IPv4 support (fixes your issue)
- ✅ Similar workflow to Railway
- ✅ Good documentation

---

## 💰 Part 2: Billing & Usage Tracking Architecture

### Current State Analysis

**What you have:**
- ✅ User authentication (Firebase/JWT)
- ✅ User IDs tracked in `insights` table
- ✅ API calls logged in `insights` table
- ✅ Single Google API key (shared)

**What you need:**
- ❌ Per-user API usage tracking
- ❌ Cost calculation per request
- ❌ Billing integration
- ❌ Usage limits/quota management
- ❌ Transparent pricing for users

### Architecture Options

## Option A: Usage-Based Billing (Recommended) ⭐

**How it works:**
1. Track each API call with user_id
2. Calculate cost per request (tokens used)
3. Bill users monthly based on usage
4. Show usage dashboard to users

### Implementation Plan

#### Step 1: Create Usage Tracking Table

```python
# finq-backend/app/models/usage.py
class APIUsage(Base):
    __tablename__ = "api_usage"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    service = Column(String, nullable=False)  # 'gemini', 'fred', etc.
    endpoint = Column(String, nullable=False)  # '/chat/analyze'
    
    # Usage metrics
    tokens_used = Column(Integer, nullable=True)  # For Gemini
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    request_size = Column(Integer, nullable=True)  # Bytes
    
    # Cost calculation
    cost_usd = Column(Numeric(10, 6), nullable=False)  # Cost in USD
    pricing_tier = Column(String, nullable=True)  # 'free', 'pro', etc.
    
    # Metadata
    request_id = Column(String, nullable=True)  # For tracking
    session_id = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
```

#### Step 2: Track Usage in Chat Endpoint

```python
# finq-backend/app/api/chat.py
@router.post("/analyze")
async def analyze_financial_data(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),  # Get from auth
    db: Session = Depends(get_db)
):
    # ... existing code ...
    
    # Track usage BEFORE API call
    usage_record = APIUsage(
        user_id=current_user.id,
        service='gemini',
        endpoint='/chat/analyze',
        request_id=str(uuid.uuid4()),
        session_id=request.session_id,
    )
    db.add(usage_record)
    
    try:
        # Make API call
        response = await analyzer.analyze_financial_data(...)
        
        # Calculate tokens and cost
        if hasattr(response, 'usage_metadata'):
            usage_record.input_tokens = response.usage_metadata.prompt_token_count
            usage_record.output_tokens = response.usage_metadata.candidates_token_count
            usage_record.tokens_used = usage_record.input_tokens + usage_record.output_tokens
        
        # Calculate cost (Gemini pricing)
        cost = calculate_gemini_cost(
            input_tokens=usage_record.input_tokens or 0,
            output_tokens=usage_record.output_tokens or 0
        )
        usage_record.cost_usd = cost
        
        db.commit()
        
    except Exception as e:
        usage_record.cost_usd = 0  # Failed requests don't cost
        db.commit()
        raise
```

#### Step 3: Cost Calculation Function

```python
# finq-backend/app/services/billing.py
def calculate_gemini_cost(input_tokens: int, output_tokens: int) -> float:
    """
    Calculate cost based on Gemini Flash pricing
    Current pricing (as of 2024):
    - Input: $0.075 per 1M tokens
    - Output: $0.30 per 1M tokens
    """
    INPUT_COST_PER_MILLION = 0.075
    OUTPUT_COST_PER_MILLION = 0.30
    
    input_cost = (input_tokens / 1_000_000) * INPUT_COST_PER_MILLION
    output_cost = (output_tokens / 1_000_000) * OUTPUT_COST_PER_MILLION
    
    return input_cost + output_cost

def calculate_user_monthly_cost(user_id: str, db: Session) -> dict:
    """Calculate total cost for user this month"""
    from datetime import datetime
    from sqlalchemy import func
    
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0)
    
    total_cost = db.query(func.sum(APIUsage.cost_usd)).filter(
        APIUsage.user_id == user_id,
        APIUsage.created_at >= start_of_month
    ).scalar() or 0
    
    total_requests = db.query(func.count(APIUsage.id)).filter(
        APIUsage.user_id == user_id,
        APIUsage.created_at >= start_of_month
    ).scalar() or 0
    
    return {
        "total_cost_usd": float(total_cost),
        "total_requests": total_requests,
        "period": "current_month"
    }
```

#### Step 4: User Subscription/Billing Model

```python
# finq-backend/app/models/subscription.py
class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, unique=True, index=True)
    
    # Plan details
    plan_type = Column(String, nullable=False)  # 'free', 'pro', 'enterprise'
    monthly_limit_usd = Column(Numeric(10, 2), nullable=True)  # Spending limit
    request_limit = Column(Integer, nullable=True)  # Max requests/month
    
    # Billing
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    payment_method_id = Column(String, nullable=True)
    
    # Status
    status = Column(String, nullable=False)  # 'active', 'canceled', 'past_due'
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

#### Step 5: Usage Limits Middleware

```python
# finq-backend/app/middleware/usage_limits.py
async def check_usage_limits(
    user_id: str,
    db: Session,
    estimated_cost: float = 0.01  # Estimated cost for this request
) -> bool:
    """Check if user has exceeded usage limits"""
    from app.models.subscription import Subscription
    from app.services.billing import calculate_user_monthly_cost
    
    # Get user subscription
    subscription = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.status == 'active'
    ).first()
    
    if not subscription:
        # Free tier - check limits
        monthly_usage = calculate_user_monthly_cost(user_id, db)
        if monthly_usage['total_cost_usd'] + estimated_cost > 5.00:  # $5 free limit
            return False
        if monthly_usage['total_requests'] >= 100:  # 100 free requests
            return False
    else:
        # Paid tier - check subscription limits
        monthly_usage = calculate_user_monthly_cost(user_id, db)
        if subscription.monthly_limit_usd:
            if monthly_usage['total_cost_usd'] + estimated_cost > subscription.monthly_limit_usd:
                return False
        if subscription.request_limit:
            if monthly_usage['total_requests'] >= subscription.request_limit:
                return False
    
    return True
```

## Option B: Per-User API Keys (Advanced)

**How it works:**
1. Users provide their own Google API keys
2. You proxy requests through their keys
3. Charge a platform fee (e.g., 20% markup)
4. No direct API costs for you

**Pros:**
- ✅ No API costs for you
- ✅ Users control their own quota
- ✅ Transparent pricing

**Cons:**
- ❌ More complex setup
- ❌ Users need Google Cloud accounts
- ❌ Harder to manage

### Implementation:

```python
# finq-backend/app/models/user_api_key.py
class UserAPIKey(Base):
    __tablename__ = "user_api_keys"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, unique=True, index=True)
    gemini_api_key = Column(String, nullable=True)  # Encrypted
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
```

## Option C: Hybrid Approach (Best of Both) ⭐⭐⭐

**How it works:**
1. **Free Tier**: Shared API key, limited usage
2. **Pro Tier**: Users can bring their own key OR pay usage-based
3. **Enterprise**: Dedicated resources

**Implementation:**
- Free users: Use shared key, 100 requests/month
- Pro users: Option to use own key (no per-request cost) OR pay usage-based
- Enterprise: Dedicated API keys, custom limits

---

## 💳 Part 3: Billing Integration (Stripe)

### Step 1: Install Stripe

```bash
pip install stripe
```

### Step 2: Stripe Integration

```python
# finq-backend/app/services/stripe_service.py
import stripe
from app.config import settings

stripe.api_key = settings.stripe_secret_key

def create_customer(user_id: str, email: str) -> str:
    """Create Stripe customer"""
    customer = stripe.Customer.create(
        email=email,
        metadata={'user_id': user_id}
    )
    return customer.id

def create_subscription(customer_id: str, price_id: str) -> str:
    """Create subscription"""
    subscription = stripe.Subscription.create(
        customer=customer_id,
        items=[{'price': price_id}],
    )
    return subscription.id

def create_usage_based_invoice(
    customer_id: str,
    usage_amount: float,
    description: str
) -> str:
    """Create invoice for usage-based billing"""
    invoice_item = stripe.InvoiceItem.create(
        customer=customer_id,
        amount=int(usage_amount * 100),  # Convert to cents
        currency='usd',
        description=description,
    )
    
    invoice = stripe.Invoice.create(
        customer=customer_id,
        auto_advance=True,
    )
    invoice.finalize_invoice()
    
    return invoice.id
```

### Step 3: Webhook Handler

```python
# finq-backend/app/api/billing.py
@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhooks"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle events
    if event['type'] == 'invoice.payment_succeeded':
        # Update subscription status
        pass
    elif event['type'] == 'customer.subscription.deleted':
        # Cancel subscription
        pass
    
    return {"status": "success"}
```

---

## 📊 Part 4: Usage Dashboard for Users

### Frontend Component

```typescript
// finq-frontend/components/billing/UsageDashboard.tsx
export function UsageDashboard() {
  const { user } = useAuth();
  const { data: usage } = useQuery({
    queryKey: ['usage', user?.uid],
    queryFn: () => api.getUsageStats(user?.uid),
  });
  
  return (
    <Card>
      <h2>Usage & Billing</h2>
      <div>
        <p>This Month:</p>
        <p>Requests: {usage?.total_requests || 0}</p>
        <p>Cost: ${usage?.total_cost_usd?.toFixed(4) || '0.0000'}</p>
        <p>Remaining: ${usage?.remaining_limit || '0.00'}</p>
      </div>
      <UsageChart data={usage?.daily_breakdown} />
    </Card>
  );
}
```

---

## 🎯 Recommended Architecture

### Phase 1: Basic Usage Tracking (Week 1)
1. ✅ Create `api_usage` table
2. ✅ Track all Gemini API calls
3. ✅ Calculate costs
4. ✅ Show usage dashboard

### Phase 2: Billing Integration (Week 2)
1. ✅ Integrate Stripe
2. ✅ Create subscription plans
3. ✅ Usage-based invoicing
4. ✅ Payment handling

### Phase 3: Advanced Features (Week 3-4)
1. ✅ Per-user API keys option
2. ✅ Usage alerts
3. ✅ Cost optimization tips
4. ✅ Enterprise features

---

## 💡 Pricing Strategy

### Suggested Plans:

**Free Tier:**
- 100 requests/month
- $5 credit/month
- Basic features

**Pro Tier ($29/month):**
- 1,000 requests/month
- $50 credit/month
- Advanced features
- Priority support

**Enterprise (Custom):**
- Unlimited requests
- Custom limits
- Dedicated support
- SLA

### Usage-Based Pricing:
- **Pay-as-you-go**: $0.01 per request (minimum $10/month)
- **Volume discounts**: 10% off for 10K+ requests/month

---

## 🚀 Quick Start: Render Deployment

1. **Sign up**: https://render.com
2. **New Web Service** → Connect GitHub
3. **Settings:**
   - Root: `finq-backend`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables:**
   - `DATABASE_URL`: Your Supabase string
   - `GEMINI_API_KEY`: Your key
   - `CORS_ORIGINS`: Vercel URLs
5. **Deploy!**

This should fix your IPv6 issue immediately!

---

Would you like me to:
1. Create the usage tracking models and migrations?
2. Implement the billing service?
3. Set up the Stripe integration?
4. Create the usage dashboard component?

Let me know which parts you'd like me to implement first!


