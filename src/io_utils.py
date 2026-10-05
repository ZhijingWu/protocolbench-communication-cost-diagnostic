"""Experiment-only I/O, source loading and provenance; no original source edits."""
import csv
import hashlib
import importlib.util
import json
import math
import os
import platform
import subprocess
import sys
import types
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
REPO = Path(os.environ.get("AGENTPROTOCOLS_ROOT", str(BASE.parent / "AgentProtocols"))).expanduser().resolve()
PROTOCOLS = ("A2A", "ACP", "ANP", "Agora")
AUDIT_PATHS = (
    "routerbench/proto_router.py", "routerbench/prompt_template.py",
    "routerbench/run_benchmark.py", "routerbench/evaluator.py",
    "scenarios/gaia/protocol_backends/meta_protocol/llm_router.py",
    "scenarios/gaia/protocol_backends/meta_protocol/network.py",
    "scenarios/gaia/runners/run_meta_protocol.py",
    "scenarios/gaia/config/meta_protocol.yaml", "src/core/base_agent.py",
    "src/core/network.py", "src/core/protocol_converter.py", "src/core/metrics.py",
    "src/core/unified_message.py", "src/agent_adapters/agora_adapter.py",
)


def protocol_name(value):
    names = {p.lower(): p for p in PROTOCOLS}
    try:
        return names[str(value).lower()]
    except KeyError:
        raise ValueError(f"Unsupported protocol: {value}") from None


def nonnegative(value, name):
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return value


def output_path(path):
    path = Path(path).resolve()
    if not path.is_relative_to(BASE):
        raise ValueError(f"Output must remain under {BASE}: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path, value):
    output_path(path).write_text(json.dumps(value, indent=2, sort_keys=True,
                                          allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path, rows, fields):
    with output_path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="raise", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_config(path):
    import yaml
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Config must be a mapping")
    return data


def fingerprint(value):
    text = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(text.encode()).hexdigest()


def source_module(name, path):
    """Execute original module from disk under an isolated experiment namespace."""
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # required by dataclasses
    try:
        spec.loader.exec_module(module)
    except BaseException:
        del sys.modules[name]
        raise
    return module


def original_converters():
    # core/__init__.py eagerly imports all SDKs. This isolated package only loads
    # the two ORIGINAL pure modules and honors their relative import unchanged.
    name = "_topology_original_core"
    if name not in sys.modules:
        package = types.ModuleType(name)
        package.__path__ = [str(REPO / "src/core")]
        sys.modules[name] = package
    ute = source_module(name + ".unified_message", REPO / "src/core/unified_message.py")
    converters = source_module(name + ".protocol_converter", REPO / "src/core/protocol_converter.py")
    return ute.UTE, converters.ENCODE_TABLE


def provenance(config, extra=None):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(REPO), *args], text=True).strip()
    return {"python": sys.version, "executable": sys.executable,
            "platform": platform.platform(), "head": git("rev-parse", "HEAD"),
            "branch": git("branch", "--show-current"), "config": config,
            "config_sha256": fingerprint(config),
            "source_sha256": {p: hashlib.sha256((REPO / p).read_bytes()).hexdigest()
                              for p in AUDIT_PATHS}, **(extra or {})}
