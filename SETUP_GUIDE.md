# 🚀 Complete Setup Guide - Facebook Marketplace Bot SaaS

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Cheapest Deployment Option](#cheapest-deployment-option)
3. [Step-by-Step Setup](#step-by-step-setup)
4. [Chrome Extension Setup](#chrome-extension-setup)
5. [Testing](#testing)
6. [Going Live](#going-live)
7. [Cost Breakdown](#cost-breakdown)

---

## Prerequisites

Before you start, you'll need:
- [ ] A computer with Python 3.11+ installed
- [ ] Chrome browser
- [ ] Credit card (for Stripe and hosting - but most are FREE tier)
- [ ] Basic command line knowledge

---

## 🎯 Cheapest Deployment Option (RECOMMENDED)

### Total Cost: **£0-5/month** for first 100 users!

We'll use:
1. **Railway.app** - FREE tier (500 hours/month, plenty for starting)
2. **Stripe** - FREE (only pay 2.9% + 20p per transaction)
3. **PostgreSQL** - FREE on Railway
4. **Redis** - FREE on Railway
5. **Cloudinary** - FREE tier (25GB storage, 25GB bandwidth)

**Alternative (if Railway credits run out):**
- **Render.com** - FREE tier with 750 hours/month

---

## Step-by-Step Setup

### 1️⃣ Create Stripe Account (FREE - 10 minutes)

1. Go to https://stripe.com and sign up
2. Complete business verification
3. Go to **Developers → API keys**
4. Copy:
   - `Publishable key` (starts with `pk_test_`)
   - `Secret key` (starts with `sk_test_`)
5. Go to **Developers → Webhooks**
6. Click **Add endpoint**
7. Enter URL: `https://your-app-url.railway.app/api/subscription/webhook` (you'll get this later)
8. Select events: `customer.subscription.*`, `invoice.payment_*`
9. Copy the `Signing secret` (starts with `whsec_`)

**Cost:** FREE (2.9% + 20p per transaction)

---

### 2️⃣ Deploy to Railway (FREE - 15 minutes)

1. Go to https://railway.app and sign up with GitHub
2. Click **New Project** → **Deploy from GitHub repo**
3. Connect your GitHub account and select your bot repository
4. Railway will auto-detect the `railway.toml` file

**Add Database:**
1. Click **New** → **Database** → **Add PostgreSQL**
2. Railway automatically creates `DATABASE_URL` environment variable

**Add Redis:**
1. Click **New** → **Database** → **Add Redis**
2. Railway automatically creates `REDIS_URL` environment variable

**Add Environment Variables:**
1. Click on your service → **Variables** tab
2. Add these variables:

```bash
# Required
JWT_SECRET_KEY=<generate-with-command-below>
ENCRYPTION_KEY=<generate-with-command-below>
STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET_HERE

# Optional (but recommended)
OPENAI_API_KEY=sk-YOUR_KEY_HERE
FRONTEND_URL=https://your-domain.com
```

**Generate Secret Keys:**
```bash
# JWT Secret
python -c "import secrets; print(secrets.token_hex(32))"

# Encryption Key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

3. Click **Deploy** - Railway will build and deploy automatically!
4. Once deployed, click **Settings** → **Networking** → **Generate Domain**
5. Copy your URL (e.g., `https://your-app-name.up.railway.app`)

**Update Stripe Webhook:**
- Go back to Stripe Dashboard → Webhooks
- Update endpoint URL to: `https://your-app-name.up.railway.app/api/subscription/webhook`

**Cost:** FREE for first 500 hours/month ($5/month after)

---

### 3️⃣ Create Stripe Products (5 minutes)

Run this Python script to create subscription tiers in Stripe:

```bash
# Install Stripe SDK
pip install stripe

# Set your Stripe secret key
export STRIPE_SECRET_KEY=sk_test_YOUR_KEY

# Run the setup script
python stripe_integration.py
```

This will create 3 products:
- Basic (£15/month)
- Pro (£30/month)
- Premium (£50/month)

Copy the `price_id` values printed to console and update `config/subscription_tiers.py`:

```python
SUBSCRIPTION_TIERS = {
    'basic': {
        ...
        'stripe_price_id': 'price_XXXXX',  # Paste here
    },
    'pro': {
        ...
        'stripe_price_id': 'price_YYYYY',  # Paste here
    },
    'premium': {
        ...
        'stripe_price_id': 'price_ZZZZZ',  # Paste here
    }
}
```

Commit and push changes to GitHub - Railway will auto-deploy.

---

### 4️⃣ Setup Cloudinary for Images (FREE - 5 minutes)

1. Go to https://cloudinary.com and sign up
2. Go to **Dashboard**
3. Copy your **Cloud name**, **API Key**, and **API Secret**
4. Add to Railway environment variables:

```bash
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

**Cost:** FREE (25GB storage, 25GB bandwidth/month)

---

### 5️⃣ Setup OpenAI (Optional - for Premium tier)

1. Go to https://platform.openai.com/api-keys
2. Create new API key
3. Add to Railway environment variables:

```bash
OPENAI_API_KEY=sk-YOUR_KEY
```

**Cost:** ~£0.002 per AI title generation (Premium feature)

---

## Chrome Extension Setup

### 1️⃣ Load Extension Locally (for testing)

1. Open Chrome → `chrome://extensions/`
2. Enable **Developer mode** (top right)
3. Click **Load unpacked**
4. Select the `chrome-extension` folder
5. Extension icon will appear in toolbar

### 2️⃣ Update API URL

Edit `chrome-extension/popup/popup.js` and `chrome-extension/background/service-worker.js`:

```javascript
// Change this:
const API_URL = 'http://localhost:5000/api';

// To this:
const API_URL = 'https://your-app-name.up.railway.app/api';
```

### 3️⃣ Test Extension

1. Click extension icon
2. Click **Register** and create an account
3. Login to Facebook in another tab
4. In extension, click **Add Account**
5. Click **Auto-Detect Cookies**
6. Create a test listing!

---

### 4️⃣ Publish to Chrome Web Store (Optional - £4 one-time fee)

1. Create developer account: https://chrome.google.com/webstore/devconsole
2. Pay one-time £4 registration fee
3. Zip your `chrome-extension` folder
4. Upload to Web Store
5. Fill in:
   - Description (use text from `landing-page/index.html`)
   - Screenshots (take from your extension)
   - Privacy policy (use template below)
6. Submit for review (1-3 days approval)

**Cost:** £4 one-time fee

---

## Testing

### Test Registration & Login
```bash
# Register a user
curl -X POST https://your-app.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password123"}'

# Login
curl -X POST https://your-app.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password123"}'
```

### Test Subscription Webhook

1. Go to Stripe Dashboard → Webhooks → Your webhook
2. Click **Send test webhook**
3. Select `customer.subscription.created`
4. Check Railway logs to see if it processed

---

## Going Live

### 1️⃣ Switch Stripe to Live Mode

1. Stripe Dashboard → Toggle to **Live mode**
2. Get new API keys from **Developers → API keys**
3. Update Railway environment variables:
   - `STRIPE_SECRET_KEY=sk_live_...`
   - `STRIPE_PUBLISHABLE_KEY=pk_live_...`
4. Update webhook secret

### 2️⃣ Deploy Landing Page

**Option A: Railway (FREE)**
1. Create new Railway service
2. Connect GitHub repo
3. Select `landing-page` folder
4. Deploy!

**Option B: Netlify (FREE)**
1. Go to https://netlify.com
2. Drag & drop `landing-page` folder
3. FREE custom domain + SSL

**Option C: GitHub Pages (FREE)**
```bash
# Push landing-page to gh-pages branch
cd landing-page
git init
git add .
git commit -m "Landing page"
git push origin gh-pages
```
Access at: `https://your-username.github.io/repo-name`

### 3️⃣ Setup Custom Domain (Optional - £10/year)

1. Buy domain from Namecheap (£10/year) or Google Domains
2. In Railway → Settings → Domains → Add custom domain
3. Update DNS records as shown
4. SSL auto-configured!

---

## 💰 Cost Breakdown

### Minimum (FREE Plan)
- **Railway:** FREE (500 hours/month)
- **Stripe:** FREE (2.9% + 20p per transaction)
- **Cloudinary:** FREE (25GB)
- **OpenAI:** Pay-as-you-go (~£0.002 per AI generation)
- **Domain:** Optional (£10/year)
- **Chrome Web Store:** Optional (£4 one-time)

**Total:** £0/month (+ transaction fees)

---

### After FREE Tier (100+ users)

**Railway Pro ($20/month = ~£16/month):**
- 100GB egress
- Unlimited services
- 8GB RAM
- 8vCPU

**Stripe:** Still FREE (just transaction fees)

**Total:** ~£16/month + transaction fees

---

### Scaling to 1000 Users

**Railway:** ~£40/month (multiple services)
**PostgreSQL:** Use Railway's built-in (included)
**Redis:** Use Railway's built-in (included)
**Cloudinary:** ~£25/month (Advanced plan)

**Total:** ~£65/month

---

## 🎯 Revenue Projection

With your pricing:
- **20 Basic users** (£15 × 20) = £300/month
- **10 Pro users** (£30 × 10) = £300/month
- **5 Premium users** (£50 × 5) = £250/month

**Total Revenue:** £850/month
**Costs:** £65/month
**Profit:** £785/month

---

## 🛠️ Troubleshooting

### "Database connection failed"
- Check `DATABASE_URL` is set in Railway
- Ensure PostgreSQL service is running

### "Stripe webhook not working"
- Verify webhook URL is correct
- Check `STRIPE_WEBHOOK_SECRET` is set
- Check Railway logs for errors

### "Extension can't connect to API"
- Update `API_URL` in popup.js and service-worker.js
- Check CORS is enabled in `app_cloud.py`

### "Bot not creating listings"
- Check Celery worker is running (Railway should auto-start)
- Check Redis is running
- Verify cookies are valid

---

## 📚 Next Steps

1. **Set up monitoring:** Add Sentry for error tracking (FREE tier)
2. **Email notifications:** Set up SendGrid (FREE tier: 100 emails/day)
3. **Analytics:** Add Google Analytics to landing page
4. **Support:** Set up Crisp chat widget (FREE tier)
5. **Documentation:** Create help docs at your-domain.com/docs

---

## 🚨 IMPORTANT SECURITY NOTES

1. **Never commit `.env` file** - Add to `.gitignore`
2. **Use strong JWT secret** - Generate with command above
3. **Rotate API keys** every 6 months
4. **Enable 2FA** on Stripe, Railway, GitHub
5. **Monitor logs** for suspicious activity
6. **Backup database** weekly (Railway auto-backups)

---

## 📞 Support

If you get stuck:
1. Check Railway logs: Dashboard → Service → Logs
2. Check Stripe webhooks: Dashboard → Webhooks → Event details
3. Test API endpoints with `curl` commands above
4. Review this guide section by section

---

## ✅ Launch Checklist

- [ ] Railway deployed successfully
- [ ] PostgreSQL + Redis connected
- [ ] Stripe products created
- [ ] Environment variables set
- [ ] Webhook working (test event sent)
- [ ] Extension installed and working
- [ ] Test account created
- [ ] Test listing created successfully
- [ ] Landing page deployed
- [ ] Domain connected (optional)
- [ ] Analytics setup
- [ ] Privacy policy added
- [ ] Terms of service added

---

**You're ready to launch! 🚀**

Cost to get started: **£0** (using free tiers)
Time to launch: **~2 hours**
Revenue potential: **£850+/month** (with just 35 users)

Good luck with your SaaS business!
