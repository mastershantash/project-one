# Python for Production ML Serving — Learning Path & Tracker

**Who this is for:** Shantanu — senior Java backend engineer (microservices, distributed systems, AWS, Kafka, Redis, performance work) learning Python to build/serve production ML systems.

**The goal:** Not "learn Python" in the abstract — learn Python and the ML-serving stack well enough to build the same kind of production-grade systems you already build in Java, just for ML workloads. Everywhere possible, new ideas are tied back to something you already know.

**How to use this file:** Each module has a checklist. As we cover something in chat, come back here and check it off and jot a one-line note under "Notes" if anything's worth remembering. The "Progress Tracker" at the top always tells us where to pick up next session.

---

## Progress Tracker

| Module | Status | Notes |
|---|---|---|
| 0. Roadmap agreed | ✅ Done | Chose "productionizing ML" track over "building/training models" track |
| 1. Python fast-track for Java engineers | ✅ Done (async deferred to Module 4) | Syntax, collections, comprehensions, type hints, classes/duck typing, error handling, context managers, venv/uv all solid |
| 2. Professional project structure | ✅ Done | src/ layout, pyproject.toml, pytest, ruff, mypy, pre-commit, Docker, CI, logging, pydantic-settings all covered |
| 3. Just enough ML to know what you're serving | ✅ Done | Weights/architecture, tensor shapes, training vs. inference, model formats, MLflow all covered |
| 4. ML serving stack (your home turf) | ✅ Done | FastAPI, async, model servers, Redis, Kafka, vector DBs, feature stores, drift monitoring, scaling all covered |
| 5. Capstone project | ✅ Done | Full working repo — FastAPI + versioned async Redis caching + Kafka consumer + pytest + Docker + CI + mypy/ruff all passing |
| 6. Cloud-Native GitOps & K8s Runtime | ✅ Done | MicroK8s v1.30, ArgoCD GitOps engine, Helm packaging, non-root hardened Docker builds, GitHub Actions CI/CD to GHCR |
| 7. Dual-Namespace Platform & Full Observability | ✅ Done | Platform namespace `ml-infra` & workload namespace `ml-app`, cross-namespace DNS, declarative Kafka topics, Kafka UI (30880), Prometheus + Grafana (30300), Splunk via Fluent Bit |

**Core roadmap (Modules 1–7) is complete.** 🎉

**Advanced Next Horizons (Pick whenever you want to explore):**
- Swap toy `LinearRegression` for a real pretrained model (e.g. HuggingFace text classifier or ONNX Runtime).
- Dedicated model servers (BentoML, Triton, vLLM) comparison.
- External Secrets Operator (ESO) syncing from HashiCorp Vault / Cloud Secret Managers.

**Related file:** `python-revision-sheet.md` — quick-lookup cheat sheet, updated alongside this tracker.

---

## Module 1: Python Fast-Track for Java Engineers

*Goal: stop translating in your head. Read and write Python at the speed you read Java.*

- [x] **Syntax shape** — no braces, no semicolons; indentation *is* the block structure. This trips people up for about a day, then never again.
- [x] **Core collections** — `list` (≈ `ArrayList`), `dict` (≈ `HashMap`), `tuple` (immutable, no Java equivalent really — think a fixed-size record), `set` (≈ `HashSet`).
- [x] **Functions as values / list comprehensions** — `[expr for item in iterable]` replaces most `.stream().map()` chains. Key gotcha learned: comprehensions transform each item independently — no running-total/accumulator behavior like a loop has.
- [x] **Type hints** — Python is dynamically typed by default, but `mypy`/type hints give you back Java-style safety (`def foo(x: int) -> str:`). Non-negotiable for "professional" code — treat it like Java's compiler check.
- [x] **Classes & duck typing** — Python has classes but no `interface` keyword; it uses "duck typing" (if it has the right methods, it works) or `Protocol`/`ABC` when you want something closer to a Java interface. `self` is explicit; `__init__` is the constructor; `.pop(key, None)` is the idiomatic safe-delete.
- [x] **Error handling** — `try`/`except`/`finally` maps almost 1:1 to Java's `try`/`catch`/`finally`. No checked-vs-unchecked distinction. Don't capture `as e` if unused — `ruff` will flag it.
- [x] **Context managers** — the `with` statement is Python's `try-with-resources`; guarantees cleanup even if an exception is raised mid-block, not just "less typing."
- [ ] **Async** — `asyncio`/`async def`/`await` is Python's answer to Java's `CompletableFuture` / reactive streams. **Deferred to Module 4**, where it's actually needed for the serving stack.
- [x] **Virtual environments** — every project gets an isolated Python + dependency set, similar in spirit to how a Maven/Gradle build isolates a classpath, except you activate it explicitly (`venv`, or better, `uv`).
- [x] **Package management** — `pip` is the base tool; `uv` is the modern equivalent of Maven/Gradle (`uv init`, `uv add`, `uv run`, `uv sync`). Lockfiles pin the *entire* transitive dependency tree — stronger guarantee than a plain `requirements.txt`.

