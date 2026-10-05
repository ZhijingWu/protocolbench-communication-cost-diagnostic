"""Empirical profiles with explicit real versus conversion-only boundaries."""
import asyncio
import importlib.metadata
import json
import math
import statistics
import time
import uuid
from .io_utils import PROTOCOLS, REPO, original_converters

RAW_FIELDS = ["mode", "protocol", "payload_size_bytes", "phase", "repetition",
              "latency_ms", "conversion_runtime_ms", "encoded_bytes", "success",
              "error_type", "error_message", "stage", "measurement_kind"]
STAT_FIELDS = ["mode", "protocol", "payload_size_bytes", "measurement_kind",
               "measured_attempts", "success_count", "failure_rate", "mean_latency_ms",
               "median_latency_ms", "p95_latency_ms", "mean_conversion_runtime_ms",
               "median_conversion_runtime_ms", "p95_conversion_runtime_ms",
               "mean_encoded_bytes"]


def payload(size, token="topology-profile-fixed"):
    if size < len(token):
        raise ValueError("Payload too small for acknowledgement token")
    return {"text": token + "x" * (size - len(token))}


def percentile(values, q):
    if not values:
        return None
    values = sorted(values)
    index = (len(values) - 1) * q
    lo, hi = math.floor(index), math.ceil(index)
    return values[lo] + (values[hi] - values[lo]) * (index - lo)


def summarize(rows):
    output = []
    keys = sorted({(r["mode"], r["protocol"], r["payload_size_bytes"]) for r in rows})
    for mode, protocol, size in keys:
        measured = [r for r in rows if (r["mode"], r["protocol"], r["payload_size_bytes"]) ==
                    (mode, protocol, size) and r["phase"] == "measured"]
        good = [r for r in measured if r["success"]]
        record = {"mode": mode, "protocol": protocol, "payload_size_bytes": size,
                  "measurement_kind": "request_timer" if mode == "real" else "conversion_serialization",
                  "measured_attempts": len(measured), "success_count": len(good),
                  "failure_rate": 1 - len(good) / len(measured) if measured else None,
                  "mean_encoded_bytes": statistics.mean([r["encoded_bytes"] for r in good]) if good else None}
        for field in ("latency_ms", "conversion_runtime_ms"):
            values = [r[field] for r in good if r[field] is not None]
            record.update({"mean_" + field: statistics.mean(values) if values else None,
                           "median_" + field: statistics.median(values) if values else None,
                           "p95_" + field: percentile(values, .95)})
        output.append(record)
    return output


def empty_row(mode, protocol, size, phase, repetition):
    return dict(mode=mode, protocol=protocol, payload_size_bytes=size, phase=phase,
                repetition=repetition, latency_ms=None, conversion_runtime_ms=None,
                encoded_bytes=None, success=False, error_type="", error_message="",
                stage="", measurement_kind="request_timer" if mode == "real" else "conversion_serialization")


def conversion_sample(protocol, size):
    UTE, encoders = original_converters()
    # Fixed original UTE instance separates deterministic sizes from UUID/time noise.
    envelope = UTE(id="00000000-0000-0000-0000-000000000000", src="profile-source",
                   dst="profile-destination", timestamp=1700000000.0,
                   content=payload(size), context={}, metadata={})
    start = time.perf_counter_ns()
    encoded = encoders[protocol.lower()](envelope)
    size_bytes = len(json.dumps(encoded).encode("utf-8"))  # EXACT BaseAgent byte metric definition
    duration_ms = (time.perf_counter_ns() - start) / 1e6
    return duration_ms, size_bytes


def _metric_value(metric, labels, suffix):
    values = [sample.value for family in metric.collect() for sample in family.samples
              if sample.name.endswith(suffix) and sample.labels == labels]
    return sum(values)


def _contains_token(value, token):
    if isinstance(value, str):
        return token in value
    if isinstance(value, dict):
        return any(_contains_token(v, token) for v in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_token(v, token) for v in value)
    return False


