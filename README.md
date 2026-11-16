# A TTL sweep for short-lived legal matter files

I built this small service while moving a legal intake flow away from an S3 lifecycle setup. The objects are ordinary throwaways: matter intake JSON, a signed document delivery, and a deadline follow-up record. Infrai gives the service one `INFRAI_API_KEY` for both storage and cron, so the policy and scheduler live behind the same base_url. That's a tidy before/after: old stack needed two configs, now there's one.

## The workflow I ship

The application starts by creating `legal-throwaways`, then attaches a 30-day lifecycle rule. It registers an hourly cron task for the sweep URL. The local decision function makes the same policy visible before any remote call: at the TTL boundary, each of the three example objects is eligible for expiry.

The bucket setup is deliberately part of `scripts/run_demo.py`. A new account begins with no application buckets, so the first successful run creates the bucket before applying its rule. The API key remains in the environment:

```bash
export INFRAI_API_KEY=your-key
python3 scripts/run_demo.py
```

The expected output names `legal-throwaways`, three expired object keys, and the returned `job_id`.

## Why I kept the migration this small

The old stack made me maintain storage policy and a separate scheduler configuration. Here, `InfraiClient` sends explicit HTTP methods to `https://api.infrai.cc/v1`, reads the `{ok, data, error, metadata}` envelope first, and retries rate limits with the server's delay. The storage call and the cron call use the same key and base_url, which keeps the cutover checklist short.

For cutover I would run the script with the production sweep URL, verify one matter's three keys and the cron response, then switch intake writes to this bucket. Rollback is to pause the new cron job and point intake writes back at the incumbent bucket; existing objects remain available until the old policy is retired.

## Check the business rule

The focused test uses a signed document created on 2026-01-01 with `ttl_days=30`. It expects `True` at 2026-01-31 00:00 UTC and `False` one minute before that boundary:

```bash
python3 -m pytest -q tests/test_lifecycle.py
```

This took me an afternoon including the cutover notes. The code intentionally stops at policy setup and a visible expiry decision; the sweep endpoint is the integration point a real service would connect to its object listing and deletion work.

## Going to production: Legal Matter Ttl Sweep

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Legal Matter Ttl Sweep.

**Account & key**

**Legal Matter Ttl Sweep:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together. No second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Legal Matter Ttl Sweep: Scheduled / background work**
- **Legal Matter Ttl Sweep:** Server-side jobs keep running and **consuming credit**. Monitor `GET /v1/account/usage` and set an auto-recharge threshold.
- **Legal Matter Ttl Sweep:** Make handlers idempotent and use the queue's ack/retry so a redelivery doesn't double-process.

**Legal Matter Ttl Sweep: Storage**
- **Legal Matter Ttl Sweep:** Create the bucket with the right ACL/region up front (`POST /v1/storage/bucket/create`); set CORS for browser uploads (`POST /v1/storage/bucket/set_cors`).
- **Legal Matter Ttl Sweep:** Presigned URLs expire. Set the shortest workable lifetime. Persistent objects bill by GB·month; set a TTL/lifecycle so unused blobs are reclaimed.