**You'll know you've got this when:** you can read an unfamiliar Python file and mentally map every line to "this is basically X in Java" without me explaining it.

---

## Module 2: Professional Project Structure

*Goal: the difference between "a folder of scripts" and something you'd actually deploy.*

- [x] **`src/` layout** — Python's version of a clean package layout (`src/myproject/...`) instead of dumping files in the repo root. Prevents import bugs that only show up later. `__init__.py` marks a folder as an importable package.
- [x] **`pyproject.toml`** — the modern Python equivalent of `pom.xml` / `build.gradle`: declares dependencies, build config, tool settings, all in one file.
- [x] **Dependency locking** — `uv.lock` pins exact versions of the *entire transitive tree*, like a Maven dependency tree resolved and frozen — for reproducible builds across machines. `uv add <pkg>` updates both `pyproject.toml` and the lockfile.
- [x] **Testing — `pytest`** — your JUnit. Files `test_*.py`, functions `test_*`, plain `assert` (no `assertEquals`). Gotcha caught live: use `==` for value equality, not `is` (Python's `==`/`is` are the *inverse* of Java's `.equals()`/`==`).
- [x] **Linting & formatting — `ruff`** — your Checkstyle/Spotless in one faster tool, mostly auto-fixing. Added as `--dev` dependency (build-time only, never shipped).
- [x] **Type checking — `mypy`** — runs type hints through a checker at build time, closest thing Python has to "the compiler caught this," moving failures from deep-in-a-call-stack-at-runtime to the exact call site before running anything.
- [x] **Pre-commit hooks** — run lint/format/type-check before every commit via `.pre-commit-config.yaml` + `pre-commit install`, same idea as a fast local CI gate.
- [x] **Docker packaging** — copy `pyproject.toml`/`uv.lock` and `uv sync --frozen --no-dev` *before* copying source code, for layer-cache efficiency. Same instinct as not shipping test deps in a final JAR.
- [x] **CI/CD — GitHub Actions** — install → lint → type-check → test, same pipeline shape as any Java CI you've built, Python tools slotted in.
- [x] **Logging** — Python's `logging` module (or `structlog`), playing JLogger/SLF4J's role. Log structured fields via `extra={...}`, not string concatenation.
- [x] **Config management — `pydantic-settings`** — typed, validated config loaded from env vars, direct cousin of Spring's `@ConfigurationProperties`.

**You'll know you've got this when:** you can scaffold a new Python service from scratch — proper layout, tests, lint, Docker, CI — without looking anything up.

---

## Module 3: Just Enough ML to Know What You're Serving

*Goal: not becoming a data scientist — just understanding what's inside the box you're going to serve. This is intentionally the shortest module.*

- [x] **What a "model" actually is** — a file containing learned numbers (weights) + a known architecture to plug them into. Not magic — just a big function.
- [x] **Tensors / arrays — `numpy` basics** — multi-dimensional arrays with fast math. Key distinctions learned: `*` is element-wise (same shape in/out), `@`/`np.dot` is matrix multiply (shared dimension disappears), `np.outer` is the "all pairs" operation. Shape `()` = scalar, shape `(0,)` = empty 1-D array — not the same thing. First axis of a batch = which sample (independent requests); other axes = values about that one sample — directly maps to how request batching works in serving.
- [ ] **`pandas` basics** — for wrangling tabular data; roughly "SQL-ish DataFrame operations in-process." *(deferred — not hit yet, revisit if a serving task needs tabular feature wrangling)*
- [x] **Training vs. inference** — training (`.fit()`) produces the weights (slow, GPU-heavy, happens rarely, never runs inside a serving API); inference (`.predict()`/forward pass) uses the weights to answer a request (fast, is 100% of what serving means).
- [x] **Common model file formats** — `pickle` (Python-native, avoid in production — can execute arbitrary code on load, breaks across versions), `ONNX` (portable, cross-framework), `TorchScript`/`safetensors` (PyTorch-native, `safetensors` is data-only/safer than pickle).
- [x] **One tiny hands-on model** — ran a `scikit-learn` `LinearRegression`: `model.coef_` is the learned weight, `model.predict()` is inference/forward pass — same two steps as any larger model.
- [x] **Model registries — MLflow** — versioned storage for trained models (`log_model`/`load_model`), playing the role your artifact repo (Nexus/Artifactory) plays for JARs, plus tracks metrics per version to compare before promoting.