def _has_failure(value):
    if isinstance(value, str):
        return any(marker in value.lower() for marker in ("[agora fallback]", "[agora error]"))
    if isinstance(value, dict):
        if value.get("error") or value.get("status") in ("failed", "error") or value.get("type") == "error":
            return True
        return any(_has_failure(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return any(_has_failure(v) for v in value)
    return False


class RealSession:
    """Uses running ORIGINAL protocol servers via unchanged real client adapters.

    Endpoint config supplies url, receiver_id and ANP target_did as appropriate.
    Receiver must echo the unique topology-profile-* token (no LLM inference needed).
    The profiler never creates a mock server or accepts adapter fallback strings.
    """
    def __init__(self, protocol, endpoint, timeout):
        self.protocol, self.endpoint, self.timeout = protocol, endpoint, timeout
        self.agent = self.client = self.adapter = None
        self.dst = (endpoint or {}).get("receiver_id", "profile-destination")

    async def open(self):
        import sys
        sys.path.insert(0, str(REPO))
        # Import first to expose actual dependency blockers rather than hide them
        # behind missing endpoint configuration. Import has no SDK stand-in.
        import httpx
        from src.core.base_agent import BaseAgent
        from src.core.metrics import REQUEST_LATENCY, MSG_BYTES
        self.latency_metric, self.bytes_metric = REQUEST_LATENCY, MSG_BYTES
        if not self.endpoint or not self.endpoint.get("url"):
            raise ValueError(f"Configure real_endpoints.{self.protocol}.url for a running repository server")
        self.client = httpx.AsyncClient(timeout=self.timeout)
        self.agent = BaseAgent("profile-source", httpx_client=self.client)
        url = self.endpoint["url"]
        if self.protocol == "A2A":
            from src.agent_adapters.a2a_adapter import A2AAdapter
            self.adapter = A2AAdapter(httpx_client=self.client, base_url=url)
        elif self.protocol == "ACP":
            from src.agent_adapters.acp_adapter import ACPAdapter
            self.adapter = ACPAdapter(httpx_client=self.client, base_url=url, agent_id=self.dst)
        elif self.protocol == "Agora":
            from src.agent_adapters.agora_adapter import AgoraClientAdapter
            self.adapter = AgoraClientAdapter(toolformer=None, target_url=url,
                                              httpx_client=self.client, agent_id=self.dst)
        elif self.protocol == "ANP":
            from src.agent_adapters.anp_adapter import ANPAdapter
            if not self.endpoint.get("target_did"):
                raise ValueError("ANP real endpoint requires a valid target_did")
            self.adapter = ANPAdapter(httpx_client=self.client,
                                      target_did=self.endpoint["target_did"],
                                      target_http_base_url=url, host_domain="127.0.0.1",
                                      host_port=str(BaseAgent._find_free_port()))
        else:
            raise ValueError(self.protocol)
        await asyncio.wait_for(self.adapter.initialize(), self.timeout)
        self.agent.add_outbound_adapter(self.dst, self.adapter)
        # Same client-only lifecycle as existing BaseAgent.from_a2a/from_ap/from_anp;
        # no receiver is mocked or replaced. This agent has no inbound server.
        self.agent._initialized = True

    async def sample(self, size):
        labels = {"src": "profile-source", "dst": self.dst, "protocol": self.protocol.lower()}
        byte_labels = {"direction": "out", "agent_id": "profile-source"}
        before_sum = _metric_value(self.latency_metric, labels, "_sum")
        before_count = _metric_value(self.latency_metric, labels, "_count")
        before_bytes = _metric_value(self.bytes_metric, byte_labels, "_total")
        token = "topology-profile-" + uuid.uuid4().hex
        error = None
        try:
            response = await asyncio.wait_for(self.agent.send(self.dst, payload(size, token)), self.timeout)
            if _has_failure(response) or not _contains_token(response, token):
                raise ValueError("Receiver acknowledgement missing or adapter returned fallback/error")
        except Exception as exc:
            error = exc
        after_count = _metric_value(self.latency_metric, labels, "_count")
        latency = ((_metric_value(self.latency_metric, labels, "_sum") - before_sum) * 1000
                   if after_count - before_count == 1 else None)
        encoded_bytes = _metric_value(self.bytes_metric, byte_labels, "_total") - before_bytes
        if error is None and (latency is None or encoded_bytes <= 0):
            error = RuntimeError("Missing per-request original metrics; reject unmeasured success")
        return latency, int(encoded_bytes) if encoded_bytes > 0 else None, error

    async def close(self):
        try:
            if self.agent:
                await self.agent.stop()
            elif self.adapter:
                await self.adapter.cleanup()
        finally:
            if self.client:
                await self.client.aclose()


async def profile(config, mode):
    if mode not in ("real", "conversion-only"):
        raise ValueError("Mode must be real or conversion-only")
    warmup, repeats = int(config["warmup"]), int(config["measured_repetitions"])
    if warmup < 0 or repeats < 1:
        raise ValueError("Require nonnegative warmup and at least one measured repetition")
    rows, blockers = [], []
    for protocol in PROTOCOLS:
        session, setup_error = None, None
        if mode == "real":
            session = RealSession(protocol, config.get("real_endpoints", {}).get(protocol),
                                  config.get("timeout_seconds", 30))
            try:
                await session.open()
            except Exception as exc:
                setup_error = exc
                blockers.append({"protocol": protocol, "error_type": type(exc).__name__, "message": str(exc)})
        try:
            for size in config["payload_size_bytes"]:
                if not isinstance(size, int) or size <= 0:
                    raise ValueError("Payload sizes must be positive integer bytes")
                for phase, count in (("warmup", warmup), ("measured", repeats)):
                    for repetition in range(count):
                        row = empty_row(mode, protocol, size, phase, repetition)
                        try:
                            if setup_error:
                                row["stage"] = "setup_blocked_not_sent"
                                raise setup_error
                            if mode == "conversion-only":
                                row["stage"] = "conversion_serialization"
                                row["conversion_runtime_ms"], row["encoded_bytes"] = conversion_sample(protocol, size)
                            else:
                                row["stage"] = "request"
                                row["latency_ms"], row["encoded_bytes"], error = await session.sample(size)
                                if error:
                                    raise error
                            row["success"] = True
                        except Exception as exc:
                            row["error_type"], row["error_message"] = type(exc).__name__, str(exc)
                        rows.append(row)
        finally:
            if session:
                try:
                    await session.close()
                except Exception as exc:
                    blockers.append({"protocol": protocol, "stage": "cleanup",
                                     "error_type": type(exc).__name__, "message": str(exc)})
    return rows, summarize(rows), blockers


def dependency_versions():
    names = ["a2a-sdk", "acp-sdk", "agora-protocol", "agent-connect", "uvicorn", "httpx",
             "prometheus-client", "psutil", "pynvml", "PyYAML", "pytest"]
    versions = {}
    for name in names:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return versions
