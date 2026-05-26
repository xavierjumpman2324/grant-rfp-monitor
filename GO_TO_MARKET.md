# Grant & RFP Monitor — 10-Day First Customer Playbook

---

# PAGE 1: THE MISSION

## Your Goal
Get 1 paying customer within 10 days of reading this document.

Not 10 customers. Not $10K MRR. One customer.

One customer proves the concept, gives you a testimonial, tells you what to improve,
and gives you confidence to get the next 10. Everything starts with one.

## What You're Selling
A service that saves organizations time and money by automatically finding grants
and RFPs that match their mission — so they never miss a funding opportunity again.

**The one-line pitch:**
"We watch every grant and RFP posted by the federal government and your state,
24/7, and alert you the moment something matches your organization — so you never
miss a deadline again."

## The Price
- Start conversations offering a FREE 14-day trial (no credit card)
- After trial: $299/month (Starter plan)
- Don't negotiate below $299. The value is there.

---

# PAGE 2: BEFORE YOU MAKE ONE CALL

## Step 1 — Deploy the App (Day 1)

You cannot sell something that isn't live. Do this first.

1. Go to railway.app → sign up with GitHub
2. Click "New Project" → "Deploy from GitHub repo" → select grant-rfp-monitor
3. Set root directory to: backend
4. Add environment variables:
   - SECRET_KEY = (any random 32-character string)
   - ANTHROPIC_API_KEY = (get from console.anthropic.com)
5. Add PostgreSQL: click "New" → "Database" → "PostgreSQL" (Railway auto-sets DATABASE_URL)
6. Set start command: uvicorn main:app --host 0.0.0.0 --port $PORT
7. Railway gives you a URL like: grant-rfp-monitor-production.up.railway.app
8. That's your live product. Test it — register an account, browse opportunities.

**Cost: ~$5/month on Railway. Get Anthropic API key free tier to start.**

## Step 2 — Get a Domain (Day 1)

Go to Namecheap.com. Search for one of these:
- grantmonitor.ai (~$15/yr)
- rfpmonitor.io (~$12/yr)
- grantwatch.ai (~$15/yr)
- fundingalert.io (~$12/yr)

Buy it. Point it to your Railway URL (Railway has a custom domain option — paste your domain in).

Now you have: yoursite.com instead of a railway URL. This matters for credibility.

## Step 3 — Set Up a Professional Email (Day 1)

Go to Google Workspace ($6/month) or Zoho Mail (free).
Create: xavier@yourdomainname.com

Do NOT reach out from a Gmail. It kills credibility immediately.

## Step 4 — SendGrid for Email Alerts (Day 1)

1. Go to sendgrid.com → sign up free (100 emails/day free)
2. Get your API key
3. Add SENDGRID_API_KEY and SENDGRID_FROM_EMAIL to Railway env vars
4. Now the app sends real email alerts automatically

---

# PAGE 3: WHO TO TARGET FIRST

## Your Ideal First Customer Profile

**DO target:**
- Nonprofits with 5–50 employees (big enough to have budget, small enough to not have a grants team)
- Government contractors doing under $10M/year in federal contracts
- Grant consultants who manage 3–10 nonprofit clients
- Community health centers
- Workforce development organizations
- Housing nonprofits
- Education nonprofits

**DO NOT target (yet):**
- Solo 1-person nonprofits (no budget)
- Large hospitals or universities (too slow to decide, need procurement)
- Government agencies (bureaucratic, 6-month sales cycles)

## Where to Find Them — Free Methods

### Method 1: IRS Tax-Exempt Organization Search
Go to: apps.irs.gov/app/eos
Search by city and state. Every 501(c)(3) is listed with their address and EIN.
Filter by: City = [your city], State = [your state]
This gives you hundreds of local nonprofits to contact.

### Method 2: GuideStar / Candid
Go to: candid.org
Free search shows nonprofit names, locations, mission, revenue size.
Filter for organizations with $500K–$5M annual revenue (they have budget).