**You'll know you've got this when:** given a model file and its docs, you know what format it's in, how to load it, and what "running inference" means without hand-waving.

---

## Module 4: ML Serving Stack — Your Home Turf

*Goal: this is where your distributed-systems experience directly transfers. Most of this is "systems you already know, aimed at a new kind of workload."*

- [x] **FastAPI** — Spring Boot analogue: `@app.post` ≈ `@PostMapping`, pydantic models ≈ `@RequestBody` DTO + Bean Validation but automatic (422 before handler runs, not opt-in). `uvicorn` ≈ Tomcat underneath.
- [x] **Async in FastAPI** — `async def` for handlers that `await` I/O (Redis, DB, network); plain `def` for pure CPU work — FastAPI runs `def` handlers in a thread pool automatically, so either way the server isn't blocked.
- [x] **Dedicated model servers** — TorchServe (PyTorch default), Triton (framework-agnostic, max GPU throughput), BentoML (FastAPI + ML batteries, gentler curve), Ray Serve (cluster-native, closest to general distributed-systems tooling). Decision is a trade-off, not a single correct answer — same as picking a broker or service mesh.
- [x] **Batching** — grouping requests into the batch axis (tie-back to Module 3 tensor shapes) for GPU throughput.
- [x] **Caching — Redis** — result caching (hash of input → prediction) and feature caching (precomputed expensive values). Key lesson: **always include model version in the cache key** — redeploys auto-invalidate old entries with zero stale responses, cleaner than relying on TTL alone or stale-while-revalidate.
- [x] **Streaming — Kafka** — async/batch inference (producer → consumer scores → result topic, naturally `async def`) and streaming feature pipelines (features computed continuously, written to a feature store before request time). Deciding factor between sync API vs. async Kafka pipeline is **whether a caller is blocked waiting**, not raw volume.
- [x] **Vector databases** (Pinecone, Weaviate, pgvector) — approximate nearest-neighbor search over embeddings (vs. Redis's exact-match `GET`), backbone of RAG.
- [x] **Feature stores** (e.g., Feast) — shared source of truth for model inputs so training and serving compute features identically. Without one: **training-serving skew** — silent accuracy degradation, no errors, no crash.
- [x] **Observability** — standard Prometheus/Grafana (latency/errors) stays all-green during skew or drift, because the model runs fine and returns a fast, valid-shaped, just-wrong answer. Needs a *second*, ML-specific monitoring layer (input/output distribution tracking, eventual ground-truth comparison) — infra health and prediction correctness are orthogonal signals.
- [x] **Scaling** — Kubernetes is the same tool; ML-specific wrinkles are GPU scheduling (often whole-GPU-per-pod, not fractional), cold starts (large models take seconds-minutes to load into GPU memory), and a sharper keep-warm-vs-cost trade-off than typical stateless services (same shape as Lambda cold starts, bigger cost per unit).

**You'll know you've got this when:** you can sketch an architecture diagram for "serve this model at scale" using the same instincts you'd use for any distributed system, correctly substituting the ML-specific pieces.

---

## Module 5: Capstone Project

*Goal: put it all together in one small but "real" system.*

- [x] Picked the Module 3 `LinearRegression` toy model — deliberately simple, so focus stayed on serving architecture, not model complexity.
- [x] Wrapped it in a FastAPI service, structured per Module 2 (`src/` layout, tests, types, lint) — repo: `~/code/Tinkering/ml-serving-capstone`.
- [x] Added Redis caching for repeated predictions, **with model version baked into the cache key** (Module 4's lesson, applied for real).
- [x] Added a Kafka consumer for async/batch scoring requests, reusing the same pure `model.py` functions as the FastAPI path.
- [x] Containerized with Docker (deps layer cached separately from code).
- [x] Wired up CI (ruff, mypy, pytest) via GitHub Actions.
- [ ] Basic metrics/logging — not yet added, good candidate for a follow-up session.

**You'll know you're done when:** you could hand this repo to another backend engineer and they'd recognize it as a "real service," not a notebook exported to `.py`.

---

## Session Log

*(Add a dated entry each time we make progress, so we can pick the thread back up quickly.)*

- **2026-09-20** — Roadmap agreed. Chose the "productionizing ML" track (serving/infra) over "building/training models." Created this tracker.
- **2026-09-20** — Completed Module 1 (Python fast-track), minus async (deferred to Module 4). Worked through hands-on checks for collections, list comprehensions, type hints, classes, error handling, context managers, and `uv`/venv — all solid on first or second try.
- **2026-09-21** — Completed Module 2 (professional project structure): layout, pyproject.toml, pytest (caught a real `is` vs `==` bug live), ruff, mypy, pre-commit, Docker, CI, logging, config. Created `python-revision-sheet.md` as a running cheat sheet alongside this tracker.
- **2026-09-22** — Completed Module 3 (just enough ML): tensor shapes and matrix-multiply semantics (ran hands-on numpy checks), training vs. inference, model file formats, one hands-on scikit-learn model, MLflow registry. `pandas` deliberately skipped for now — revisit if/when a serving task needs it.
- **2026-10-14** — Completed Module 4 (ML serving stack): FastAPI + async rules, model server trade-offs, Redis caching with versioned keys (own insight: stale-while-revalidate as an alternative, good instinct), Kafka sync-vs-async decision driver, vector DBs, feature stores / training-serving skew, drift monitoring as a second observability layer, GPU/scaling wrinkles. Also had a detour discussing Python vs. Spring AI for the stated serving/infra goal — stuck with Python.
- **2026-10-15 to 2026-10-19** — Built the Module 5 capstone end-to-end at `~/code/Tinkering/ml-serving-capstone`. Real bugs hit and fixed along the way (all logged in the revision sheet): camelCase habit, untrained-model race condition (fixed with `@lru_cache`), caching logic in the wrong architectural layer, the big one — `async def` doesn't make blocking code non-blocking by itself (needed `redis.asyncio` + real `await`), calling an async function without `await` silently no-ops, `src/` layout import path, and a `requires-python` version bump to fix a real `ruff` PEP 604 error. Finished with `ruff check` and `mypy` both clean and `pytest` passing. Core 5-module roadmap complete.


---

## Module 6: Cloud-Native Kubernetes Runtime & GitOps Engine

*Goal: Deploy the serving stack to a real Kubernetes environment declaratively without manual kubectl imperative commands.*

- [x] **MicroK8s v1.30 runtime** — local single-node production-compatible Kubernetes engine with native containerd CRI.
- [x] **Hardened container images** — Multi-stage build with Astral `uv`, non-root user (`appuser:1000`), layer caching, read-only root filesystems.
- [x] **Helm 3 Packaging** — Parameterized Kubernetes templates with `values.yaml`, ConfigMaps, Services, and Probes.
- [x] **ArgoCD GitOps Automation** — Continuous reconciliation loop pulling unidirectionally from GitHub (`main` branch) with automated self-healing.
- [x] **GitHub Actions CI/CD** — Automated pytest, ruff, Docker Buildx, and publishing to GitHub Container Registry (`ghcr.io`).

---

## Module 7: Platform Architecture, Dual Namespaces, & Full Observability

*Goal: Build an enterprise-grade, multi-tenant platform architecture separating shared infrastructure from applications, complete with metrics, dashboards, and declarative topology.*

- [x] **Dual-Namespace Architecture** — `ml-infra` (shared platform) and `ml-app` (workload).
- [x] **Cross-Namespace DNS Resolution** — Routing via `service.namespace` (`redis-service.ml-infra:6379` and `kafka-service.ml-infra:9092`).
- [x] **Declarative Kafka Topics** — Automated Kubernetes Job (`create-kafka-topics`) creating `inference-requests` and `inference-results` with 3 partitions and an init container waiting for Kafka readiness.
- [x] **Kafka UI Web Dashboard** — Deployed on NodePort `30880` (`http://localhost:30880`) for real-time partition, topic, and consumer lag inspection.
- [x] **FastAPI Prometheus Instrumentation** — Integrated `prometheus-fastapi-instrumentator` exposing `/metrics` with latency histograms, QPS, status codes, and garbage collection metrics.
- [x] **Prometheus Kubernetes SD** — Cross-namespace pod scraping via annotations (`prometheus.io/scrape: "true"`, `/metrics`, port 8000).
- [x] **Pre-Provisioned Grafana Dashboard** — Deployed on NodePort `30300` (`http://localhost:30300`) with auto-provisioned Prometheus data source and custom MLOps metrics dashboard (RPS, p95/p99 latency, predictions, memory RSS, CPU).
- [x] **Enterprise Logging via Pattern A** — Fluent Bit DaemonSet mounted to `/var/log/pods`, parsing JSON structured logs and streaming securely to Splunk HEC (Docker host port 8088).
- [x] **Kubernetes Secrets Management** — Isolating credentials (`splunk-hec-token`) into Kubernetes `Secret` resources, with architectural patterns for External Secrets Operator (ESO).
