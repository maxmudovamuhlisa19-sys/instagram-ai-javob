"""
Instagram DM -> AI avtomatik javob boti (rasmiy Meta Graph API orqali)

Ishlash tartibi:
  1. Instagram xabari keladi -> Meta webhook orqali shu serverga yuboriladi.
  2. Xabar matni AI (OpenAI) ga yuboriladi.
  3. AI javob yasab, uni qaytadan Instagram'ga yozadi.

O'rnatish: README_UZ.md ga qarang.
"""

import os
import logging

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Query, Request

load_dotenv()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ig-ai-bot")

# ---------- Sozlamalar (.env faylidan o'qiydi) ----------
VERIFY_TOKEN = os.environ["VERIFY_TOKEN"]              # Webhook tasdiqlash tokeni (ixtiyoriy, o'zingiz tanlang)
PAGE_ACCESS_TOKEN = os.environ["PAGE_ACCESS_TOKEN"]    # Facebook Page Access Token (instagram_manage_messages huquqi bilan)
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]          # OpenAI API kaliti
IG_USER_ID = os.environ.get("IG_USER_ID", "")          # Sizning Instagram business akkauntingiz ID raqami (ixtiyoriy, himoya uchun)
PORT = int(os.environ.get("PORT", "8000"))
GRAPH_VERSION = os.environ.get("GRAPH_VERSION", "v20.0")
GRAPH = f"https://graph.facebook.com/{GRAPH_VERSION}"
OPENAI_URL = os.environ.get("OPENAI_URL", "https://api.openai.com/v1/chat/completions")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

# Botning shaxsiyati (AI ga beriladigan ko'rsatma). O'zgartirsangiz shu yerni tahrirlang.
SYSTEM_PROMPT = os.environ.get(
    "SYSTEM_PROMPT",
    "Sen foydalanuvchiga Instagram orqali javob beruvchi do'stona, qisqa va tushunarli "
    "o'zbek tilidagi yordamchisan. Hech qachon dastur yoki AI ekanligini oshkor qilmaysan. "
    "Foydalanuvchi savoliga qisqa, aniq javob ber. Kerak bo'lsa, aniqrog'ini so'rayver.",
)

app = FastAPI(title="Instagram AI Javob Boti")

# Qayta ishlovni oldini olish uchun (bir xabar bir necha marta kelishi mumkin)
_processed_ids: set[str] = set()


# ---------- Yordamchi funksiyalar ----------
async def generate_reply(user_text: str) -> str:
    """OpenAI dan javob matnini olish."""
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        "max_tokens": int(os.environ.get("OPENAI_MAX_TOKENS", "400")),
        "temperature": float(os.environ.get("OPENAI_TEMPERATURE", "0.7")),
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(OPENAI_URL, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
    return data["choices"][0]["message"]["content"].strip()


async def send_ig_text(recipient_id: str, text: str) -> dict:
    """Instagram'ga matnli xabar yuborish."""
    url = f"{GRAPH}/{recipient_id}/messages"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text},
        "access_token": PAGE_ACCESS_TOKEN,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        return r.json()


# ---------- Endpointlar ----------
@app.get("/")
async def health():
    return {"status": "ok", "bot": "instagram-ai-javob"}


@app.get("/webhook")
async def webhook_verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    """Meta webhook'ni birinchi marta tekshirganda shu endpoint chaqiriladi."""
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        log.info("Webhook tasdiqlandi (verify ok)")
        return int(hub_challenge)
    log.warning("Webhook tasdiqlash xatosi")
    return {"error": "verification failed"}, 403


@app.post("/webhook")
async def webhook_receive(request: Request):
    """Kelgan Instagram xabarlarini qabul qiladi."""
    body = await request.json()
    log.info("Webhook keldi: %s", body)

    if body.get("object") != "instagram":
        return {"status": "ignored"}

    for entry in body.get("entry", []):
        for change in entry.get("changes", []):
            if change.get("field") != "messages":
                continue

            value = change.get("value") or {}
            message = value.get("message") or {}
            sender_id = (value.get("sender") or {}).get("id")
            text = message.get("text")
            mid = message.get("mid")

            if not sender_id or not text:
                continue

            # 1) O'z xabarimizga javob berib turmaslik uchun
            if value.get("is_echo"):
                continue
            if IG_USER_ID and sender_id == IG_USER_ID:
                continue

            # 2) Takroriy xabarlarni o'tkazib yuborish
            if mid and mid in _processed_ids:
                continue
            if mid:
                _processed_ids.add(mid)

            log.info("Yangi xabar. Kimdan: %s | Matn: %s", sender_id, text)

            try:
                reply = await generate_reply(text)
                await send_ig_text(sender_id, reply)
                log.info("Javob yuborildi: %s", reply)
            except Exception as exc:  # noqa: BLE001
                log.error("Xatolik: %s", exc)

    return {"status": "ok"}
