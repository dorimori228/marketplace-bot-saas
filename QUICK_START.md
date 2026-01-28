# ⚡ Quick Start - Deploy in 30 Minutes

## Prerequisites
- GitHub account
- Credit card (for Stripe - FREE to start)

---

## Step 1: Push to GitHub (5 min)

```bash
cd "c:\Users\adamm\Documents\localhost FB BOT tester\facebook-marketplace-bot"

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Facebook Marketplace Bot SaaS"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git push -u origin main
```

---

## Step 2: Stripe Setup (5 min)

1. Create account: https://stripe.com
2. Get test keys: Dashboard → Developers → API keys
   - Copy `sk_test_...`
   - Copy `pk_test_...`
3. Create webhook: Dashboard → Developers → Webhooks
   - URL: `https://YOUR-APP.railway.app/api/subscription/webhook` (update later)
   - Events: `customer.subscription.*`, `invoice.*`
   - Copy `whsec_...`

---

## Step 3: Deploy to Railway (10 min)

1. Sign up: https://railway.app (use GitHub)
2. Click **New Project** → **Deploy from GitHub**
3. Select your repository
4. Add **PostgreSQL** (New → Database → PostgreSQL)
5. Add **Redis** (New → Database → Redis)
6. Add environment variables:

```bash
# Required (click Variables tab):
JWT_SECRET_KEY=<run-command-below>
ENCRYPTION_KEY=<run-command-below>
STRIPE_SECRET_KEY=sk_test_YOUR_KEY
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY
STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET
```

**Generate secrets:**
```bash
# JWT Secret
python -c "import secrets; print(secrets.token_hex(32))"

# Encryption Key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

7. Click **Deploy**
8. Settings → Networking → **Generate Domain**
9. Copy your URL: `https://YOUR-APP.up.railway.app`

---

## Step 4: Create Stripe Products (3 min)

```bash
# Install Stripe
pip install stripe

# Set key
set STRIPE_SECRET_KEY=sk_test_YOUR_KEY

# Run script
python stripe_integration.py
```

Copy the 3 `price_id` values and update `config/subscription_tiers.py`:

```python
'basic': {'stripe_price_id': 'price_XXXXX'},
'pro': {'stripe_price_id': 'price_YYYYY'},
'premium': {'stripe_price_id': 'price_ZZZZZ'}
```

Commit and push:
```bash
git add config/subscription_tiers.py
git commit -m "Update Stripe price IDs"
git push
```

---

## Step 5: Update Extension (2 min)

Edit these 2 files:

**chrome-extension/popup/popup.js** (line 7):
```javascript
const API_URL = 'https://YOUR-APP.up.railway.app/api';
```

**chrome-extension/background/service-worker.js** (line 56):
```javascript
const API_URL = 'https://YOUR-APP.up.railway.app/api';
```

---

## Step 6: Load Extension (2 min)

1. Chrome → `chrome://extensions/`
2. Enable **Developer mode**
3. **Load unpacked** → Select `chrome-extension` folder
4. Done!

---

## Step 7: Test (3 min)

1. Click extension icon
2. Register account
3. Login to Facebook (different tab)
4. Extension → **Add Account** → **Auto-Detect Cookies**
5. Create test listing!

---

## ✅ You're Live!

**Deployed in:** ~30 minutes
**Cost:** £0/month (FREE tier)

---

## What's Next?

1. **Go Live:**
   - Switch Stripe to live mode
   - Update API keys
   - Publish extension to Chrome Web Store (£4)

2. **Get Customers:**
   - Deploy landing page
   - Post in Facebook selling groups
   - Share with friends

3. **Make Money:**
   - £15/month × 20 users = £300/month
   - £30/month × 10 users = £300/month
   - £50/month × 5 users = £250/month
   - **Total: £850/month profit!**

---

## Troubleshooting

**"Can't connect to API"**
- Update API_URL in extension files
- Check Railway deployment succeeded

**"Stripe webhook not working"**
- Update webhook URL in Stripe dashboard
- Add `/api/subscription/webhook` to end

**"Database error"**
- Ensure PostgreSQL is added in Railway
- Check DATABASE_URL is set

---

## Full Documentation

- **Complete guide:** See `SETUP_GUIDE.md`
- **Implementation details:** See `IMPLEMENTATION_COMPLETE.md`

---

**Need help?** Read the full guides above!
