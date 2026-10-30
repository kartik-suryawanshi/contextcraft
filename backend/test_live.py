import httpx
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

client = httpx.Client(base_url="http://127.0.0.1:8000")

# 1. Health
h = client.get("/api/v1/health").json()
print("HEALTH:", h)

# 2. Run Project Orion Execution
payload = {
    "query": (
        "Prepare an analysis of Project Orion. Its original budget was ₹10 lakh, "
        "the deadline was December 2026, and the project budget was later revised to ₹12 lakh. "
        "Explain the current project status using the available information."
    ),
    "max_iterations": 2,
    "mock_mode": True,
}
res = client.post("/api/v1/executions", json=payload).json()
print(f"EXECUTION ID: {res['id']}, STATUS: {res['status']}, LATENCY: {res['total_duration_ms']}ms, TOKENS: {res['total_tokens_estimated']}")
print(f"FINAL ANSWER:\n{res['final_answer']}\n")

# 3. Check Memories
mems = client.get("/api/v1/memories").json()
print(f"TOTAL MEMORIES: {mems['total']}")
for item in mems["items"]:
    print(f"  [{item['status'].upper()}] {item['topic']}: {item['fact_text']} (val={item['value']})")

# 4. Check Conflict Audits
audits = client.get("/api/v1/memories/audits/conflicts").json()
print(f"\nCONFLICT AUDIT EVENTS ({len(audits)}):")
for a in audits:
    print(f"  {a['topic']} ({a['resolution_type']}): {a['explanation']}")

# 5. Check Traces
traces = client.get(f"/api/v1/executions/{res['id']}/traces").json()
print(f"\nEXECUTION TRACES ({len(traces)}):")
for t in traces:
    print(f"  Step {t['step_order']}: Agent '{t['agent_name']}' completed in {t['duration_ms']}ms, {t['estimated_token_count']} tokens")

# 6. Check Memory Views
views = client.get(f"/api/v1/executions/{res['id']}/memory-views").json()
print(f"\nROLE MEMORY VIEWS ({len(views)}):")
for v in views:
    print(f"  Agent '{v['agent_name']}': {v['tokens_consumed']}/{v['token_budget']} tokens consumed ({len(v['selected_units'])} accepted, {len(v['excluded_units'])} excluded)")
