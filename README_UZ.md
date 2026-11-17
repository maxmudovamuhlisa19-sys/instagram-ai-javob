# Instagram DM — AI avtomatik javob boti

Bu loyiha Instagram **Direct (DM)** xabarlariga **AI avtomatik javob** yozib beradi.
Rasmiy yo'l: Instagram professional akkaunt → Facebook Page → Meta Graph API → OpenAI.

> **Muhim:** Shaxsiy akkauntlarda rasmiy DM API ishlamaydi. Shuning uchun akkauntingizni
> **Business (yoki Creator)** turiga o'tkazishingiz kerak. Bu bepul va profilingizni
> buzmaydi — faqat akkaunt turi o'zgaradi.

---

## Loyihadagi fayllar

| Fayl | Nima uchun |
|---|---|
| `app.py` | Botning asosiy kodi (FastAPI server) |
| `requirements.txt` | Python kutubxonalar |
| `.env.example` | Sozlamalar namoyishi — bu nusxani `.env` qilib to'ldiring |
| `render.yaml` | Render serveriga avtomatik o'rnatish uchun |
| `README_UZ.md` | Bu qo'llanma |

---

## 1-qadam: Instagram akkauntni professionalga o'tkazish

1. Instagram ilovasini oching → **Profil** → yuqori o'ngda **☰ (uch chiziq)**.
2. **Settings and privacy** → **Account type and tools** → **Switch to professional account**.
3. **Business** ni tanlang (Creator ham mumkin, lekin Business tavsiya).
4. Jarayon davomida sizdan **Facebook Page** so'raydi — **yangi page yarating**
   (nom va kategoriya muhim emas, masalan "Mening sahifam").

---

## 2-qadam: Instagram va Facebook Page'ni bog'lash

1. Instagram → **Settings** → **Account** → **Linked accounts** → **Facebook**.
2. O'sha yaratgan Page'ingizni tanlang va ulang.

---

## 3-qadam: Meta for Developersda ilova yaratish

1. https://developers.facebook.com/ oching → **My Apps** → **Create app**.
2. **App type** → **Business** → **Next**.
3. Ilova nomini yozing (masalan `ig-ai-javob`), pochtangizni tanlang → **Create app**.
4. Chap menyudan **Instagram** mahsulotini qo'shing (**Add product**).

## 4-qadam: O'z akkauntingizni "tester" qilib qo'yish

Ilova **Development** rejimida bo'lganda faqat tester akkauntlar ishlay oladi.

1. App Dashboard → **Roles** → **Instagram testers** → **Add Instagram testers**.
2. Instagram akkauntingiz **foydalanuvchi nomini** kiriting → **Submit**.
3. Instagram ilovasida sizga **taklif (invite)** keladi — uni **tasdiqlang**.
   (Ba'zan u yerda ko'rinmaydi; sahifani yangilab ko'ring yoki Instagram notification'ini tekshiring.)

---

## 5-qadam: Page Access Token olish (muhim!)

Buning uchun **Graph API Explorer** ishlatamiz:

1. https://developers.facebook.com/tools/explorer/ oching.
2. Yuqori o'ngda o'z ilovangizni tanlang.
3. **Permissions** qismidan quyidagilarni qo'shing:
   - `instagram_manage_messages`
   - `pages_show_list`
   - `pages_read_engagement`
4. **Generate Access Token** ni bosing va Facebook akkauntingiz bilan tasdiqlang.
   → Bu token **faqat 1 soat** ishlaydi. Uni uzaytiramiz.

**5.1. 60 kunlik token olish** (brauzerda ochib, APP_ID va APP_SECRET ni ilovangizdan oling):
```
https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=1_SOATLIK_TOKEN
```
Natijadagi `access_token` ni nusxalab, quyidagiga paste qiling:
```
https://graph.facebook.com/v20.0/me/accounts?fields=access_token&access_token=60_KUNLIK_TOKEN
```
Bu yerda sizning Page'ingiz uchun chiqadigan `access_token` ni oling.
**Mana shu token `PAGE_ACCESS_TOKEN` bo'ladi** (uzoq muddatli, o'chmaydi).

> APP_ID va APP_SECRET ni olish: App Dashboard → **Settings** → **Basic**.

---

## 6-qadam: Serverni yig'ish (Render — bepul)

