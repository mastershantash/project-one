# Python Quick Revision Sheet

Fast lookup for things already covered — not a tutorial, just a memory jog. New modules get appended below as we go.

---

## Module 1: Python Fast-Track (Java → Python)

### Syntax
| Java | Python |
|---|---|
| `{ }` blocks | Indentation (4 spaces) — colon `:` opens the block |
| `;` line end | Newline ends the statement |
| `//` comment | `#` comment |

```python
if x > 0:
    print("positive")
```

### Collections
| Java | Python | Notes |
|---|---|---|
| `ArrayList<T>` | `list` | mutable, ordered |
| `HashMap<K,V>` | `dict` | `d["key"] = value`, `d.get("key")` |
| `HashSet<T>` | `set` | unique, unordered |
| *(no direct equivalent)* | `tuple` | immutable, fixed-size: `(1, 2, 3)` |

```python
scores = {"alice": 90}
scores["bob"] = 85
for name, score in scores.items():
    print(name, score)
```

### List comprehensions (replaces `.stream().map()`)
Shape: `[expression for item in iterable]`

```python
doubled = [2 * n for n in nums]   # transforms each item independently
```

**Gotcha:** comprehensions do NOT accumulate a running total across iterations — every iteration is independent. Use a loop or `sum()` for that.

### Type hints (pairs with `mypy` for Java-style safety)
```python
def total_score(scores: dict[str, int]) -> int:
    return sum(scores.values())
```

