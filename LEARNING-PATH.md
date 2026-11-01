# Python for Production ML Serving & GitOps — Learning Path & Tracker

**Who this is for:** Senior Java Backend / Distributed Systems Engineers learning Python, Cloud-Native Kubernetes, and GitOps to build and productionize high-throughput ML systems.

**The Curriculum Design:** Split cleanly into three parts:
- **Part I: The Application Layer** (Python 3.12, `uv`, `src/` layout, scikit-learn, async Redis, FastAPI, Kafka streaming worker, Ruff, Mypy, Pytest, Docker).
- **Part II: The Platform & GitOps Layer** (MicroK8s v1.30, Splunk HEC, Polyrepo pattern, Dual Namespaces, Helm charts, KRaft Kafka, Kafka UI, Prometheus, Grafana, ArgoCD).
- **Part III: Production Hardening, Zero-Dollar Stack & SRE** (Trivy CI scanning, Ingress-NGINX with rate limiting, NetworkPolicies, PodDisruptionBudgets, What Cannot Be Done For Free, 12 War Stories, Senior Interview Q&A).

---

## Master Progress Tracker

| Section | Topic | Status | Key Deliverable / Verification |
|---|---|---|---|
| **00** | Java ↔ Python Rosetta Stone | ✅ Complete | Mental model bridging JVM, Maven, Spring Boot, Netty, threads to asyncio & GIL |
| **PART I** | **The Application Layer** | | **Python Microservice & Hardened Container** |
| 01 | Toolchain & Environment Setup | ✅ Complete | Python 3.12, Astral `uv`, Git, standalone binary caching |
| 02 | Modern Project Scaffolding | ✅ Complete | Strict `src/` layout, package imports, directory tree |
| 03 | Modern Dependencies & Lockfiles | ✅ Complete | Declarative `pyproject.toml`, cryptographic `uv.lock`, `.venv` |
| 04 | The ML Model Serving Logic | ✅ Complete | `model.py`, scikit-learn, `@lru_cache` singleton weights |
| 05 | Asynchronous Redis Caching Layer | ✅ Complete | `redis_cache.py`, versioned MD5 keys, fail-open resilience, 1s timeouts |
| 06 | FastAPI Serving REST API | ✅ Complete | `main.py`, Pydantic v2 DTOs, `/healthz`, `/readyz`, `/predict`, JSON logging |
| 07 | Prometheus Instrumentation | ✅ Complete | `prometheus-fastapi-instrumentator`, OpenMetrics `/metrics` endpoint |
| 08 | Event-Driven Kafka Streaming Worker | ✅ Complete | `kafka_worker.py`, `aiokafka` consumer/producer loop, retry backoff |
| 09 | Static Analysis & Type Safety | ✅ Complete | `uv run ruff check --fix`, `uv run mypy src/`, zero warnings |
| 10 | Automated Pytest Suite | ✅ Complete | `tests/test_model.py`, `tests/test_api.py`, 6 passing tests |
| 11 | Production Multi-Stage Dockerfile | ✅ Complete | Non-root `UID 1000` (`appuser`), 3-step `uv` cache layers, `.dockerignore` |
| 12 | Local Verification Runbook | ✅ Complete | Bare-metal `uvicorn` and local Docker container cURL verification |
| **PART II** | **The Platform & GitOps Layer** | | **Cloud-Native Kubernetes & GitOps Platform** |
| 13 | Local Kubernetes Cluster (MicroK8s) | ✅ Complete | MicroK8s v1.30, user permissions, RBAC, CoreDNS, hostpath-storage |
| 14 | Splunk Enterprise & HEC Setup | ✅ Complete | Docker container, Web UI (8000), HEC port 8088, token auth |
| 15 | The Decoupled Polyrepo Pattern | ✅ Complete | `project-one` (App repo) & `project-one-gitops` (Platform repo) |
| 16 | Dual-Namespace Topology & DNS | ✅ Complete | `ml-infra` vs `ml-app`, blast-radius isolation, CoreDNS FQDN routing |
| 17 | Shared Platform Helm Chart | ✅ Complete | `helm/ml-infra` (Redis, KRaft Kafka, Kafka UI, Prometheus, Grafana, Fluent Bit) |
| 18 | Workload Serving Helm Chart | ✅ Complete | `helm/ml-app` (Deployment, ClusterIP, ConfigMap, HPA) |
| 19 | Declarative Topics & Kafka UI | ✅ Complete | Init-container TCP readiness polling, Kafka UI NodePort 30880 |
| 20 | ArgoCD GitOps Engine Setup | ✅ Complete | Server-Side Apply install (bypassing 262KB CRD limit), NodePort 30781 |
| 21 | Multi-App GitOps Manifests | ✅ Complete | `infra-app.yaml` & `workload-app.yaml`, automated sync, self-healing |
| **PART III**| **Production Hardening & SRE** | | **Enterprise SRE, Zero-Dollar Stack & Economics** |
| 22 | Enterprise CI/CD & GHCR Integration | ✅ Complete | GitHub Actions, Git SHA tagging (`sha-<commit>`), Trivy vulnerability scan |
| 23 | The Zero-Dollar Production Stack | ✅ Complete | Ingress rate-limiting, PodDisruptionBudget, NetworkPolicy isolation |
| 24 | The Hard Economic Limits | ✅ Complete | What CANNOT be done for free (Multi-AZ, Cloud LBs, Static IPs, Phone Alerts) |
| 25 | Cluster Runbook & Port Matrix | ✅ Complete | Consolidated endpoint matrix, smoke-test scripts, health checks |
| 26 | Production War Stories (12 Bugs) | ✅ Complete | In-depth root cause and fixes for all 12 production issues encountered |
| 27 | Senior Engineering Revision Q&A | ✅ Complete | 15 advanced interview questions bridging Java, MLOps, and Kubernetes |

---

## Conceptual Deep Dives

### 1. The Python GIL & High-Throughput Inference
In Java, 10,000 requests are handled across JVM OS threads or Virtual Threads. In Python, I/O is cooperative single-threaded (`asyncio`), but CPU-bound scikit-learn/NumPy matrix math **releases the Global Interpreter Lock (GIL)** to execute at bare-metal speeds in optimized C/Fortran (OpenBLAS/MKL).

### 2. Kafka KRaft Raft Quorum vs ZooKeeper
Apache Kafka 3.x+ eliminates ZooKeeper using the KRaft consensus protocol. Cluster metadata is committed directly to an internal, replicated partition (`@metadata`). A cold-start init-container barrier is mandatory to prevent topic provisioning jobs from crashing while the KRaft controller quorum elects an active leader.

### 3. Server-Side Apply vs ETCD 262KB Annotation Limit
Client-side `kubectl apply` serializes prior manifests into `kubectl.kubernetes.io/last-applied-configuration`. Large OpenAPI schemas (like ArgoCD CRDs) exceed ETCD's 256KB annotation limit. Server-Side Apply (`--server-side`) delegates merge logic to the Kubernetes API server using field-management metadata, bypassing annotation size ceilings.

### 4. CoreDNS Cross-Namespace FQDN Routing (`ndots:5`)
Kubernetes appends `ndots:5` in `/etc/resolv.conf`. Unqualified service names across namespaces waste up to 4 DNS query roundtrips with `NXDOMAIN` responses. Supplying the complete FQDN (`<service>.<namespace>.svc.cluster.local`) resolves queries on the initial packet.
