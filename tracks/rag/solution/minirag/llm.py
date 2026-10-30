"""Language-model adapters behind one small interface. (Supplied.)

    llm.name
    llm.complete(messages, temperature=0.0, max_tokens=512) -> str

`messages` is a list of {"role": "system" | "user" | "assistant", "content": str}.
No SDKs are needed: each adapter is one HTTP call. Pick one with make_llm():

    extractive               offline baseline, no model at all (see ExtractiveLLM)
    ollama:llama3.2:3b       local model served by Ollama
    openai:<model>           OpenAI or any OpenAI-compatible server (OPENAI_API_KEY, OPENAI_BASE_URL)
    anthropic:<model>        Anthropic Messages API (ANTHROPIC_API_KEY)
"""
import os
import re

from .net import ModelError, post_json
from .text import tokenize

SOURCE_HEADER = re.compile(r"^\[S(\d+)\]([^\n]*)\n", re.M)


class ExtractiveLLM:
    """Not a language model: copies the source sentences that best overlap the question.

    It exists so the whole pipeline runs offline and deterministically. It
    scores sentences by the share of question terms they contain (terms found
    only in the source's title/heading count half), copies the best sentence
    and the one after it, cites them, and abstains when nothing overlaps
    enough. It never follows instructions found in sources. Real models write
    better answers, and can also be talked into worse ones: compare them in Lab 4.
    """

    name = "extractive"

    def __init__(self, threshold=0.4):
        self.threshold = threshold

    def complete(self, messages, temperature=0.0, max_tokens=512):
        from .generation import ABSTAIN  # local import avoids a cycle
        prompt = messages[-1]["content"]
        sources_text, _, question = prompt.rpartition("Question:")
        wanted = set(tokenize(question))
        candidates = []  # (label, position, sentence, sentence terms, header terms)
        for label, header, text in split_sources(sources_text):
            head = set(tokenize(header))
            for position, sentence in enumerate(sentences(text)):
                candidates.append((label, position, sentence, set(tokenize(sentence)), head))
        if not wanted or not candidates:
            return ABSTAIN
        def score(c):
            in_sentence = wanted & c[3]
            in_header = (wanted & c[4]) - in_sentence
            return (len(in_sentence) + 0.5 * len(in_header)) / len(wanted)

        ranked = sorted(candidates, key=lambda c: (-score(c), c[0], c[1]))
        best = ranked[0]
        if score(best) < self.threshold:
            return ABSTAIN
        picked = [best]
        following = next((c for c in candidates if c[0] == best[0] and c[1] == best[1] + 1), None)
        if following and len(following[3]) >= 4 and not following[2].endswith(":"):
            picked.append(following)
        other = next((c for c in ranked[1:] if c[0] != best[0] and score(c) >= self.threshold), None)
        if other:
            picked.append(other)
        return " ".join(f"{c[2]} [S{c[0]}]" for c in picked)


def split_sources(text):
    """Yield (number, header, body) for each '[Sn] header' block in a prompt."""
    marks = list(SOURCE_HEADER.finditer(text))
    for mark, nxt in zip(marks, marks[1:] + [None]):
        yield int(mark.group(1)), mark.group(2), text[mark.end(): nxt.start() if nxt else len(text)].strip()


def sentences(text):
    """Rough sentence splitter that also treats list items and table rows as sentences."""
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            continue  # headings are labels, not answers
        line = line.lstrip("-*0123456789. ").strip()
        if not line or set(line) <= set("|- :"):
            continue
        if line.startswith("|"):
            yield " — ".join(cell.strip() for cell in line.strip("|").split("|") if cell.strip())
            continue
        for part in re.split(r"(?<=[.!?])\s+", line):
            if part:
                yield part


class ScriptedLLM:
    """Test double: returns canned replies (a list, or a function of the messages) and records calls."""

    name = "scripted"

    def __init__(self, replies):
        self.replies, self.calls = replies, []

    def complete(self, messages, temperature=0.0, max_tokens=512):
        self.calls.append(messages)
        if callable(self.replies):
            return self.replies(messages)
        if not self.replies:
            raise ModelError("ScriptedLLM has no replies left")
        return self.replies.pop(0)


class OllamaLLM:
    def __init__(self, model, host=None, timeout=120):
        self.model, self.timeout, self.name = model, timeout, f"ollama:{model}"
        self.host = (host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")

    def complete(self, messages, temperature=0.0, max_tokens=512):
        reply = post_json(f"{self.host}/api/chat", {
            "model": self.model, "messages": messages, "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens}}, timeout=self.timeout)
        return reply["message"]["content"]


class OpenAICompatLLM:
    def __init__(self, model, base_url=None, api_key=None, timeout=120):
        self.model, self.timeout, self.name = model, timeout, f"openai:{model}"
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")

    def complete(self, messages, temperature=0.0, max_tokens=512):
        reply = post_json(f"{self.base_url}/chat/completions",
                          {"model": self.model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens},
                          headers={"Authorization": f"Bearer {self.api_key}"}, timeout=self.timeout)
        return reply["choices"][0]["message"]["content"]


class AnthropicLLM:
    def __init__(self, model, api_key=None, base_url=None, timeout=120):
        self.model, self.timeout, self.name = model, timeout, f"anthropic:{model}"
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.base_url = (base_url or os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")).rstrip("/")

    def complete(self, messages, temperature=0.0, max_tokens=512):
        system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
        chat = [m for m in messages if m["role"] != "system"]
        reply = post_json(f"{self.base_url}/v1/messages",
                          {"model": self.model, "max_tokens": max_tokens, "temperature": temperature,
                           "system": system, "messages": chat},
                          headers={"x-api-key": self.api_key, "anthropic-version": "2023-06-01"}, timeout=self.timeout)
        return "".join(block.get("text", "") for block in reply["content"] if block.get("type") == "text")


def make_llm(spec="extractive"):
    kind, _, model = spec.partition(":")
    if kind == "extractive":
        return ExtractiveLLM()
    if not model:
        raise ValueError(f"{spec!r}: name the model, e.g. ollama:llama3.2:3b")
    adapters = {"ollama": OllamaLLM, "openai": OpenAICompatLLM, "anthropic": AnthropicLLM}
    if kind not in adapters:
        raise ValueError(f"unknown LLM {spec!r}; use extractive, ollama:<model>, openai:<model> or anthropic:<model>")
    return adapters[kind](model)