### Method 3: SAM.gov Contractor Search
Go to: sam.gov/search → Entity search → filter by state
These are registered government contractors — they LIVE off RFPs.
Every entity listed needs what you're selling.

### Method 4: LinkedIn
Search: "grants manager" OR "development director" OR "grants coordinator"
Filter by: Location = [your city]
These are the exact decision makers. Connect + message directly.

### Method 5: Local Business Journals
Search "[your city] nonprofit" or "[your city] government contractor"
Local business journals publish lists of top nonprofits every year.
Google: "largest nonprofits in [your city] 2024"

---

# PAGE 4: THE OUTREACH SYSTEM

## The 3-Touch Sequence (Do This for Every Prospect)

**Touch 1 — LinkedIn Connection Request (Day 1 of outreach):**
"Hi [Name], I built a tool that automatically monitors grants.gov and SAM.gov
and alerts organizations like [Org Name] when new funding matches their mission.
Wanted to connect."

(No pitch yet. Just connect.)

**Touch 2 — LinkedIn Message (2 days after connecting):**
"Hey [Name] — thanks for connecting. Quick question: does [Org Name] have a
system that automatically monitors for new grants and federal RFPs, or is
that more of a manual process right now?

I built something that does it automatically and wanted to see if it's
relevant for you."

(This is a question, not a pitch. Questions get replies. Pitches get ignored.)

**Touch 3 — Follow-up or Email (3 days later if no reply):**
"Hi [Name],

I sent a note on LinkedIn — just wanted to follow up here in case this is
a better channel.

I built Grant & RFP Monitor (yourdomainname.com) — it watches grants.gov,
SAM.gov, and state portals 24/7 and emails you the moment a new opportunity
matches your organization. AI reads every listing and tells you exactly
what it means for you and what to do next.

Free 14-day trial, no credit card. Takes 2 minutes to set up.

Would it be worth a quick look? Happy to walk you through it on a 15-minute call."

---

## Cold Email Template (For Direct Outreach)

**Subject:** New [your state] grants for [Org Name]?

Hi [First Name],

Quick question — does [Org Name] have a way to automatically track new
federal and state grants as they're posted, or is someone manually checking
grants.gov?

I ask because I built a tool (yourdomainname.com) that monitors 40+ funding
sources 24/7 and sends instant alerts when something matches your
organization's focus areas.

Most development teams I talk to are either checking manually (time-consuming)
or missing opportunities entirely (expensive).

Free 14-day trial — no credit card, 2 minutes to set up.

Worth a look?

[Your Name]
[yourdomainname.com]
[Phone]

---

## Cold Call Script (When You Have a Phone Number)

**Gatekeeper:**
"Hi — could I speak with whoever manages grants or development? It's
regarding new federal funding opportunities for [Org Name]."

**Decision Maker Opening:**
"Hi [Name], I'll be quick — I built a tool that automatically monitors
grants.gov and SAM.gov and alerts your team the moment new funding matches
[Org Name]. Do you have 60 seconds?"

*(If yes)*

"Most organizations I talk to are either manually checking grant sites —
which takes hours — or missing opportunities entirely. We automate the
whole monitoring piece. AI reads every new grant, scores it for your
specific mission, and emails your team instantly.

Free 14-day trial. Would it be worth seeing?"

**If they say yes:** "Perfect — what's your email? I'll send you the link
right now and you can be set up in 2 minutes."

**If they say send info first:** "Absolutely — best email? And just so I
send it to the right person — are you the one who'd make a call on something
like this or would someone else need to be involved?"

**If they say not interested:** "Totally fair. Can I ask — is it more that
you already have a system in place, or just not the right timing?"

---

# PAGE 5: YOUR DAY-BY-DAY 10-DAY PLAN

## Day 1 — Infrastructure
- [ ] Deploy app to Railway (follow Page 2 steps)
- [ ] Buy a domain on Namecheap
- [ ] Set up professional email (Google Workspace or Zoho)
- [ ] Get Anthropic API key and add to Railway
- [ ] Get SendGrid API key and add to Railway
- [ ] Test the live app end to end — register, browse, chat
- [ ] Register YOUR account on the live app

