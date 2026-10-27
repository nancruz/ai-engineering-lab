"""Plug a real local model (Ollama /api/chat with tools) into agent.run_agent.

Standard library only. Requires a running Ollama server and a tool-capable
model tag you have pulled yourself. The adapter records every request's usage
and raw response so a run can be inspected afterwards. It handles one tool call
per turn; if the model returns several, the rest are recorded and ignored.
"""
import json
import urllib.error
import urllib.request

from agent import TOOLS


def tool_specs():
    return [{"type": "function", "function": {"name": t["name"], "description": t["description"],
                                              "parameters": t["input_schema"]}} for t in TOOLS]


def to_ollama(messages):
    out = []
    for m in messages:
        if m["role"] in ("system", "user"):
            out.append({"role": m["role"], "content": m["content"]})
        elif m["role"] == "assistant" and "tool_call" in m:
            call = m["tool_call"]
            out.append({"role": "assistant", "content": "",
                        "tool_calls": [{"type": "function", "function": {"name": call["tool"], "arguments": call["args"]}}]})
        elif m["role"] == "assistant":
            out.append({"role": "assistant", "content": m["content"]})
        elif m["role"] == "tool":
            out.append({"role": "tool", "tool_name": m["name"], "content": m["content"]})
    return out


class OllamaModel:
    def __init__(self, tag, host="http://localhost:11434", timeout=180):
        self.tag, self.host, self.timeout, self.log = tag, host.rstrip("/"), timeout, []

    def __call__(self, task, steps, messages):
        body = {"model": self.tag, "messages": to_ollama(messages), "tools": tool_specs(), "stream": False}
        request = urllib.request.Request(self.host + "/api/chat", data=json.dumps(body).encode(),
                                         headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = json.loads(response.read())
        except urllib.error.URLError as error:
            raise RuntimeError(f"Ollama request failed ({error}). Is the server running at {self.host}?") from error
        message = raw.get("message", {})
        calls = message.get("tool_calls") or []
        self.log.append({"input_tokens": raw.get("prompt_eval_count"), "output_tokens": raw.get("eval_count"),
                         "extra_tool_calls_ignored": max(0, len(calls) - 1), "raw": raw})
        if calls:
            fn = calls[0]["function"]
            args = fn.get("arguments") or {}
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {"_unparsed": args}
            return {"tool": fn["name"], "args": args}
        return {"final": message.get("content", "")}
