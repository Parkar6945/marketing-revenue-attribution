import json
import math
from collections import defaultdict

class AttributionEngine:
    def __init__(self, journeys_path="customer_journeys.json", costs_path="channel_costs.json"):
        with open(journeys_path, "r", encoding="utf-8") as f:
            self.journeys = json.load(f)
        with open(costs_path, "r", encoding="utf-8") as f:
            self.channel_costs = json.load(f)

    def calculate_attribution_models(self):
        first_touch = defaultdict(float)
        last_touch = defaultdict(float)
        linear = defaultdict(float)
        time_decay = defaultdict(float)
        u_shaped = defaultdict(float)

        total_conversions = 0
        total_revenue = 0.0
        funnel_stats = {
            "total_visitors": len(self.journeys),
            "total_leads": sum(1 for j in self.journeys if j["became_lead"]),
            "total_customers": sum(1 for j in self.journeys if j["converted"]),
            "total_revenue": sum(j["revenue"] for j in self.journeys)
        }

        for j in self.journeys:
            if not j["converted"]:
                continue

            rev = j["revenue"]
            total_conversions += 1
            total_revenue += rev
            tps = j["touchpoints"]
            n = len(tps)

            # 1. First-Touch Attribution
            first_channel = tps[0]["channel"]
            first_touch[first_channel] += rev

            # 2. Last-Touch Attribution
            last_channel = tps[-1]["channel"]
            last_touch[last_channel] += rev

            # 3. Linear Attribution
            split_rev = rev / n
            for tp in tps:
                linear[tp["channel"]] += split_rev

            # 4. Time-Decay Attribution (exponential decay towards the last touch)
            half_life_days = 7.0
            weights = []
            for idx, tp in enumerate(tps):
                # distance from last touchpoint in arbitrary decay scale
                dist = (n - 1 - idx)
                weight = math.pow(0.5, dist / 2.0)
                weights.append(weight)
            sum_w = sum(weights)
            for idx, tp in enumerate(tps):
                time_decay[tp["channel"]] += rev * (weights[idx] / sum_w)

            # 5. U-Shaped (40% first, 40% last, 20% middle)
            if n == 1:
                u_shaped[tps[0]["channel"]] += rev
            elif n == 2:
                u_shaped[tps[0]["channel"]] += rev * 0.5
                u_shaped[tps[1]["channel"]] += rev * 0.5
            else:
                u_shaped[tps[0]["channel"]] += rev * 0.40
                u_shaped[tps[-1]["channel"]] += rev * 0.40
                mid_rev = (rev * 0.20) / (n - 2)
                for tp in tps[1:-1]:
                    u_shaped[tp["channel"]] += mid_rev

        all_channels = sorted(list(self.channel_costs.keys()))
        comparison = []
        for ch in all_channels:
            cost = self.channel_costs.get(ch, 1000.0)
            lin_rev = linear.get(ch, 0.0)
            roi = ((lin_rev - cost) / cost * 100.0) if cost > 0 else 0.0

            comparison.append({
                "channel": ch,
                "cost": round(cost, 2),
                "first_touch": round(first_touch.get(ch, 0.0), 2),
                "last_touch": round(last_touch.get(ch, 0.0), 2),
                "linear": round(lin_rev, 2),
                "time_decay": round(time_decay.get(ch, 0.0), 2),
                "u_shaped": round(u_shaped.get(ch, 0.0), 2),
                "linear_roas": round(lin_rev / cost, 2) if cost > 0 else 0.0,
                "roi_percent": round(roi, 1)
            })

        # Calculate funnel drop-off analysis
        lead_conv_rate = (funnel_stats["total_leads"] / funnel_stats["total_visitors"]) * 100
        deal_close_rate = (funnel_stats["total_customers"] / funnel_stats["total_leads"]) * 100
        overall_conversion = (funnel_stats["total_customers"] / funnel_stats["total_visitors"]) * 100

        # AI Insights / Recommendations
        recommendations = self.generate_insights(comparison, funnel_stats)

        return {
            "funnel": {
                **funnel_stats,
                "lead_conversion_rate": round(lead_conv_rate, 1),
                "deal_close_rate": round(deal_close_rate, 1),
                "overall_conversion_rate": round(overall_conversion, 1)
            },
            "channel_attribution": comparison,
            "recommendations": recommendations
        }

    def generate_insights(self, comparison, funnel):
        insights = []
        
        # Identify underperforming and high-performing channels
        best_channel = max(comparison, key=lambda x: x["linear_roas"])
        worst_channel = min(comparison, key=lambda x: x["linear_roas"])

        insights.append({
            "type": "opportunity",
            "title": f"Top Performing Channel: {best_channel['channel']}",
            "description": f"Generating a {best_channel['linear_roas']}x ROAS (${best_channel['linear']:,.0f} revenue against ${best_channel['cost']:,.0f} cost). Recommend increasing allocation by 15-25%."
        })

        if worst_channel['linear_roas'] < 1.0:
            insights.append({
                "type": "warning",
                "title": f"Subsidized/Loss-Making Channel: {worst_channel['channel']}",
                "description": f"Producing only {worst_channel['linear_roas']}x ROAS. Cost (${worst_channel['cost']:,.0f}) exceeds attributed revenue (${worst_channel['linear']:,.0f}). Requires targeting audit or budget haircut."
            })

        # Multi-touch discrepancy insight
        for ch in comparison:
            ft = ch["first_touch"]
            lt = ch["last_touch"]
            if ft > lt * 1.5 and ft > 10000:
                insights.append({
                    "type": "info",
                    "title": f"Key Brand Opener: {ch['channel']}",
                    "description": f"First-touch revenue (${ft:,.0f}) significantly outstrips last-touch (${lt:,.0f}). Do NOT cut this top-of-funnel driver even if last-click looks modest."
                })
                break

        return insights

if __name__ == "__main__":
    engine = AttributionEngine()
    results = engine.calculate_attribution_models()
    print("Funnel:", results["funnel"])
