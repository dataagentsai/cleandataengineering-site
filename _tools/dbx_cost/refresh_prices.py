"""Refresh the cost calculator's prices.

    python3 _tools/dbx_cost/refresh_prices.py            # update prices.json, print a summary
    python3 _tools/dbx_cost/refresh_prices.py --check    # report only, change nothing

What it refreshes:
  * EC2 on-demand prices (US East, Linux) for every instance in prices.json, from AWS's public price
    list (no key needed).
  * Databricks DBU list prices, from the system.billing.list_prices table, but only when a workspace is
    connected through DATABRICKS_HOST, DATABRICKS_TOKEN and DATABRICKS_WAREHOUSE_ID. Databricks' public
    pricing pages load their prices in the browser, so they can't be read reliably by a script.
Anything not refreshed and older than 60 days is listed as due for a manual check.
The summary is Markdown, so the monthly GitHub Action can use it as the pull request body.
"""
import gzip
import json
import os
import sys
import urllib.request
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRICES = HERE / "prices.json"
EC2_URL = ("https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/"
           "ec2-ondemand-without-sec-sel/US%20East%20(N.%20Virginia)/Linux/index.json")
TODAY = date.today().isoformat()
STALE_DAYS = 60


def fetch(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "cleandataengineering-price-refresh", **(headers or {})})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return json.loads(raw)


def refresh_ec2(p, changes, notes):
    try:
        feed = fetch(EC2_URL)
    except Exception as ex:  # keep going; report it
        notes.append(f"EC2 price list could not be read: {ex}")
        return
    region = next(iter(feed["regions"].values()))
    by_type = {v.get("Instance Type"): float(v["price"]) for v in region.values() if v.get("Instance Type")}
    for name, inst in p["instances"].items():
        new = by_type.get(name)
        if new is None:
            notes.append(f"EC2 {name}: not found in the AWS price list")
            continue
        new = round(new, 4)
        if abs(new - inst["usd_per_hour"]) > 1e-6:
            changes.append(f"EC2 {name}: ${inst['usd_per_hour']} → ${new} per hour")
            inst["usd_per_hour"] = new
    p["instances_meta"]["checked"] = TODAY
    p["instances_meta"]["usd_status"] = "checked"


def refresh_dbu(p, changes, notes):
    host, token, wh = (os.environ.get(k) for k in ("DATABRICKS_HOST", "DATABRICKS_TOKEN", "DATABRICKS_WAREHOUSE_ID"))
    if not (host and token and wh):
        notes.append("Databricks DBU prices not refreshed: no workspace connected (set DATABRICKS_HOST, DATABRICKS_TOKEN, DATABRICKS_WAREHOUSE_ID).")
        return
    sql = ("SELECT sku_name, pricing.default AS price FROM system.billing.list_prices "
           "WHERE cloud = 'AWS' AND currency_code = 'USD' AND price_end_time IS NULL")
    body = json.dumps({"statement": sql, "warehouse_id": wh, "wait_timeout": "50s"}).encode()
    try:
        res = fetch(host.rstrip("/") + "/api/2.0/sql/statements", data=body,
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
        rows = {r[0]: float(r[1]) for r in res["result"]["data_array"]}
    except Exception as ex:
        notes.append(f"Databricks list prices could not be read: {ex}")
        return
    for key, item in p["dbu"].items():
        for tier in ("premium", "enterprise"):
            for pattern in item.get("system_sku", []):
                sku = pattern.replace("{tier}", tier.upper())
                if sku in rows:
                    new = round(rows[sku], 4)
                    if abs(new - item[tier]) > 1e-6:
                        changes.append(f"{item['label']} ({tier}): ${item[tier]} → ${new} per DBU")
                        item[tier] = new
                    item["status"], item["checked"] = "checked", TODAY
                    item["source"] = "system.billing.list_prices"
                    break


def stale(p):
    out = []
    for key, item in p["dbu"].items():
        checked = item.get("checked")
        if not checked or (date.today() - date.fromisoformat(checked)).days > STALE_DAYS:
            out.append(f"{item['label']} (last checked {checked or 'never'})")
    return out


def main():
    check_only = "--check" in sys.argv
    p = json.loads(PRICES.read_text())
    changes, notes = [], []
    refresh_ec2(p, changes, notes)
    refresh_dbu(p, changes, notes)
    due = stale(p)
    if changes and not check_only:
        p["as_of"] = TODAY
    if not check_only:
        PRICES.write_text(json.dumps(p, indent=2, ensure_ascii=False) + "\n")
    print(f"## Cost calculator price refresh, {TODAY}\n")
    print("### Changed\n" + ("\n".join(f"- {c}" for c in changes) if changes else "- No price changes."))
    if notes:
        print("\n### Notes\n" + "\n".join(f"- {n}" for n in notes))
    if due:
        print("\n### Due for a manual check against databricks.com/product/pricing\n" + "\n".join(f"- {d}" for d in due))


if __name__ == "__main__":
    main()
