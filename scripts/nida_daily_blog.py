#!/usr/bin/env python3
"""
Nida Daily Blog Poster — Auto-generates and publishes blog posts
via the Nida Agent API. Runs headless, no approval needed for creates.
"""
import json
import os
import random
import re
import string
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# ─── CONFIG ─────────────────────────────────────────────────────────
API_KEY = os.environ.get("NIDA_AGENT_API_KEY", "")
if not API_KEY:
    key_file = Path(__file__).with_name(".nida_api_key")
    if key_file.exists():
        API_KEY = key_file.read_text().strip()

WORKSPACE_ID = "155a9310-0d78-4241-ac87-71a7ce6b68ad"
SITE_ID = "14760766-a5e7-4c04-b72d-77da83194f0d"      # nida.craftedmatrix.com
TOPICS_FILE = Path.home() / ".hermes" / "scripts" / "nida_blog_topics.json"
STATE_FILE = Path.home() / ".hermes" / "scripts" / "nida_blog_state.json"
API_URL = "https://www.nida-os.com/api/agent/execute"

# ─── TOPIC BANK ─────────────────────────────────────────────────────
DEFAULT_TOPICS = [
    {
        "title": "5 Ways AI Agents Are Transforming Small Business CRMs",
        "slug": "ai-agents-transforming-small-business-crm",
        "meta_title": "5 Ways AI Agents Are Transforming Small Business CRMs",
        "meta_description": "Discover how AI-powered agents are revolutionizing customer relationship management for small businesses in 2026.",
        "sections": [
            ("h2", "Introduction"),
            ("p", "Small businesses are increasingly turning to AI agents to streamline their customer relationship management. These intelligent systems can automate repetitive tasks, provide personalized customer interactions, and deliver insights that were previously only available to enterprise-level organizations."),
            ("h2", "1. Automated Lead Qualification"),
            ("p", "AI agents can instantly score and categorize incoming leads based on behavior, demographics, and engagement history. This ensures your sales team focuses on the most promising prospects while nurturing the rest automatically."),
            ("h2", "2. 24/7 Customer Support"),
            ("p", "With AI-powered chatbots and voice agents, small businesses can offer round-the-clock support without hiring additional staff. These agents handle FAQs, troubleshoot issues, and escalate complex cases to human team members."),
            ("h2", "3. Predictive Analytics"),
            ("p", "Modern AI CRMs analyze historical data to predict customer churn, identify upsell opportunities, and forecast revenue trends. This empowers business owners to make data-driven decisions proactively."),
            ("h2", "4. Personalized Marketing at Scale"),
            ("p", "AI agents craft individualized email campaigns, social media posts, and follow-up sequences based on each contact's preferences and journey stage. The result is higher engagement and conversion rates."),
            ("h2", "5. Seamless Workflow Automation"),
            ("p", "From scheduling appointments to sending invoices, AI agents integrate with your existing tools to eliminate manual busywork. This frees up your team to focus on strategy and relationship building."),
            ("h2", "Conclusion"),
            ("p", "The future of small business CRM is agentic. By embracing AI-powered automation now, you position your business to scale efficiently while delivering exceptional customer experiences."),
        ]
    },
    {
        "title": "Why Every Startup Needs an Agentic CRM in 2026",
        "slug": "why-startups-need-agentic-crm-2026",
        "meta_title": "Why Every Startup Needs an Agentic CRM in 2026",
        "meta_description": "Startups that adopt agentic CRM systems gain a competitive edge through automation, intelligence, and scalability.",
        "sections": [
            ("h2", "The Startup Advantage"),
            ("p", "Startups operate in fast-paced environments where every minute and dollar counts. Traditional CRMs require constant manual input, but agentic CRMs act as autonomous team members that handle data entry, follow-ups, and reporting."),
            ("h2", "Speed to Lead"),
            ("p", "Research shows that responding to a lead within 5 minutes increases conversion rates by 900%. Agentic CRMs ensure instant engagement via auto-responders, chatbots, and voice AI — even while you sleep."),
            ("h2", "Zero-Click Data Capture"),
            ("p", "Every email, call, and meeting is automatically logged, categorized, and analyzed. Your team never has to waste time on data entry again."),
            ("h2", "Intelligent Prioritization"),
            ("p", "AI agents rank your pipeline based on deal velocity, engagement signals, and historical close rates. Founders can focus on the deals that matter most."),
            ("h2", "Built for Scale"),
            ("p", "As your startup grows, your agentic CRM scales with you. Add new workflows, integrations, and team members without switching platforms or retraining staff."),
            ("h2", "Getting Started"),
            ("p", "The barrier to entry has never been lower. Modern agentic CRMs offer startup-friendly pricing, quick onboarding, and no-code customization. Start with one workflow and expand from there."),
        ]
    },
    {
        "title": "The Complete Guide to CRM Automation for Service Businesses",
        "slug": "crm-automation-guide-service-businesses",
        "meta_title": "The Complete Guide to CRM Automation for Service Businesses",
        "meta_description": "Learn how service-based businesses can automate scheduling, follow-ups, invoicing, and customer communication with a modern CRM.",
        "sections": [
            ("h2", "What Is CRM Automation?"),
            ("p", "CRM automation refers to the use of technology to perform repetitive customer relationship tasks without human intervention. For service businesses, this includes appointment reminders, follow-up emails, review requests, and more."),
            ("h2", "1. Appointment & Scheduling Automation"),
            ("p", "Integrate your CRM with scheduling tools like Calendly or Acuity. Automatically send confirmation emails, SMS reminders 24 hours before appointments, and follow-up messages after service completion."),
            ("h2", "2. Pipeline Management"),
            ("p", "Track every client from initial inquiry to project completion. Automated stage transitions move deals forward based on triggers like signed contracts or completed payments."),
            ("h2", "3. Review Generation"),
            ("p", "Happy clients are your best marketers. Automate review requests via email or SMS 3–7 days after service delivery. Include direct links to Google, Yelp, or industry-specific platforms."),
            ("h2", "4. Recurring Service Reminders"),
            ("p", "For maintenance, cleaning, or coaching businesses, automate reminders for recurring appointments. Reduce no-shows and keep clients engaged long-term."),
            ("h2", "5. Invoicing & Payment Follow-Up"),
            ("p", "Connect your CRM to Stripe, PayPal, or Square. Send invoices automatically and trigger polite payment reminders for overdue accounts."),
            ("h2", "Conclusion"),
            ("p", "Service businesses that embrace CRM automation save 10+ hours per week, improve client satisfaction, and increase repeat bookings. The technology is accessible, affordable, and transformative."),
        ]
    },
    {
        "title": "How AI Voice Agents Are Replacing Traditional Phone Systems",
        "slug": "ai-voice-agents-replacing-phone-systems",
        "meta_title": "How AI Voice Agents Are Replacing Traditional Phone Systems",
        "meta_description": "AI voice agents now handle inbound calls, schedule appointments, and answer FAQs with human-like natural conversation.",
        "sections": [
            ("h2", "The End of Hold Music"),
            ("p", "Customers hate waiting on hold. AI voice agents answer instantly, 24/7, with natural-sounding conversation. They understand context, handle objections, and route complex issues to the right human specialist."),
            ("h2", "Conversational Intelligence"),
            ("p", "Modern voice AI uses large language models and emotion detection to adapt tone, pace, and vocabulary in real time. Callers often cannot distinguish AI from human agents."),
            ("h2", "Cost Efficiency"),
            ("p", "A single AI voice agent can handle thousands of concurrent calls at a fraction of the cost of a human call center. Businesses save 60–80% on phone support costs while improving availability."),
            ("h2", "Integration with CRM"),
            ("p", "When voice agents connect to your CRM, every call is logged, transcribed, and analyzed. Follow-up tasks are created automatically, and customer records are enriched with conversation data."),
            ("h2", "Real-World Results"),
            ("p", "Clinics using AI voice agents report 40% reduction in no-shows. E-commerce brands see 25% increase in phone orders. Service businesses reclaim 15+ hours per week previously spent on phone tag."),
            ("h2", "The Future Is Voice-First"),
            ("p", "As voice AI continues to improve, the line between human and machine support will blur. Early adopters gain customer loyalty through instant, empathetic, and always-available service."),
        ]
    },
    {
        "title": "Building a Sales Funnel That Converts While You Sleep",
        "slug": "sales-funnel-converts-while-you-sleep",
        "meta_title": "Building a Sales Funnel That Converts While You Sleep",
        "meta_description": "Design an automated sales funnel that captures leads, nurtures them with AI, and closes deals around the clock.",
        "sections": [
            ("h2", "The 24/7 Sales Machine"),
            ("p", "A well-designed sales funnel combined with AI automation creates a revenue engine that never sleeps. Leads enter at the top, get educated and nurtured automatically, and convert at the bottom — all without manual intervention."),
            ("h2", "Stage 1: Attract"),
            ("p", "Use SEO-optimized content, social media, and paid ads to drive traffic to landing pages. Offer valuable lead magnets like guides, calculators, or free trials in exchange for contact information."),
            ("h2", "Stage 2: Capture"),
            ("p", "Smart forms and chatbots capture lead data and instantly enrich it. AI agents verify emails, score leads, and segment audiences based on behavior and intent signals."),
            ("h2", "Stage 3: Nurture"),
            ("p", "Deploy multi-channel nurture sequences: welcome emails, educational content, case studies, and testimonials. AI personalizes timing and content based on engagement patterns."),
            ("h2", "Stage 4: Convert"),
            ("p", "When leads show buying signals — like visiting pricing pages or requesting demos — AI escalates them to your sales team with full context. Automated scheduling removes friction from the booking process."),
            ("h2", "Stage 5: Retain"),
            ("p", "Post-sale automation ensures smooth onboarding, gathers feedback, and identifies upsell opportunities. Happy customers become referral engines through automated review and referral requests."),
            ("h2", "Conclusion"),
            ("p", "The best sales funnels are invisible to the customer but indispensable to the business. Build yours once, optimize continuously, and let AI handle the heavy lifting."),
        ]
    },
    {
        "title": "Email Automation Strategies That Actually Drive Revenue",
        "slug": "email-automation-strategies-revenue",
        "meta_title": "Email Automation Strategies That Actually Drive Revenue",
        "meta_description": "Stop sending batch-and-blast emails. Learn segmentation, trigger-based automation, and personalization tactics that boost ROI.",
        "sections": [
            ("h2", "Beyond the Newsletter"),
            ("p", "Newsletters have their place, but revenue-driving email automation is behavioral, segmented, and triggered. It sends the right message to the right person at the exact moment they need it."),
            ("h2", "Welcome Sequences That Convert"),
            ("p", "First impressions matter. A 5–7 email welcome sequence introduces your brand story, showcases top content, and presents a low-risk offer. Automation ensures every new subscriber gets the same VIP treatment."),
            ("h2", "Abandoned Cart & Browse Recovery"),
            ("p", "E-commerce and service businesses lose millions to abandoned carts and incomplete inquiries. Automated recovery emails sent within 1–3 hours recover 10–15% of otherwise lost revenue."),
            ("h2", "Re-Engagement Campaigns"),
            ("p", "Subscribers go cold. AI identifies disengaged contacts and triggers win-back sequences with special offers, surveys, or valuable updates. Clean your list and revive dormant relationships."),
            ("h2", "Post-Purchase Upsells"),
            ("p", "The moment after purchase is the best time to sell again. Automate cross-sell and upsell emails based on purchase history, browsing behavior, and product affinity data."),
            ("h2", "Measuring What Matters"),
            ("p", "Track revenue per email, lifetime value impact, and automation-attributed conversions. Vanity metrics like open rates are secondary to actual dollar returns."),
            ("h2", "Conclusion"),
            ("p", "Email automation is not about sending more emails. It is about sending smarter emails. When powered by CRM data and AI, every message feels personal and drives measurable business outcomes."),
        ]
    },
    {
        "title": "Chatbots vs. AI Agents: What's the Difference for Your Business?",
        "slug": "chatbots-vs-ai-agents-business",
        "meta_title": "Chatbots vs. AI Agents: What's the Difference for Your Business?",
        "meta_description": "Understand the key differences between rule-based chatbots and modern AI agents to choose the right solution for customer engagement.",
        "sections": [
            ("h2", "Not All Bots Are Created Equal"),
            ("p", "The terms 'chatbot' and 'AI agent' are often used interchangeably, but they represent fundamentally different technologies with vastly different capabilities and business impact."),
            ("h2", "Rule-Based Chatbots"),
            ("p", "Traditional chatbots follow rigid decision trees. They match keywords to pre-written responses and cannot handle unexpected questions. They are cheap to build but break quickly and frustrate users."),
            ("h2", "Modern AI Agents"),
            ("p", "AI agents use large language models and can understand context, remember conversation history, and take actions. They book appointments, update CRM records, process refunds, and learn from feedback."),
            ("h2", "Use Case: Customer Support"),
            ("p", "A chatbot might deflect 20% of tickets. An AI agent resolves 70% end-to-end and escalates the remaining 30% with full context. The cost per resolution drops by 80%."),
            ("h2", "Use Case: Sales"),
            ("p", "Chatbots collect contact forms. AI agents qualify leads in real time, demo products via screen sharing, negotiate pricing within approved bands, and schedule meetings directly on sales reps' calendars."),
            ("h2", "Which Should You Choose?"),
            ("p", "If you need basic FAQ handling, a chatbot suffices. If you want to automate workflows, personalize interactions, and scale operations, invest in AI agents. The ROI difference is exponential."),
            ("h2", "Conclusion"),
            ("p", "The shift from chatbots to AI agents is as significant as the shift from brick-and-mortar to e-commerce. Early adopters will define the next era of customer experience."),
        ]
    },
    {
        "title": "How to Choose the Right CRM for Your Business Stage",
        "slug": "choose-right-crm-business-stage",
        "meta_title": "How to Choose the Right CRM for Your Business Stage",
        "meta_description": "From solopreneur to enterprise — learn which CRM features matter most at each stage of business growth.",
        "sections": [
            ("h2", "Stage 1: Solopreneur / Freelancer"),
            ("p", "You need simplicity. Look for free or low-cost CRMs with contact management, basic email integration, and mobile access. Avoid bloated enterprise features you will not use."),
            ("h2", "Stage 2: Small Team (2–10)"),
            ("p", "Collaboration becomes critical. Prioritize pipeline visibility, task assignment, shared calendars, and integration with your existing tools like Slack, QuickBooks, or Mailchimp."),
            ("h2", "Stage 3: Growing Business (10–50)"),
            ("p", "Automation is non-negotiable. You need workflow builders, email sequences, lead scoring, and reporting dashboards. API access enables custom integrations as you scale."),
            ("h2", "Stage 4: Established Company (50+)"),
            ("p", "Enterprise-grade security, role-based permissions, advanced analytics, and multi-department customization matter most. Consider white-label options and dedicated support."),
            ("h2", "The One Feature Every Stage Needs"),
            ("p", "Regardless of size, every business benefits from AI-powered automation. The sooner you adopt intelligent CRM features, the faster you outpace competitors stuck in manual processes."),
            ("h2", "Red Flags to Avoid"),
            ("p", "Beware of long-term contracts, expensive per-user pricing, poor mobile apps, and lack of API access. Choose a CRM that grows with you, not one that holds you hostage."),
            ("h2", "Conclusion"),
            ("p", "The right CRM at the right time accelerates growth. Re-evaluate your needs annually and do not be afraid to migrate when your current tool becomes a bottleneck."),
        ]
    },
]

