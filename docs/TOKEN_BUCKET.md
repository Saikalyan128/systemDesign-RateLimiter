# Token Bucket Algorithm

## What is it?

Token Bucket is a rate-limiting algorithm that controls how many requests a client can make over time.  
It allows **short bursts** of traffic while enforcing a **sustained average rate**.

---

## Core Concept

Think of a physical bucket that holds tokens:

```
             +------------------+
  Refill →   |  ● ● ● ● ● ● ● ●|  ← bucket_limit (max tokens)
  (rate/sec) |                  |
             +------------------+
                      ↓
              Incoming Request
                      ↓
          token available?
          ┌─────Yes──────┐
          ↓              ↓
     Consume 1 token   No tokens left
     ✅ Allow request  ❌ 429 Too Many Requests
```

- Tokens are added at a fixed **refill rate** every **interval** seconds.
- Each request consumes **1 token**.
- If the bucket is empty, the request is **rejected**.
- The bucket never exceeds **bucket_limit** tokens.

---

## Parameters (this implementation)

| Parameter      | Default | Description                              |
|----------------|---------|------------------------------------------|
| `bucket_limit` | 8       | Maximum tokens the bucket can hold       |
| `refill_rate`  | 3       | Tokens added per interval                |
| `interval`     | 5s      | How often (in seconds) refill is checked |

With these defaults: a client gets **3 tokens every 5 seconds**, with a burst capacity of **8**.

---

## How a Request Flows Through the Code

```
HTTP Request
     │
     ▼
middleware (main.py)
     │  calls
     ▼
RateLimiter.TokenBucket(ip_address)        ← Ratelimiter.py
     │
     ├─ New IP?  → create TokenBucketAlgo, store in clients{}
     └─ Known IP? → reuse existing object (state preserved)
          │
          ▼
     token_obj.accept_request()             ← tokenbucket.py
          │
          ├─ refill()
          │     └─ elapsed >= interval?
          │           yes → add (refill_rate × intervals_elapsed) tokens
          │                 cap at bucket_limit
          │                 advance start_time by full intervals only*
          │           no  → skip
          │
          ├─ token >= 1?
          │     yes → token -= 1 → return True  → 200 OK
          └─     no →              return False → 429 Too Many Requests
```

> \* Advancing `start_time` by only full intervals (not resetting to `now`) preserves the  
> leftover partial-interval time, so no time is lost between refills.

---

## Step-by-step Example

Config: `bucket_limit=8, refill_rate=3, interval=5s`

| Time   | Event                        | Tokens Before | Tokens After |
|--------|------------------------------|---------------|--------------|
| t=0s   | Client connects, bucket init | —             | 8            |
| t=0s   | Request 1                    | 8             | 7            |
| t=0s   | Request 2                    | 7             | 6            |
| t=0s   | Request 3–8 (burst)          | 6             | 0            |
| t=0s   | Request 9                    | 0             | **429**      |
| t=5s   | Request 10 (refill triggers) | 0 + 3 = 3     | 2            |
| t=10s  | Request 11 (refill triggers) | 2 + 3 = 5     | 4            |

---

## Key Properties

| Property         | Behaviour                                                       |
|------------------|-----------------------------------------------------------------|
| **Burst support** | A full bucket allows up to `bucket_limit` requests instantly   |
| **Rate control**  | Sustained throughput limited to `refill_rate / interval` req/s |
| **Per-client**    | Each IP gets its own independent bucket (via `clients{}` dict) |
| **No starvation** | Slow/infrequent clients always accumulate tokens over time     |

---

## Compared to Other Algorithms

| Algorithm          | Burst Allowed | Memory | Smoothness |
|--------------------|---------------|--------|------------|
| **Token Bucket**   | ✅ Yes         | Low    | Good       |
| Leaky Bucket       | ❌ No          | Low    | Strict     |
| Fixed Window       | ✅ Yes         | Low    | Poor       |
| Sliding Window Log | ❌ No          | High   | Best       |

---

## Files

| File              | Role                                                    |
|-------------------|---------------------------------------------------------|
| `tokenbucket.py`  | `TokenBucketAlgo` class — bucket state + refill logic  |
| `Ratelimiter.py`  | `RateLimiter` class — per-IP bucket management         |
| `main.py`         | FastAPI middleware — intercepts every request           |
| `test_client.py`  | Tests: health check + 429 burst test                   |
