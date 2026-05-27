"""
AI DevTools — OpenRouter API Client
Mendukung streaming response, auto-retry, dan fallback model otomatis.
"""

import requests
import json
import time
from config import API_KEY, BASE_URL, DEFAULT_MODEL

# Model fallback jika primary rate-limited (hasil test)
FALLBACK_MODELS = [

]


class OpenRouterClient:
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-devtools.local",
            "X-Title": "AI DevTools",
        }

    def set_model(self, model: str):
        self.model = model

    def chat(self, messages: list, system_prompt: str = None, stream: bool = True,
             _retry: int = 0, _model_override: str = None):
        """
        Kirim pesan ke OpenRouter.
        Auto-retry dengan backoff + fallback model jika rate-limited.
        """
        model = _model_override or self.model
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        payload = {
            "model": model,
            "messages": full_messages,
            "stream": stream,
            "temperature": 0.7,
        }

        try:
            if stream:
                resp = requests.post(
                    f"{BASE_URL}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    stream=True,
                    timeout=120,
                )
                resp.raise_for_status()
                return self._parse_stream(resp)
            else:
                resp = requests.post(
                    f"{BASE_URL}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=120,
                )
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"]

        except requests.exceptions.HTTPError as e:
            code = e.response.status_code

            # Rate limit → coba fallback model
            if code == 429:
                fallbacks = [m for m in FALLBACK_MODELS if m != model]
                if _retry < len(fallbacks):
                    next_model = fallbacks[_retry]
                    wait = min(2 ** _retry, 8)
                    print(f"\n[!] Rate limit pada {model.split('/')[-1]}, "
                          f"coba {next_model.split('/')[-1]} dalam {wait}s...")
                    time.sleep(wait)
                    return self.chat(
                        messages, system_prompt, stream,
                        _retry=_retry + 1, _model_override=next_model
                    )
                raise RuntimeError(
                    "Rate limit di semua model. Tunggu beberapa menit lalu coba lagi."
                )

            elif code == 402:
                raise RuntimeError(
                    "Kredit habis untuk model berbayar ini. "
                    "Pilih model FREE di menu Ganti Model."
                )
            elif code == 401:
                raise RuntimeError("API Key tidak valid atau expired.")
            elif code == 404:
                raise RuntimeError(f"Model '{model}' tidak ditemukan di OpenRouter.")
            else:
                raise RuntimeError(f"HTTP Error {code}: {e.response.text[:200]}")

        except requests.exceptions.ConnectionError:
            raise RuntimeError("Tidak bisa konek ke internet. Cek koneksi Anda.")
        except requests.exceptions.Timeout:
            raise RuntimeError("Request timeout. Coba lagi.")

    def _parse_stream(self, response):
        """Parse SSE stream dari OpenRouter"""
        for raw_line in response.iter_lines():
            if raw_line:
                line = raw_line.decode("utf-8")
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        return
                    try:
                        data = json.loads(data_str)
                        delta = data["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue

    def quick_ask(self, prompt: str, system: str = None) -> str:
        """Non-streaming, return string penuh"""
        return self.chat(
            [{"role": "user", "content": prompt}],
            system_prompt=system,
            stream=False,
        )

