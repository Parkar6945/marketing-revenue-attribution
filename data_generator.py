import random
import json
from datetime import datetime, timedelta

CHANNELS = ["Paid Search (Google Ads)", "Social Ads (Meta)", "LinkedIn B2B", "SEO Organic", "Email Marketing", "Webinar / Events", "Referral / Partner"]
CAMPAIGNS = {
    "Paid Search (Google Ads)": ["Brand_Search_Q3", "Intent_HighValue_Search", "Competitor_Conquesting"],
    "Social Ads (Meta)": ["Meta_Retargeting_Video", "Meta_TopFunnel_Awareness", "Meta_Lookalike_Prospects"],
    "LinkedIn B2B": ["Enterprise_DecisionMakers", "Tech_Leaders_Sponsored", "InMail_LeadGen"],
    "SEO Organic": ["Organic_Blog_Tutorials", "Homepage_DirectOrganic", "Product_Comparison_Guides"],
    "Email Marketing": ["Nurture_Drip_Series", "Product_Demo_Followup", "ReEngagement_Campaign"],
    "Webinar / Events": ["Q3_Tech_Virtual_Summit", "Product_DeepDive_Webinar"],
    "Referral / Partner": ["Affiliate_TechPartners", "Client_Referral_Incentive"]
}

CHANNEL_COST_ESTIMATES = {
    "Paid Search (Google Ads)": 28500,
    "Social Ads (Meta)": 24000,
    "LinkedIn B2B": 31000,
    "SEO Organic": 8500,
    "Email Marketing": 4200,
    "Webinar / Events": 16000,
    "Referral / Partner": 9800
}

def generate_customer_journeys(num_customers=500):
    random.seed(42)
    start_date = datetime(2026, 7, 1)
    journeys = []

    for i in range(1, num_customers + 1):
        customer_id = f"CUST-{1000 + i}"
        num_touchpoints = random.choices([1, 2, 3, 4, 5, 6], weights=[15, 30, 25, 15, 10, 5])[0]
        
        # Determine if journey converted
        # Realistic funnel: lead generation rate high (~65%), conversion to closed-won revenue (~28%)
        became_lead = random.random() < 0.65
        converted = became_lead and (random.random() < 0.45)
        deal_value = round(random.uniform(2500, 18000), 2) if converted else 0.0

        touchpoints = []
        current_time = start_date + timedelta(days=random.randint(0, 60), hours=random.randint(8, 20))

        for step in range(num_touchpoints):
            channel = random.choice(CHANNELS)
            campaign = random.choice(CAMPAIGNS[channel])
            touchpoints.append({
                "step_order": step + 1,
                "channel": channel,
                "campaign": campaign,
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S")
            })
            current_time += timedelta(days=random.randint(1, 10), hours=random.randint(1, 8))

        journeys.append({
            "customer_id": customer_id,
            "became_lead": became_lead,
            "converted": converted,
            "revenue": deal_value,
            "touchpoint_count": len(touchpoints),
            "touchpoints": touchpoints
        })

    with open("customer_journeys.json", "w", encoding="utf-8") as f:
        json.dump(journeys, f, indent=2)

    with open("channel_costs.json", "w", encoding="utf-8") as f:
        json.dump(CHANNEL_COST_ESTIMATES, f, indent=2)

    print(f"Generated {num_customers} customer journeys successfully.")

if __name__ == "__main__":
    generate_customer_journeys()
