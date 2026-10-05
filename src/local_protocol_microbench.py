"""Local, real-server communication microbenchmark; no wire-format replacements."""
import asyncio
import hashlib
import ipaddress
import json
import math
import os
import re
import socket
import statistics
import sys
import time
import traceback
from pathlib import Path
from .io_utils import BASE, PROTOCOLS, REPO, output_path, write_json

RAW_FIELDS = ["protocol", "payload_size_bytes", "phase", "repetition", "latency_ms",
              "encoded_request_bytes", "success", "error_type", "error_message",
              "timing_source", "timing_sanity_passed", "wall_clock_start_ns", "wall_clock_end_ns",
              "original_request_metric_ms", "ute_encoded_bytes", "server_requests",
              "executor_calls", "transport_path"]
SETUP_FIELDS = ["protocol", "status", "setup_latency_ms", "server_url", "transport_path",
                "error_type", "error_message"]
STAT_FIELDS = ["protocol", "payload_size_bytes", "status", "requested_repetitions",
               "attempted_requests", "successful_requests", "failures", "skipped_requests",
               "mean_latency_ms", "median_latency_ms", "p95_latency_ms", "std_latency_ms",
               "mean_encoded_request_bytes", "setup_latency_ms", "transport_path", "timing_source"]
PROBE = re.compile(r"topology-profile-[a-z0-9]+-[0-9]+-[wm]-[0-9]+x*")


def monotonic_ms(start, end):
    if end <= start:
        raise RuntimeError("Nonpositive wall-clock send interval")
    return (end - start) / 1e6


def echo_probe(value):
    """Read a business probe from actual SDK input; no protocol envelope is built."""
    if hasattr(value, "model_dump"):
        value = value.model_dump()
    if isinstance(value, dict):
        for child in value.values():
            try:
                return echo_probe(child)
            except ValueError:
                pass
    elif isinstance(value, (list, tuple)):
        for child in value:
            try:
                return echo_probe(child)
            except ValueError:
                pass
    elif isinstance(value, str):
        match = PROBE.search(value)
        if match:
            return match.group(0)
    raise ValueError("Actual executor input contains no microbenchmark probe")


class EchoReceipts:
    """Deterministic fixed-size acknowledgement; no LLM and no external service."""
    def __init__(self):
        self.calls = 0
        self.receipts = []

    def acknowledge(self, value):
        text = echo_probe(value)
        self.calls += 1
        receipt = f"bytes={len(text.encode())};sha256={hashlib.sha256(text.encode()).hexdigest()}"
        self.receipts.append(receipt)
        return receipt

    async def answer(self, text):
        # The repository ANP/Agora HTTP handlers support this worker callback.
        # Its historical name mentions QA/LLM; this implementation is pure echo.
        return self.acknowledge(text)


class SDKNoopExecutor:
    """A2A SDK interface consumed by repository A2A server and Agora wrapper."""
    def __init__(self, receipts):
        self.receipts = receipts
        self.agora_qa_worker = receipts  # existing Agora HTTP responder hook

    async def execute(self, context, event_queue):
        from a2a.utils import new_agent_text_message
        message = getattr(context, "message", None)
        if message is None:
            message = context.get_user_input()
        await event_queue.enqueue_event(new_agent_text_message(self.receipts.acknowledge(message)))

    async def cancel(self, context, event_queue):
        return None


class ACPNoopExecutor:
    def __init__(self, receipts):
        self.receipts = receipts
        self.agent_id = "profile-destination"
        self.capabilities = ["deterministic_microbenchmark_echo"]

    async def __call__(self, messages, context):
        yield self.receipts.acknowledge(messages)


class ANPNoopExecutor:
    def __init__(self, receipts):
        self.receipts = receipts

    async def __call__(self, value):
        return self.receipts.acknowledge(value)

    async def answer(self, value):
        return await self.receipts.answer(value)


class ServerBodyObserver:
    """Count real received HTTP body bytes without changing ASGI events/handlers."""
    def __init__(self, app, observations):
        self.app, self.observations = app, observations

    async def __call__(self, scope, receive, send):
        body_bytes = 0
        is_request = scope.get("type") == "http" and scope.get("method") == "POST"
        async def observe_receive():
            nonlocal body_bytes
            event = await receive()
            if event.get("type") == "http.request":
                body_bytes += len(event.get("body", b""))
            return event  # exact original event, no buffering or transformation
        try:
            await self.app(scope, observe_receive, send)
        finally:
            if is_request:
                self.observations.append({"path": scope.get("path"), "body_bytes": body_bytes})