## Day 2 — Build Your Prospect List
- [ ] Find 50 prospects using IRS search, GuideStar, and LinkedIn
- [ ] For each: Organization name, contact name, email or phone, LinkedIn URL
- [ ] Put them in a Google Sheet with columns:
  Name | Org | Email | Phone | LinkedIn | Touch1 | Touch2 | Touch3 | Status

Target breakdown:
- 20 nonprofits (development directors, grants managers)
- 20 government contractors (operations managers, BD directors)
- 10 grant consultants

## Day 3 — First Wave Outreach
- [ ] Send LinkedIn connection requests to all 50 prospects
- [ ] Send cold emails to anyone whose email you found (aim for 20)
- [ ] Post on your personal LinkedIn:

"I just launched a tool that monitors grants.gov and SAM.gov 24/7 and
alerts nonprofits and contractors when new funding matches their mission.
AI reads every listing and tells you exactly what it means for your org.

Free 14-day trial: [yourdomainname.com]

If you work in grants, nonprofit development, or federal contracting —
or know someone who does — I'd love for you to check it out."

## Day 4 — Follow Up + Second Wave
- [ ] Send Touch 2 messages to everyone who connected on LinkedIn
- [ ] Find 25 more prospects and send connection requests
- [ ] Post in 2 Facebook groups:
  Search: "nonprofit professionals [your city]" or "grants managers network"
  Post: Same message as LinkedIn, adjusted for the group

## Day 5 — Calls + Demos
- [ ] Call anyone who replied but hasn't signed up yet
- [ ] Offer a 15-minute Zoom demo to anyone on the fence
- [ ] For demos: screen share your live dashboard, show them:
  1. How the alerts work
  2. A real grant that matches their mission
  3. The AI advisor answering a question about it
  4. How to save and track an application

## Day 6 — Warm Network
- [ ] Text or email 10 people you personally know who work at nonprofits
  or know people who do. Ask them to forward your info to the right person.
  Message: "Hey — I launched something that could help nonprofits find grants
  automatically. Do you know anyone in development or grants I should talk to?"
- [ ] Post in local Facebook community groups and NextDoor if relevant

## Day 7 — Reddit + Online Communities
Post in these subreddits (read rules first, be genuine not spammy):
- r/nonprofit
- r/grantwriting
- r/smallbusiness
- r/govcontracting

Post title: "I built a free tool that monitors grants.gov and SAM.gov 24/7
— would love feedback from grants professionals"

Frame it as seeking feedback, not selling. Include your URL.

## Day 8 — Follow Up Everyone
- [ ] Send Touch 3 to anyone who hasn't replied to Touch 1 or 2
- [ ] Re-email cold emails that got no response with a 1-line follow-up:
  "Just bumping this up — would a free trial be worth 2 minutes of your time?"
- [ ] Review who's signed up for trials — email them personally:
  "Hey [Name] — saw you signed up. I'm the founder. Any questions I can answer?
  Happy to hop on a quick call."

## Day 9 — Convert Trial Users
- [ ] Check your Railway logs / database for anyone who registered
- [ ] Email every trial user personally (you have their email from signup)
- [ ] Ask: "What would make this a no-brainer for your organization?"
- [ ] Offer to jump on a call with anyone who's on the fence

## Day 10 — Close
- [ ] Follow up with every warm lead from the past 9 days
- [ ] For anyone who liked it but hasn't paid: offer a deal
  "I'm running a founder's special this week — lock in $199/month for life
  if you start today. After this week it goes to $299."
- [ ] Ask your first trial user directly:
  "Based on what you've seen, does this solve a real problem for [Org Name]?
  If so, I'd love to have you as our first customer."

---

# PAGE 6: HOW TO HANDLE COMMON SITUATIONS

## "Can you send me more information?"
"Absolutely — what's your email? I'll send you the link to the free trial
and a 2-minute overview. The easiest way to see if it's right for you is
just to try it — takes 2 minutes and no credit card."

Don't send a PDF. Send the trial link. Get them in the product.

