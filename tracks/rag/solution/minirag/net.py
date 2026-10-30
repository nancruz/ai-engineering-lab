"""Tiny JSON-over-HTTP helper so model adapters need no SDKs. (Supplied.)"""
import json
import urllib.error
import urllib.request


class ModelError(RuntimeError):
    """A model or embedding provider failed (network, auth, bad reply)."""


def post_json(url, payload, headers=None, timeout=60):
    data = json.dumps(payload).encode()
    request = urllib.request.Request(url, data=data, method="POST",
                                     headers={"Content-Type": "application/json", **(headers or {})})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as err:
        body = err.read().decode(errors="replace")[:300]
        raise ModelError(f"{url} returned HTTP {err.code}: {body}") from None
    except (urllib.error.URLError, TimeoutError, ConnectionError) as err:
        raise ModelError(f"could not reach {url}: {err}") from None
    except json.JSONDecodeError as err:
        raise ModelError(f"{url} did not return JSON: {err}") from None