def install_local_network_guard():
    """This benchmark must not contact an LLM or any non-loopback endpoint."""
    def guard(event, args):
        if event == "socket.connect":
            address = args[1]
            if isinstance(address, tuple) and address:
                try:
                    local = ipaddress.ip_address(address[0]).is_loopback
                except ValueError:
                    local = address[0] == "localhost"
                if not local:
                    raise RuntimeError("Microbenchmark disallows non-loopback network connections")
    sys.addaudithook(guard)
    for key in ("OPENAI_API_KEY", "ANP_DID_SERVICE_URL", "ANP_DID_API_KEY",
                "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        os.environ.pop(key, None)
    os.environ["NO_PROXY"] = "127.0.0.1,localhost,::1"


def _contains(value, text):
    if isinstance(value, str):
        return text in value
    if isinstance(value, dict):
        return any(_contains(v, text) for v in value.values())
    if isinstance(value, (tuple, list)):
        return any(_contains(v, text) for v in value)
    return False


def _metric_value(metric, labels, suffix):
    return sum(sample.value for family in metric.collect() for sample in family.samples
               if sample.name.endswith(suffix) and sample.labels == labels)


class LocalSession:
    def __init__(self, protocol, timeout, setup_timeout):
        self.protocol, self.timeout, self.setup_timeout = protocol, timeout, setup_timeout
        self.receiver = self.sender = self.client = self.adapter = None
        self.receipts = EchoReceipts()
        self.observations = []
        self.transport_path = ""
        self.url = ""

    async def open(self):
        # src is also needed by the ORIGINAL Agora server's absolute import.
        sys.path.insert(0, str(REPO / "src"))
        sys.path.insert(0, str(REPO))
        import httpx
        from src.core.base_agent import BaseAgent
        from src.core.metrics import REQUEST_LATENCY, MSG_BYTES
        self.latency_metric, self.bytes_metric = REQUEST_LATENCY, MSG_BYTES
        self.client = httpx.AsyncClient(timeout=self.timeout, trust_env=False)
        if self.protocol == "A2A":
            self.receiver = await BaseAgent.create_a2a("profile-destination", host="127.0.0.1",
                executor=SDKNoopExecutor(self.receipts), httpx_client=self.client)
            self.transport_path = "A2AAdapter -> A2AStarletteApplication /message -> SDKNoopExecutor"
        elif self.protocol == "ACP":
            self.receiver = await BaseAgent.create_acp("profile-destination", host="127.0.0.1",
                executor=ACPNoopExecutor(self.receipts), httpx_client=self.client)
            self.transport_path = "ACPAdapter -> ACPStarletteApplication /acp/message -> ACPNoopExecutor"
        elif self.protocol == "ANP":
            self.receiver = await BaseAgent.create_anp("profile-destination", host="127.0.0.1",
                executor=ANPNoopExecutor(self.receipts), httpx_client=self.client,
                enable_protocol_negotiation=False)
            self.transport_path = "ANPAdapter -> ANPSimpleNodeWrapper /anp/message HTTP -> ANPNoopExecutor.answer"
        elif self.protocol == "Agora":
            import agora
            from src.server_adapters.agora_adapter import AgoraServerWrapper
            # SDK accepts no toolformer for the direct HTTP path. No dummy model,
            # fake sender, mocked receiver, or custom /message handler is provided.
            receiver = agora.Receiver.make_default(None, tools=[], storage_path=str(output_path(BASE / "results/raw/agora_runtime/receiver.json")))
            port = BaseAgent._find_free_port()
            executor = SDKNoopExecutor(self.receipts)
            wrapper = AgoraServerWrapper(receiver, "127.0.0.1", port, "profile-destination", executor)
            self.receiver = BaseAgent("profile-destination", host="127.0.0.1", port=port,
                                      httpx_client=self.client)
            self.receiver._server_instance = wrapper
            self.receiver._server_task = asyncio.create_task(wrapper.serve())
            self.receiver._initialized = True
            self.transport_path = "AgoraClientAdapter(toolformer=None) -> AgoraServerWrapper /message -> EchoReceipts.answer"
            from flask import request
            @wrapper.agora_server.app.before_request
            def observe_flask_request():
                if request.method == "POST":
                    self.observations.append({"path": request.path, "body_bytes": len(request.get_data())})
        else:
            raise ValueError(self.protocol)
        self.url = f"http://127.0.0.1:{self.receiver.port}"
        # BaseAgent ANP readiness only checks task scheduling; poll the real HTTP
        # health endpoint before installing observers or sending any warmup.
        started = time.perf_counter()
        while True:
            task = self.receiver._server_task
            if task.done():
                await task  # preserve actual server traceback
                raise RuntimeError("Protocol server exited before becoming ready")
            try:
                response = await self.client.get(self.url + "/health", timeout=1)
                if response.status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            if time.perf_counter() - started > self.setup_timeout:
                raise TimeoutError("Local protocol server did not become healthy")
            await asyncio.sleep(.05)
        instance = self.receiver._server_instance
        if self.protocol in ("A2A", "ACP"):
            # Uvicorn connection protocols cache loaded_app at startup. Attach to
            # the ORIGINAL Starlette application's dynamic middleware stack so
            # already-open real connections are observed too. Routes are unchanged.
            app = instance.config.app
            app.middleware_stack = ServerBodyObserver(app.middleware_stack, self.observations)
        elif self.protocol == "ANP":
            app = instance.starlette_app
            app.middleware_stack = ServerBodyObserver(app.middleware_stack, self.observations)
        self.dst = "profile-destination"
        if self.protocol == "A2A":
            from src.agent_adapters.a2a_adapter import A2AAdapter
            self.adapter = A2AAdapter(httpx_client=self.client, base_url=self.url)
        elif self.protocol == "ACP":
            from src.agent_adapters.acp_adapter import ACPAdapter
            self.adapter = ACPAdapter(httpx_client=self.client, base_url=self.url, agent_id="profile-source")
        elif self.protocol == "ANP":
            from src.agent_adapters.anp_adapter import ANPAdapter
            card = (await self.client.get(self.url + "/.well-known/agent.json")).json()
            self.dst = card["id"]  # actual locally generated DID, not a dummy key
            self.adapter = ANPAdapter(httpx_client=self.client, target_did=self.dst,
                server_card=card, target_http_base_url=self.url, host_domain="127.0.0.1",
                host_port=str(BaseAgent._find_free_port()), enable_protocol_negotiation=False,
                llm_instance=None, protocol_code_path=str(BASE / "results/raw/anp_runtime"))
        elif self.protocol == "Agora":
            from src.agent_adapters.agora_adapter import AgoraClientAdapter
            self.adapter = AgoraClientAdapter(toolformer=None, target_url=self.url,
                                              httpx_client=self.client)
        await self.adapter.initialize()
        self.sender = BaseAgent("profile-source", host="127.0.0.1", httpx_client=self.client)
        self.sender.add_outbound_adapter(self.dst, self.adapter)
        self.sender._initialized = True  # existing BaseAgent client-only lifecycle

    async def sample(self, size, phase, repetition):
        token = f"topology-profile-{self.protocol.lower()}-{size}-{phase[0]}-{repetition:03d}"
        content = {"text": token + "x" * (size - len(token))}
        expected = f"bytes={size};sha256={hashlib.sha256(content['text'].encode()).hexdigest()}"
        labels = {"src": "profile-source", "dst": self.dst, "protocol": self.protocol.lower()}
        byte_labels = {"direction": "out", "agent_id": "profile-source"}
        metric_sum = _metric_value(self.latency_metric, labels, "_sum")
        metric_count = _metric_value(self.latency_metric, labels, "_count")
        boundary_bytes = _metric_value(self.bytes_metric, byte_labels, "_total")
        observed_before, calls_before = len(self.observations), self.receipts.calls
        error_type = error_message = error_traceback = ""
        response = None
        # The measured interval brackets ORIGINAL BaseAgent.send: UTE creation,
        # original encode, real adapter/server/executor/response and decode.
        start_ns = time.perf_counter_ns()
        try:
            response = await asyncio.wait_for(self.sender.send(self.dst, content), self.timeout)
        except Exception as exc:
            error_type, error_message, error_traceback = type(exc).__name__, str(exc), traceback.format_exc()
        finally:
            end_ns = time.perf_counter_ns()
        latency = monotonic_ms(start_ns, end_ns)
        observed = self.observations[observed_before:]
        requests, calls = len(observed), self.receipts.calls - calls_before
        count = _metric_value(self.latency_metric, labels, "_count") - metric_count
        original_ms = ((_metric_value(self.latency_metric, labels, "_sum") - metric_sum) * 1000
                       if count == 1 else None)
        size_metric = _metric_value(self.bytes_metric, byte_labels, "_total") - boundary_bytes
        sane = (latency > 0 and original_ms is not None and original_ms >= 0 and original_ms <= latency + .01)
        if not error_type:
            try:
                if not sane:
                    raise RuntimeError("Wall-clock send timing/original request metric sanity check failed")
                if requests != 1 or calls != 1 or not _contains(response, expected):
                    raise RuntimeError(f"Missing real executor receipt: requests={requests}, calls={calls}")
            except Exception as exc:
                error_type, error_message, error_traceback = type(exc).__name__, str(exc), traceback.format_exc()
        row = dict(protocol=self.protocol, payload_size_bytes=size, phase=phase, repetition=repetition,
                   latency_ms=latency, encoded_request_bytes=observed[0]["body_bytes"] if requests == 1 else None,
                   success=not error_type, error_type=error_type, error_message=error_message,
                   timing_source="perf_counter_ns around BaseAgent.send", timing_sanity_passed=sane,
                   wall_clock_start_ns=start_ns, wall_clock_end_ns=end_ns, original_request_metric_ms=original_ms,
                   ute_encoded_bytes=int(size_metric) if size_metric > 0 else None,
                   server_requests=requests, executor_calls=calls, transport_path=self.transport_path)
        return row, error_traceback

    async def close(self):
        try:
            if self.sender:
                await self.sender.stop()
            elif self.adapter:
                await self.adapter.cleanup()
        finally:
            try:
                if self.receiver:
                    await self.receiver.stop()
            finally:
                if self.client:
                    await self.client.aclose()


def error_record(protocol, stage, exc, **extra):
    return {"protocol": protocol, "stage": stage, "error_type": type(exc).__name__,
            "error_message": str(exc), "traceback": traceback.format_exc(), **extra}


async def profile_one_protocol(config, protocol):
    install_local_network_guard()
    session = LocalSession(protocol, config.get("timeout_seconds", 30), config.get("setup_timeout_seconds", 40))
    rows, errors = [], []
    start = time.perf_counter_ns()
    setup = {"protocol": protocol, "status": "ready", "setup_latency_ms": None,
             "server_url": "", "transport_path": "", "error_type": "", "error_message": ""}
    try:
        await asyncio.wait_for(session.open(), session.setup_timeout)
    except Exception as exc:
        setup.update(status="blocked", error_type=type(exc).__name__, error_message=str(exc))
        errors.append(error_record(protocol, "setup", exc))
    finally:
        setup["setup_latency_ms"] = monotonic_ms(start, time.perf_counter_ns())
        setup["server_url"], setup["transport_path"] = session.url, session.transport_path
    try:
        if setup["status"] == "ready":
            for size in config["payload_size_bytes"]:
                for phase, count in (("warmup", config["warmup"]), ("measured", config["measured_repetitions"])):
                    for repetition in range(count):
                        row, trace = await session.sample(size, phase, repetition)
                        rows.append(row)
                        if trace:
                            errors.append({"protocol": protocol, "stage": "request", "phase": phase,
                                "payload_size_bytes": size, "repetition": repetition,
                                "error_type": row["error_type"], "error_message": row["error_message"], "traceback": trace})
    finally:
        try:
            await asyncio.wait_for(session.close(), 25)
        except Exception as exc:
            errors.append(error_record(protocol, "cleanup", exc))
    return {"rows": rows, "setup": setup, "errors": errors}


def summarize_real(rows, setups, config):
    from .protocol_cost_profiler import percentile
    output = []
    for setup in setups:
        for size in config["payload_size_bytes"]:
            attempts = [r for r in rows if r["protocol"] == setup["protocol"] and
                        r["payload_size_bytes"] == size and r["phase"] == "measured"]
            good = [r for r in attempts if r["success"]]
            times = [r["latency_ms"] for r in good]
            record = dict(protocol=setup["protocol"], payload_size_bytes=size,
                status="blocked" if setup["status"] != "ready" or not good else ("ok" if len(good) == len(attempts) else "partial"),
                requested_repetitions=config["measured_repetitions"], attempted_requests=len(attempts),
                successful_requests=len(good), failures=len(attempts)-len(good),
                skipped_requests=config["measured_repetitions"]-len(attempts),
                mean_latency_ms=statistics.mean(times) if times else None,
                median_latency_ms=statistics.median(times) if times else None,
                p95_latency_ms=percentile(times, .95),
                std_latency_ms=statistics.stdev(times) if len(times) > 1 else (0 if times else None),
                mean_encoded_request_bytes=statistics.mean([r["encoded_request_bytes"] for r in good]) if good else None,
                setup_latency_ms=setup["setup_latency_ms"], transport_path=setup["transport_path"],
                timing_source="perf_counter_ns around BaseAgent.send")
            output.append(record)
    return output


async def run_real_microbench(config):
    from .protocol_cost_profiler import dependency_versions
    from .io_utils import provenance, write_csv
    sizes = config["payload_size_bytes"]
    if sizes != [1024, 10240, 51200, 102400] or config["warmup"] != 5 or config["measured_repetitions"] != 30:
        raise ValueError("Real benchmark requires 4 specified buckets, 5 warmups and 30 measured repetitions")
    config_path = BASE / "results/raw/real_protocol_run_config.json"
    write_json(config_path, config)
    worker_dir = output_path(BASE / "results/raw/real_workers/placeholder").parent
    rows, setups, errors = [], [], []
    for protocol in PROTOCOLS:
        worker_output = worker_dir / f"{protocol}.json"
        with (worker_dir / f"{protocol}.txt").open("w") as log:
            process = await asyncio.create_subprocess_exec(sys.executable,
                str(BASE / "scripts/run_protocol_profile.py"), "--mode", "real", "--config", str(config_path),
                "--worker-protocol", protocol, "--worker-output", str(worker_output),
                cwd=str(REPO), stdout=log, stderr=asyncio.subprocess.STDOUT)
            # Hard ceiling kills only our isolated worker, including daemon servers.
            timeout = config.get("setup_timeout_seconds", 40) + len(sizes) * 35 * config.get("timeout_seconds", 30) + 30
            try:
                await asyncio.wait_for(process.wait(), timeout)
                if process.returncode != 0:
                    raise RuntimeError(f"{protocol} worker exited {process.returncode}; see {protocol}.txt")
                result = json.loads(worker_output.read_text())
                rows.extend(result["rows"])
                setups.append(result["setup"])
                errors.extend(result["errors"])
            except Exception as exc:
                if process.returncode is None:
                    process.kill()
                    await process.wait()
                errors.append(error_record(protocol, "worker", exc, console_log=str(worker_dir / f"{protocol}.txt")))
                setups.append(dict(protocol=protocol, status="blocked", setup_latency_ms=None,
                    server_url="", transport_path="", error_type=type(exc).__name__, error_message=str(exc)))
        good = sum(r["success"] for r in rows if r["protocol"] == protocol and r["phase"] == "measured")
        print(f"{protocol}: setup={setups[-1]['status']}; measured successes={good}/120", flush=True)
    stats = summarize_real(rows, setups, config)
    write_csv(BASE / "results/raw/real_protocol_profile.csv", rows, RAW_FIELDS)
    write_csv(BASE / "results/raw/real_protocol_setup.csv", setups, SETUP_FIELDS)
    write_json(BASE / "results/raw/real_protocol_profile_failures.json", {"setup": setups, "failures": errors})
    write_csv(BASE / "results/processed/real_protocol_costs.csv", stats, STAT_FIELDS)
    write_json(BASE / "results/raw/real_protocol_manifest.json", provenance(config, {
        "mode": "real_local", "dependencies": dependency_versions(), "setup": setups,
        "latency_boundary": "perf_counter_ns immediately around await BaseAgent.send; setup/warmup excluded from summary",
        "encoded_request_bytes": "HTTP request body bytes observed at the actual local repository server",
        "ute_encoded_bytes": "original MSG_BYTES delta at converter boundary (successful adapter returns)",
        "success_requires": "real server POST, exactly one deterministic executor call, byte-count/SHA256 acknowledgement and timing sanity",
        "std_definition": "sample standard deviation (ddof=1)", "p95_definition": "linear interpolation (n-1)*0.95",
        "llm_calls": 0, "gaia_runs": 0, "external_network": "blocked by worker socket audit hook"}))
    return 0 if all(r["successful_requests"] == 30 for r in stats) and not errors else 2
