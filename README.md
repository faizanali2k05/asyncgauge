# asyncgauge

Run synchronous or asynchronous health probes concurrently and return structured timing/results without coupling the probe layer to a web framework.

```bash
python -m pip install asyncgauge
```

```python
from asyncgauge import healthy, run_all

results = await run_all({"database": check_database, "queue": check_queue}, timeout=2)
if not healthy(results):
    return {"status": "degraded", "checks": [item.as_dict() for item in results]}
```

Each probe is isolated: failures become `ProbeResult` records, results are sorted by name for stable output, and asynchronous probes receive a deadline. Keep probes small and side-effect free; the package reports health but does not decide how your service should respond.