1. https://render.com/ ro'yxatdan o'ting (GitHub bilan eng qulay).
2. Ushbu papkani **GitHub'ga yuklang** (yangi repo, masalan `instagrammmm`).
3. Render → **New** → **Web Service** → repo'ni tanlang.
4. Render `render.yaml` ni ko'rib, avtomatik sozlaydi. Quyidagi **Environment** o'zgaruvchilarini qo'lda kiriting:

| O'zgaruvchi | Qiymat |
|---|---|
| `VERIFY_TOKEN` | O'zingiz o'ylab topgan matn (keyin 7-qadamda shuni kiritasiz) |
| `PAGE_ACCESS_TOKEN` | 5-qadamda olgan token |
| `OPENAI_API_KEY` | OpenAI kalitingiz (7-qadamda tayyorlaymiz) |
| `IG_USER_ID` | (ixtiyoriy) Instagram akkaunt ID raqami |
| `SYSTEM_PROMPT` | Botning xarakati (ixtiyoriy) |

5. **Create Web Service** ni bosing — Render o'zi build qilib, ishga tushiradi.
6. Manzilni eslang, masalan: `https://instagram-ai-javob.onrender.com`

> Renderning bepul rejimi uxlab qoladi va webhook kelganda uyg'onadi (birinchi javob
> 30–60 sekund kechikishi mumkin). Doimiy tezkor ish kerak bo'lsa — boshqa host tanlang.

---

## 7-qadam: OpenAI API kaliti

1. https://platform.openai.com/api-keys oching → **Create new secret key**.
2. Kalitni (`sk-...`) `OPENAI_API_KEY` sifatida Renderga kiriting.
3. Hisobingizga kamida **5$** tushing (gpt-4o-mini juda arzon — bir necha ming xabar uchun 1$ yetadi).

---

## 8-qadam: Webhook'ni ulash

1. App Dashboard → **Webhooks** → **Instagram** → **Subscribe to webhooks**.
2. **Callback URL**: `https://instagram-ai-javob.onrender.com/webhook`
   (o'z Render manzilingizni yozing)
3. **Verify token**: 6-qadamdagi `VERIFY_TOKEN` bilan **bir xil** matn.
4. **Fields** ichidan **`messages`** ni belgilang.
5. **Subscribe** ni bosing. Meta tekshiruv yuboradi — muvaffaqiyat bo'lsa bot tayyor.

---

## 9-qadam: Sinash

1. Instagram'da o'z akkauntingizga **boshqa akkaunt**dan (yoki o'zingizdan boshqa telefon/akkauntdan) DM yozing.
2. Render loglarini oching: Render Dashboard → Service → **Logs**.
   - `Webhook keldi` degan yozuv bo'lishi kerak.
   - `Javob yuborildi` degan yozuv kelguncha bot javob beradi.
3. Agar javob kelmasa — quyidagi "Muammolar" bo'limiga qarang.

---

## Botni o'zgartirish

- **AI xarakati** — Renderda `SYSTEM_PROMPT` ni o'zgartiring.
- **Model** — `OPENAI_MODEL` (masalan `gpt-4o-mini`, `gpt-4o`).
- **Javob uzunligi** — `OPENAI_MAX_TOKENS`.
- **Telefonni tekshirish** — `IG_USER_ID` bo'sh qoldirsa ham ishlaydi (faqat o'z xabariga javob bermaslik himoyasi kuchsizroq bo'ladi).

---

## Muammolar

| Holat | Yechim |
|---|---|
| Webhook 403 qaytardi | `VERIFY_TOKEN` Meta'dagi bilan bir xil emas |
| Hech narsa yozmayapti | Render uxlab qolgandir — loglarni tekshiring, biroz kutib ko'ring |
| "Invalid token" xatosi | Page token yaroqsiz/eskirgan — 5-qadamni qaytadan bajaring |
| AI javob bermayapti | OpenAI kaliti noto'g'ri yoki hisob bo'sh |
| O'z xabarimga javob berdi | `IG_USER_ID` ni to'g'ri kiriting |
| Meta "tester" taklifini ko'rmayman | App Dashboard → Roles → Instagram testers → qayta qo'shing |

---

## Xavfsizlik eslatmalari

- `PAGE_ACCESS_TOKEN`, `OPENAI_API_KEY` hech qachon boshqalarga bermang.
- `.env` fayli GitHub'ga tushmasligi kerak (`.gitignore` uni himoyalaydi).
- Bot faqat Instagram **messaging** huquqidan foydalanadi, boshqa narsaga ruxsati yo'q.