## "We already use [GrantStation / Instrumentl / etc.]"
"I'm familiar with them — they're great for searching grant databases.
We do something different: we monitor for NEW postings in real time and
alert you the moment something matches your org, rather than you going in
to search manually. Do you have something that does that automatically?"

## "We can't afford it right now"
"I get it — budgets are tight. That's exactly why I made the trial free
with no credit card. Use it for 14 days, see if you win something with it,
and then decide. If it doesn't find you anything useful, you owe nothing."

## "I need to run it by my director / board"
"Of course. Would it help if I put together a quick 1-page summary you
could share with them? And is there a good time to do a brief call with
both of you so I can answer any questions directly?"

## "How do I know the grants are legitimate?"
"All our data comes directly from the official government APIs —
grants.gov and SAM.gov — the same sources your team would check manually.
We just automate the monitoring and match them to your organization."

---

# PAGE 7: AFTER YOU GET YOUR FIRST CUSTOMER

## Do This Immediately
1. Send them a personal thank-you (not automated — a real email or text)
2. Check in after their first week: "Did you get any alerts? Any questions?"
3. After 30 days, ask for a testimonial:
   "Would you be willing to write 2-3 sentences about how you're using the
   tool and what it's done for your organization? I'd love to add it to the
   site."
4. Ask for a referral:
   "Do you know any other nonprofits or contractors who might benefit from
   this? Even a warm intro by email goes a long way."

## Pricing After First Customer
- Don't change your prices
- Add the testimonial to your landing page immediately
- Use "Our customers include [Org Name]" in future outreach
- One real customer name is worth more than any feature list

## Month 1 Goal: 5 Customers
Once you have 1, run the same playbook again.
5 customers at $299 = $1,495 MRR.
That covers your Railway hosting, API costs, domain, and email — with profit left over.

## Month 3 Goal: 20 Customers
At this point:
- You have real testimonials
- You have product feedback to improve the app
- You have referrals coming in organically
- MRR = ~$6,000/month
- Start reaching out to Pro plan prospects ($799/mo)

---

# PAGE 8: THE MINDSET

## What Will Actually Determine Your Success

**Speed beats perfection.**
The app works. The product is real. Don't spend another week tweaking it
before you start selling. Ship it and sell it today.

**Rejection is data, not failure.**
Every "no" tells you something — wrong prospect, wrong message, wrong timing.
Adjust and move on. You need 50 conversations to find 1 customer.
That's normal. That's sales.

**Follow up more than feels comfortable.**
Most people buy after the 3rd–5th touchpoint. If you send one email and
give up, you will never get a customer. Follow up until they say no or yes.

**Talk to your users.**
Every person who signs up for a trial is gold. Call them. Ask what they
wanted and didn't find. Ask what would make them pay. They will tell you
exactly how to build a business.

**The goal this week is conversations, not closes.**
If you have 10 real conversations with qualified prospects this week,
you will get a customer. Focus on conversations first, closes second.

---

# QUICK REFERENCE CARD

| Day | Primary Action | Secondary Action |
|-----|---------------|-----------------|
| 1 | Deploy + domain + email setup | Test live app end to end |
| 2 | Build 50-person prospect list | Set up tracking spreadsheet |
| 3 | LinkedIn outreach + cold emails | Post on LinkedIn |
| 4 | Follow-up Touch 2 + 25 new prospects | Facebook group posts |
| 5 | Calls + Zoom demos | Respond to all replies |
| 6 | Warm network outreach | Ask for referrals |
| 7 | Reddit + online communities | Follow up on no-replies |
| 8 | Touch 3 to all prospects | Personal email to trial users |
| 9 | Convert trial users | Gather feedback |
| 10 | Close + founder's special offer | Ask for referrals from anyone interested |

**Daily minimums:**
- 20 outreach touches (LinkedIn messages, emails, calls)
- Respond to every reply within 2 hours
- Check Railway logs to see who signed up

**The number that matters most:** Conversations. Not followers, not impressions, not signups. Real conversations with real decision makers.