# ─── HELPERS ──────────────────────────────────────────────────────────
def load_topics():
    if TOPICS_FILE.exists():
        return json.loads(TOPICS_FILE.read_text())
    return DEFAULT_TOPICS


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"used_indices": [], "next_index": 0}


def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def build_html(topic):
    lines = [f'<h1>{topic["title"]}</h1>']
    for tag, text in topic.get("sections", []):
        lines.append(f'<{tag}>{text}</{tag}>')
    return "\n".join(lines)


def slugify(title):
    s = title.lower()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s]+', '-', s)
    return s[:80].strip('-')


def call_nida(payload: dict):
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode())
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_post(topic, status="published"):
    now = datetime.now(timezone.utc).isoformat()
    html = build_html(topic)
    payload = {
        "workspace_id": WORKSPACE_ID,
        "module": "seo_content",
        "action": "create",
        "params": {
            "data": {
                "title": topic["title"],
                "slug": topic.get("slug") or slugify(topic["title"]),
                "body_content": html,
                "content_type": "blog_post",
                "status": status,
                "website_id": SITE_ID,
                "meta_title": topic.get("meta_title", topic["title"]),
                "meta_description": topic.get("meta_description", ""),
                "publish_date": now,
            }
        }
    }
    return call_nida(payload)


def run_batch(count=2):
    topics = load_topics()
    state = load_state()
    results = []

    available = [i for i in range(len(topics)) if i not in state["used_indices"]]
    if not available:
        # Reset when exhausted
        state["used_indices"] = []
        available = list(range(len(topics)))

    random.shuffle(available)
    to_use = available[:count]

    for idx in to_use:
        topic = topics[idx]
        resp = create_post(topic, status="published")
        results.append({
            "title": topic["title"],
            "index": idx,
            "response": resp,
        })
        if resp.get("success"):
            state["used_indices"].append(idx)

    save_state(state)
    return results


# ─── MAIN ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not API_KEY:
        print("ERROR: NIDA_AGENT_API_KEY env var not set")
        exit(1)

    count = int(os.environ.get("POST_COUNT", "2"))
    results = run_batch(count)

    successes = sum(1 for r in results if r["response"].get("success"))
    print(f"Created {successes}/{len(results)} posts")
    for r in results:
        status = "OK" if r["response"].get("success") else "FAIL"
        print(f"  [{status}] {r['title']}")
        if not r["response"].get("success"):
            print(f"       -> {r['response']}")
    exit(0 if successes == len(results) else 1)