### Classes & duck typing
- `self` is explicit — first parameter of every method (Java's implicit `this`, made visible).
- `__init__` is the constructor.
- No `interface` keyword — Python uses duck typing ("if it has the right methods, it works"), or `Protocol`/`ABC` when you want an explicit contract.
- No access modifiers — `_leading_underscore` is the "private" convention, not enforced.
- `.pop(key, None)` = safe delete (no `KeyError` if missing).

```python
class Cache:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.store: dict[str, int] = {}

    def evict(self, key: str) -> None:
        self.store.pop(key, None)
```

### Error handling
Maps ~1:1 to Java's `try`/`catch`/`finally`. No checked-vs-unchecked distinction — everything's effectively unchecked.

```python
try:
    return a / b
except ZeroDivisionError:
    return None
```
Don't write `except X as e:` if `e` is unused — `ruff` will flag it.

### Context managers (`with`)
Python's `try-with-resources`. Guarantees cleanup even if an exception happens mid-block — not just less typing.

```python
with open("data.txt") as f:
    contents = f.read()
# file auto-closed here, even on exception
```

### Environments & packages
| Java (Maven) | Python |
|---|---|
| `pom.xml` | `pyproject.toml` |
| resolved dependency tree | lockfile (`uv.lock`) |
| isolated build classpath | virtual environment (`.venv`, activated or via `uv run`) |

```bash
uv init myproject     # scaffold
uv add requests       # add dependency
uv run main.py        # run inside isolated env, no manual activation
uv sync               # install exact locked versions (reproducible across machines)
```
Lockfile pins the **entire transitive tree** — stronger guarantee than a plain `requirements.txt`, which often only pins direct dependencies.

---

## Module 2: Professional Project Structure

### Layout
```
myproject/
├── pyproject.toml
├── src/myproject/
│   ├── __init__.py     # marks folder as a package
│   └── cache.py
└── tests/
    └── test_cache.py
```
Import pattern: `from myproject.cache import Cache` (package.module → name, read right to left like a Java package path).

### pyproject.toml (≈ pom.xml)
```toml
[project]
name = "myproject"
dependencies = ["requests>=2.31"]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
```
`uv add <pkg>` updates both `pyproject.toml` (dependency list) and `uv.lock` (exact resolved version, including transitive deps).

### pytest
```python
def test_put_then_get():
    cache = Cache(capacity=10)
    cache.put("x", 5)
    assert cache.get("x") == 5   # == for values, NOT is
```
**Gotcha:** `is` = identity, `==` = equality — the *inverse* of Java's `==`/`.equals()`. Small ints (-5 to 256) are cached by CPython, so `is` can pass by accident on toy examples. Only use `is` for `None` checks.

### Dev tooling
```bash
uv add --dev ruff mypy pytest pre-commit   # --dev = build-time only, never shipped
uv run ruff check .      # lint
uv run ruff format .     # format
uv run mypy src/         # type-check — catches mismatches at the call site, pre-runtime
uv run pytest            # test
uv run pre-commit install   # wires checks into git commit hook
```

### Docker (layer-cache order matters)
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev   # deps layer, cached
COPY src/ ./src/                                    # code layer, changes often
CMD ["uv", "run", "python", "-m", "myproject"]
```

### CI (GitHub Actions) — same shape as any Java pipeline
install deps → lint (`ruff`) → type-check (`mypy`) → test (`pytest`) → build image

### Logging
```python
import logging
logger = logging.getLogger(__name__)
logger.info("cache_evict", extra={"key": key})   # structured fields, not string concat
```

### Config (≈ Spring @ConfigurationProperties)
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_host: str = "localhost"
    redis_port: int = 6379
    model_config = {"env_prefix": "APP_"}

settings = Settings()   # reads APP_REDIS_HOST etc. from env, validated + typed
```

---

## Module 3: Just Enough ML

### What a model is
A file with learned numbers (**weights**) + a known **architecture** to plug them into. Not magic — a big parameterized function. Training finds good weights (slow, GPU, rare); inference runs the function on new input (fast, is 100% of "serving").

### Tensors / numpy
```python
x = np.array([1.0, 2.0, 3.0])         # shape (3,)
x * weights      # element-wise, same shape in/out
x @ weights      # matrix multiply / dot product — shared dimension DISAPPEARS
np.outer(x, weights)   # all-pairs product → bigger shape, e.g. (3,3)
```
- `()` = scalar (0-D). `(0,)` = empty 1-D array. **Not the same thing.**
- Batch shape `(batch_size, num_features) @ (num_features, num_outputs) → (batch_size, num_outputs)`.
- First axis of a batch = **which sample** (independent requests, e.g. stacked API calls). Other axes = **values about one sample**. This is the literal mechanism behind request batching in serving.

### Training vs. inference
| | Training (`.fit()`) | Inference (`.predict()`) |
|---|---|---|
| Speed | slow, GPU-heavy | fast (ms) |
| Frequency | rare, offline | every request |
| Runs in serving API? | **Never** | **Always** |

### Model file formats
| Format | Notes |
|---|---|
| `pickle` | Python-native. **Avoid in prod** — can execute arbitrary code on load, breaks across versions |
| `ONNX` | Portable, framework-agnostic — export from PyTorch, serve anywhere |
| `safetensors` | PyTorch-native, data-only (no code execution) — safer than pickle |
| `TorchScript` | PyTorch-native, optimized for PyTorch's own runtime |

### Tiny hands-on model
```python
from sklearn.linear_model import LinearRegression
model = LinearRegression()
model.fit(X, y)              # training — finds model.coef_ (the weight)
model.predict([[5]])         # inference — the forward pass
```

### MLflow (model registry ≈ Nexus/Artifactory for models)
```python
mlflow.sklearn.log_model(model, "my-model")
mlflow.sklearn.load_model("models:/my-model/production")
```

---

## Module 4: ML Serving Stack

### FastAPI (≈ Spring Boot)
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class PredictRequest(BaseModel):
    features: list[float]

@app.post("/predict")
async def predict(request: PredictRequest) -> PredictResponse:
    ...
```
- pydantic validates automatically from type hints → `422` before handler runs, no `@Valid` needed.
- `async def` when the handler `await`s I/O (Redis/DB/network). Plain `def` for pure CPU work — FastAPI runs it in a thread pool, so it still doesn't block the server either way.

### Model servers (pick based on trade-off, not "correct" answer)
| Server | Best for |
|---|---|
| TorchServe | PyTorch default, battle-tested |
| Triton | Framework-agnostic, max GPU batching/throughput |
| BentoML | FastAPI + ML batteries, gentler curve |
| Ray Serve | Cluster-native, closest to general distributed tooling |

### Redis caching
```python
def cache_key(features, model_version: str) -> str:
    return f"pred:{model_version}:" + hashlib.sha256(json.dumps(features).encode()).hexdigest()
```
**Always version the cache key with the model.** Redeploy → key changes → old entries unreachable → zero stale responses. Stronger than TTL alone.

### Kafka
- **Async/batch inference**: producer → consumer scores (often batched) → result topic. Natural `async def`.
- **Streaming feature pipelines**: features computed continuously from events, written to a feature store ahead of request time.
- **Sync API vs. async Kafka — decided by**: is a caller *blocked waiting* on this request's answer? (Not by volume.)

### Vector DBs
`query(embedding, top_k=5)` = approximate nearest-neighbor search (vs. Redis `GET key` = exact match). Backbone of RAG.

### Feature stores (e.g., Feast)
Shared source of truth so training and serving compute features identically. Without one → **training-serving skew**: silent accuracy loss, no errors, no crash.

### Observability
Standard Prometheus/Grafana (latency/errors) stays green during skew/drift — infra health and prediction correctness are orthogonal. Need a second layer: track input/output distributions over time, compare to training distribution, alert on divergence.

### Scaling
K8s is the same tool. ML-specific: GPU scheduling (often whole-GPU-per-pod), cold starts (large models take seconds–minutes to load), sharper keep-warm-vs-cost trade-off (like Lambda cold starts, bigger cost per unit).

---

## Module 5: Capstone Project

### Build log / real bugs hit and fixed
1. `getModel()` → Java-style camelCase habit. Python = `snake_case` everywhere; `ruff` enforces it.
2. Untrained module-level global `model` — nothing guaranteed training ran before serving. Fixed with a single `@lru_cache`-decorated `get_model()` that trains *and* returns in one step — trains once, cached forever after.
3. Caching logic placed inside `predict()` in `model.py` — wrong layer. Pure ML logic (`model.py`) should never import/know about Redis. Caching belongs in the API layer (`main.py`) or a dedicated module (`redis_cache.py`).
4. **The big one:** `async def` does not make code non-blocking by itself — it only allows `await` inside. Using the *synchronous* `redis.Redis` client with no `await` inside an `async def` handler blocks FastAPI's entire event loop for every concurrent request, not just the current one. Worse than plain `def` (which FastAPI auto-threadpools). Real fix: `redis.asyncio.Redis` + actually `await` every I/O call, both in the function definition *and* at every call site.
5. Calling an `async def` function without `await` doesn't run it — creates an unused coroutine object, Python warns "coroutine was never awaited," and the intended side effect (e.g. a cache write) silently never happens.
6. Order matters for caching: check cache first, only pay for `get_model()`/compute on a miss — don't do the expensive work before you know you need it.

### Final structure
```
src/ml_serving_capstone/
├── model.py        # pure ML: get_model() [cached+trained], predict(), evaluate_model() — no I/O, no Redis
├── redis_cache.py  # all Redis I/O: cache_key() [sync, pure hash], cache_prediction()/get_cached_prediction() [async]
└── main.py         # FastAPI app — orchestrates: check cache → get_model+predict on miss → write cache → respond
```

### Key pattern: versioned async cache-aside
```python
@app.post("/predict", response_model=PredictResponse)
async def predict_endpoint(request: PredictRequest):
    cached = await redis_cache.get_cached_prediction(request.input_data)
    if cached is not None:
        return PredictResponse(predictions=cached)
    model = get_model()
    X_new = np.array(request.input_data).reshape(-1, 1)
    predictions = predict(model, X_new)
    await redis_cache.cache_prediction(request.input_data, predictions.tolist())
    return PredictResponse(predictions=predictions.tolist())
```

### Kafka worker (async/batch scoring)
Reuses `model.py`'s pure functions unchanged — same `get_model()`/`predict()`, different entry point. Deliberately does **not** go through the Redis cache: batch/streaming inputs are usually unique, so caching there would be all cost (mandatory round-trip), ~0% hit rate.
```python
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from model import get_model, predict

async def run_worker() -> None:
    consumer = AIOKafkaConsumer("inference-requests", bootstrap_servers="localhost:9092", group_id="ml-serving-capstone")
    producer = AIOKafkaProducer(bootstrap_servers="localhost:9092")
    await consumer.start(); await producer.start()
    try:
        async for msg in consumer:
            request = json.loads(msg.value)
            X_new = np.array(request["input_data"]).reshape(-1, 1)
            prediction = predict(get_model(), X_new).tolist()
            await producer.send_and_wait("inference-results", json.dumps({"id": request["id"], "predictions": prediction}).encode())
    finally:
        await consumer.stop(); await producer.stop()
```

### Tests
`tests/test_model.py` imports from the installed package, not a bare filename — `from ml_serving_capstone.model import get_model, predict, evaluate_model` (this is the `src/` layout rule from Module 2 applied for real; `from model import ...` fails with `ModuleNotFoundError`).
```python
import pytest
from ml_serving_capstone.model import get_model, predict

def test_get_model_returns_trained_model():
    assert get_model().coef_[0] == pytest.approx(2.0, abs=0.01)

def test_predict_matches_expected_pattern():
    result = predict(get_model(), np.array([[5]]))
    assert result[0] == pytest.approx(10.0, abs=0.1)
```

### Dockerfile (capstone version)
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev
COPY src/ ./src/
CMD ["uv", "run", "uvicorn", "ml_serving_capstone.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
`ml_serving_capstone.main:app` = dotted package path, same convention as the test import fix above.

### CI (capstone version)
Same shape as Module 2's CI — `uv sync` → `ruff check .` → `mypy src/` → `pytest`.

### mypy + untyped third-party libraries
`sklearn`/`aiokafka` ship no type stubs — not a bug in your code, mypy just can't see inside them. Scope an exception instead of disabling mypy wholesale:
```toml
[[tool.mypy.overrides]]
module = ["sklearn.*", "aiokafka.*"]
ignore_missing_imports = true
```

### `requires-python` and syntax support
`X | None` (PEP 604) only works natively at runtime from Python 3.10+. On 3.9 it needs `from __future__ import annotations`. Fix at the source — bump `requires-python = ">=3.10"` in `pyproject.toml` — rather than patching every file.

### Status: Complete!
- Basic metrics/logging (structured logging + Prometheus) — **Completed!**
- Platform deployment, dual namespaces, declarative Kafka topics, Kafka UI, Grafana dashboards, and Splunk Fluent Bit — **Completed!**

---

## Module 6 & 7: Kubernetes Runtime, GitOps & Platform Architecture

### Dual-Namespace Architecture & Cross-Namespace DNS
In Kubernetes, isolating shared platform infrastructure (`ml-infra`) from workloads (`ml-app`) prevents tenant collisions and enables resource reuse.
- Intra-namespace: `curl http://redis-service:6379`
- Inter-namespace: `curl http://redis-service.ml-infra:6379` (or `service.namespace.svc.cluster.local`)

### Declarative Kafka Topics
Manual topic creation via CLI commands (`kafka-topics.sh --create`) is an anti-pattern. Instead, package a Kubernetes `Job` inside the Helm chart:
1. `initContainers` polls Kafka broker readiness (`kafka-broker-api-versions.sh`).
2. Main container runs idempotent `kafka-topics.sh --create --if-not-exists --topic <name> --partitions 3`.

### Prometheus FastAPI Instrumentation
```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="ML Serving Capstone API")
Instrumentator().instrument(app).expose(app)
```
Exposes `/metrics` conforming to Prometheus exposition format with standard HTTP request metrics, latency buckets, and Python process counters.

### Prometheus Pod Scrape Annotations
In Helm pod template:
```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/path: "/metrics"
  prometheus.io/port: "8000"
```

### Key Endpoint Contracts
| Service | Access Type | Port | URL |
|---|---|---|---|
| **FastAPI ML Serving** | Port-Forward / Service | `8001` (host) / `80` (cluster) | `http://localhost:8001/docs` |
| **Kafka UI Dashboard** | NodePort | `30880` | `http://localhost:30880` |
| **Grafana Dashboards** | NodePort | `30300` | `http://localhost:30300` (`admin`/`admin`) |
| **ArgoCD GitOps** | NodePort | `30781` | `https://localhost:30781` |
| **Splunk Web UI** | Docker Host Port | `8000` | `http://localhost:8000` |
| **Splunk HEC** | Docker Host Port | `8088` | `https://localhost:8088` |
