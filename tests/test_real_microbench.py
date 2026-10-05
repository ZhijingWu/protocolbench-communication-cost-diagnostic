import sys
sys.dont_write_bytecode = True
import asyncio
import hashlib
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.local_protocol_microbench import (
    EchoReceipts, ServerBodyObserver, monotonic_ms, summarize_real)


class RealMicrobenchTests(unittest.TestCase):
    def test_wall_clock_units_and_invalid_interval(self):
        self.assertEqual(monotonic_ms(1000000, 4000000), 3)
        with self.assertRaises(RuntimeError):
            monotonic_ms(10, 10)

    def test_deterministic_executor_acknowledges_entire_payload(self):
        text = "topology-profile-a2a-1024-m-000"
        text += "x" * (1024 - len(text))
        receipts = EchoReceipts()
        first = receipts.acknowledge({"nested": {"text": text}})
        self.assertEqual(first, f"bytes=1024;sha256={hashlib.sha256(text.encode()).hexdigest()}")
        self.assertEqual(receipts.acknowledge(text), first)
        self.assertEqual(receipts.calls, 2)

    def test_real_statistics_exclude_warmups_and_failed_latencies(self):
        config = {"payload_size_bytes": [1024], "measured_repetitions": 30}
        setups = [{"protocol": "A2A", "status": "ready", "setup_latency_ms": 900,
                   "transport_path": "test"}]
        rows = [dict(protocol="A2A", payload_size_bytes=1024, phase=phase,
                     success=success, latency_ms=latency, encoded_request_bytes=bytes_)
                for phase, success, latency, bytes_ in [("warmup", True, 100, 2000),
                    ("measured", True, 2, 1400), ("measured", True, 4, 1400),
                    ("measured", False, 999, None)]]
        stat = summarize_real(rows, setups, config)[0]
        self.assertEqual(stat["successful_requests"], 2)
        self.assertEqual(stat["failures"], 1)
        self.assertEqual(stat["mean_latency_ms"], 3)
        self.assertAlmostEqual(stat["std_latency_ms"], 2**.5)
        self.assertEqual(stat["mean_encoded_request_bytes"], 1400)
        self.assertEqual(stat["setup_latency_ms"], 900)

    def test_server_observer_keeps_original_asgi_events(self):
        events = [{"type": "http.request", "body": b"abc", "more_body": True},
                  {"type": "http.request", "body": b"de", "more_body": False}]
        seen, records = [], []
        async def app(scope, receive, send):
            seen.extend([await receive(), await receive()])
        index = 0
        async def receive():
            nonlocal index
            event = events[index]
            index += 1
            return event
        async def send(event):
            pass
        asyncio.run(ServerBodyObserver(app, records)(
            {"type": "http", "method": "POST", "path": "/message"}, receive, send))
        self.assertIs(seen[0], events[0])
        self.assertIs(seen[1], events[1])
        self.assertEqual(records, [{"path": "/message", "body_bytes": 5}])


if __name__ == "__main__":
    unittest.main()
