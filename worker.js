const ALLOWED_ORIGINS = new Set([
  "https://seekvera-global.github.io",
  "https://seekvera-main.seekvera-global.workers.dev"
]);

const PRIMARY_AI_MODEL = "@cf/meta/llama-3.1-8b-instruct-fast";
const FALLBACK_AI_MODEL = "@cf/google/gemma-4-26b-a4b-it";

const SUPABASE_URL = "https://nrdpyydfrpmqedtzmbyw.supabase.co";
const SUPABASE_PUBLISHABLE_KEY = "sb_publishable_tqqPQxqdNowIsSlJz4bW5w_kHOC905o";

function corsHeaders(request) {
  const origin = request.headers.get("origin") || "";
  const allowed = ALLOWED_ORIGINS.has(origin) ? origin : "";
  return {
    ...(allowed ? { "access-control-allow-origin": allowed } : {}),
    "access-control-allow-methods": "POST,GET,OPTIONS",
    "access-control-allow-headers": "content-type",
    "access-control-max-age": "86400",
    "vary": "Origin"
  };
}

const json = (request, data, status = 200) => new Response(JSON.stringify(data), {
  status,
  headers: {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store",
    "x-content-type-options": "nosniff",
    ...corsHeaders(request)
  }
});

const secure = (response) => {
  const secured = new Response(response.body, response);
  secured.headers.set("x-content-type-options", "nosniff");
  secured.headers.set("referrer-policy", "strict-origin-when-cross-origin");
  secured.headers.set("permissions-policy", "camera=(), geolocation=(), payment=(), usb=()");
  secured.headers.set("x-frame-options", "DENY");
  secured.headers.set("cross-origin-opener-policy", "same-origin");
  secured.headers.set(
    "content-security-policy",
    "default-src 'self'; img-src 'self' data: https://*.puter.com; " +
    "style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline' https://js.puter.com; " +
    "connect-src 'self' https://seekvera-main.seekvera-global.workers.dev https://text.pollinations.ai https://*.puter.com https://nrdpyydfrpmqedtzmbyw.supabase.co; " +
    "frame-src https://*.puter.com; form-action 'self' mailto:; base-uri 'self'; object-src 'none'; frame-ancestors 'none'"
  );
  return secured;
};

function clean(value, max = 300) {
  return String(value ?? "")
    .replace(/[\u0000-\u001F\u007F]/g, " ")
    .trim()
    .slice(0, max);
}

function prohibitedReason(value) {
  const t = String(value ?? "").toLowerCase();
  const tests = [
    [/(^|\W)(gun|firearm|rifle|pistol|shotgun|ammunition|ammo|grenade|explosive|bomb|taser|switchblade|combat[ -]?knife)(?=\W|$)|سلاح|مسدس|بندقية|ذخيرة|قنبلة|متفجرات|متفجر/u, "weapons_or_explosives"],
    [/(military[ -]?(uniform|gear|weapon|weapons|tank)|army[ -]?uniform|police[ -]?uniform|battle[ -]?tank|armou?red[ -]?(vehicle|tank)|ballistic[ -]?vest|body[ -]?armou?r|زي عسكري|لباس عسكري|ملابس عسكرية|دبابة عسكرية|مدرعة|سترة واقية من الرصاص)/u, "military_or_security_items"],
    [/(^|\W)(nude|naked|porn|pornography|explicit[ -]?sexual|sexual[ -]?services?|escort[ -]?services?)(?=\W|$)|عاري|عارية|عري|إباحي|اباحي|إباحية|اباحية|خدمات جنسية/u, "explicit_sexual_content"],
    [/(^|\W)(cocaine|heroin|methamphetamine|meth|fentanyl|ecstasy|mdma|lsd|controlled[ -]?drugs?|illegal[ -]?drugs?)(?=\W|$)|كوكايين|هيروين|مخدرات|مخدر|فنتانيل|إكستاسي/u, "controlled_drugs"],
    [/(stolen[ -]?(property|goods?|phone|car|vehicle)|counterfeit|fake[ -]?(passport|id|identity|document|documents)|forged[ -]?(passport|id|document|documents)|مسروق|مسروقة|بضاعة مسروقة|مزور|مزورة|جواز مزور|هوية مزورة)/u, "stolen_counterfeit_or_fake_documents"],
    [/(human[ -]?trafficking|child[ -]?(sexual|porn|pornography)|terrorist[ -]?(material|propaganda)|extremist[ -]?(material|propaganda)|اتجار بالبشر|استغلال أطفال|مواد إرهابية|دعاية إرهابية|مواد متطرفة)/u, "severe_illegal_or_exploitative_content"]
  ];
  for (const [rx, reason] of tests) if (rx.test(t)) return reason;
  return null;
}

function requestId() {
  const date = new Date().toISOString().slice(0, 10).replaceAll("-", "");
  const token = crypto.randomUUID().replaceAll("-", "").slice(0, 8).toUpperCase();
  return `SV-${date}-${token}`;
}

function extractAIText(result) {
  if (typeof result?.response === "string") return result.response.trim();
  if (typeof result?.result?.response === "string") return result.result.response.trim();
  if (typeof result?.choices?.[0]?.message?.content === "string") return result.choices[0].message.content.trim();
  if (Array.isArray(result?.choices?.[0]?.message?.content)) return result.choices[0].message.content.map(x => x?.text || "").join("\n").trim();
  return "";
}

async function runSeekveraAI(env, messages) {
  let primaryError;
  try {
    const result = await env.AI.run(PRIMARY_AI_MODEL, { messages, max_completion_tokens: 220, temperature: 0.2 }, { rejectIfBusy: true });
    const response = extractAIText(result);
    if (response) return { response, model: PRIMARY_AI_MODEL };
    primaryError = new Error("Empty primary AI response");
  } catch (error) {
    primaryError = error;
    console.warn("SEEKVERA primary AI unavailable; trying Cloudflare fallback", error);
  }
  try {
    const result = await env.AI.run(FALLBACK_AI_MODEL, { messages, max_completion_tokens: 280, temperature: 0.22 });
    const response = extractAIText(result);
    if (response) return { response, model: FALLBACK_AI_MODEL };
    throw new Error("Empty fallback AI response");
  } catch (fallbackError) {
    console.error("SEEKVERA Cloudflare AI models unavailable", { primaryError, fallbackError });
    throw fallbackError;
  }
}

async function saveRequestToSupabase(payload) {
  const response = await fetch(`${SUPABASE_URL}/rest/v1/seekvera_requests`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "apikey": SUPABASE_PUBLISHABLE_KEY,
      "authorization": `Bearer ${SUPABASE_PUBLISHABLE_KEY}`,
      "prefer": "return=minimal"
    },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    const detail = (await response.text()).slice(0, 500);
    throw new Error(`Supabase request storage failed (${response.status}): ${detail}`);
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname.startsWith("/api/")) {
      if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: corsHeaders(request) });

      if (url.pathname === "/api/health") {
        return json(request, {
          ok: true,
          service: "SEEKVERA",
          aiBinding: Boolean(env.AI),
          moderation: "enabled",
          requestStorage: "supabase",
          requestStorageReady: true,
          primaryModel: PRIMARY_AI_MODEL,
          fallbackModel: FALLBACK_AI_MODEL
        });
      }

      if (url.pathname === "/api/moderate") {
        if (request.method !== "POST") return json(request, { ok: false, error: "Method not allowed" }, 405);
        try {
          const contentLength = Number(request.headers.get("content-length") || 0);
          if (contentLength > 16000) return json(request, { ok: false, error: "Request too large" }, 413);
          const body = await request.json();
          const text = clean(body?.text ?? [body?.title, body?.description, body?.category].filter(Boolean).join(" "), 6500);
          if (!text) return json(request, { ok: false, error: "Text is required" }, 400);

          const deterministic = prohibitedReason(text);
          if (deterministic) return json(request, { ok: true, allowed: false, reviewRequired: true, reason: deterministic, source: "rules" });

          if (!env.AI) return json(request, { ok: true, allowed: true, reviewRequired: true, reason: "ai_unavailable_manual_review_required", source: "rules" });

          const system = [
            "You are SEEKVERA marketplace safety moderation.",
            "Classify only whether a proposed marketplace ad is safe to accept into a pending review queue.",
            "Block weapons, ammunition, explosives, military or police uniforms/gear, armored combat vehicles, explicit nudity or pornography, sexual services, controlled or recreational drugs, stolen or counterfeit goods, fake identity documents, scams or fraud, human trafficking, child sexual content, extremist or terrorist merchandise/propaganda, doxxing/private personal data, and clearly illegal goods or services.",
            "If the text claims an item/property belongs to someone else, is posted without permission, or shows private people without consent, block it.",
            "If ownership/permission simply cannot be verified from text, do not block solely for that; require human review.",
            "Return exactly one line in this format: ALLOW|REVIEW or BLOCK|short_reason."
          ].join(" ");
          const ai = await runSeekveraAI(env, [{ role: "system", content: system }, { role: "user", content: text }]);
          const out = ai.response.replace(/\s+/g, " ").trim();
          if (/^BLOCK\|/i.test(out)) return json(request, { ok: true, allowed: false, reviewRequired: true, reason: out.split("|").slice(1).join("|").slice(0, 120) || "ai_safety_block", source: "ai" });
          return json(request, { ok: true, allowed: true, reviewRequired: true, reason: "pending_human_review", source: "ai" });
        } catch (error) {
          console.error("SEEKVERA moderation error", error);
          return json(request, { ok: true, allowed: true, reviewRequired: true, reason: "moderation_unavailable_manual_review_required", source: "fallback" });
        }
      }

      if (url.pathname === "/api/request") {
        if (request.method !== "POST") return json(request, { ok: false, error: "Method not allowed" }, 405);
        try {
          const contentLength = Number(request.headers.get("content-length") || 0);
          if (contentLength > 16000) return json(request, { ok: false, error: "Request too large" }, 413);

          const body = await request.json();
          const country = clean(body?.country, 120);
          const city = clean(body?.city, 120);
          const type = clean(body?.type ?? body?.request_type, 80) || "Other";
          const budget = clean(body?.budget, 120);
          const requestedDate = clean(body?.date ?? body?.needed_date, 30);
          const contact = clean(body?.contact, 240);
          const description = clean(body?.description, 4000);
          const honeypot = clean(body?.website, 200);

          if (honeypot) return json(request, { ok: true, accepted: true });
          if (!country || description.length < 3) return json(request, { ok: false, error: "Country and description are required" }, 400);

          const reason = prohibitedReason([type, description, budget, city, country].join(" "));
          if (reason) return json(request, { ok: false, blocked: true, error: "This request is not allowed on SEEKVERA.", reason }, 422);

          const id = requestId();
          const neededDate = /^\d{4}-\d{2}-\d{2}$/.test(requestedDate) ? requestedDate : null;
          await saveRequestToSupabase({ reference: id, country, city, request_type: type, budget, needed_date: neededDate, contact, description, source: "seekvera-worker" });
          return json(request, { ok: true, id, createdAt: new Date().toISOString() });
        } catch (error) {
          console.error("SEEKVERA request storage error", error);
          return json(request, { ok: false, error: "Unable to save request right now", retryable: true }, 503);
        }
      }

      if (url.pathname === "/api/ai") {
        if (request.method !== "POST") return json(request, { ok: false, error: "Method not allowed" }, 405);
        try {
          const contentLength = Number(request.headers.get("content-length") || 0);
          if (contentLength > 12000) return json(request, { ok: false, error: "Request too large" }, 413);

          const body = await request.json();
          const message = clean(body?.message, 1800);
          const country = clean(body?.country, 80);
          const language = clean(body?.language, 40);
          if (!message) return json(request, { ok: false, error: "Message is required" }, 400);

          const reason = prohibitedReason(message);
          if (reason) return json(request, { ok: true, blocked: true, response: "SEEKVERA cannot help buy, sell, advertise, source or promote prohibited or illegal items or services.", reason, provider: "SEEKVERA Safety" });

          if (!env.AI) return json(request, { ok: false, error: "AI binding unavailable" }, 503);

          const system = [
            "You are SEEKVERA AI, a high-quality multilingual guide inside a worldwide discovery and comparison platform.",
            "Reply in the same language as the user unless they clearly ask for another language.",
            "Understand cross-border intent naturally: a user may live in one country and want a product, property, hotel, supplier or service in another country.",
            "Help classify what they need and give practical next steps for travel, hotels, shopping, property, business software, education, solar, health services, web hosting, jobs, import/export, cars and other lawful marketplace needs.",
            "Never assist with buying, selling, advertising, sourcing or promoting weapons, ammunition, explosives, military/police gear, explicit sexual content or sexual services, controlled drugs, stolen/counterfeit goods, fake documents, scams/fraud, trafficking, extremist/terrorist merchandise, privacy abuse, or clearly illegal goods/services. Refuse briefly and redirect to lawful alternatives.",
            "Never invent a live price, availability, provider approval, discount, booking, job opening, medical diagnosis, legal guarantee, or affiliate relationship.",
            "Do not call any provider a SEEKVERA partner unless verified partner data is actually supplied to you.",
            "When current provider data is unavailable, say that clearly and guide the user to SEEKVERA search, live web search, maps, or Request Anything.",
            "For location-sensitive requests, distinguish the user's current location from the destination they are asking about.",
            "Keep normal answers concise and useful. Ask at most one follow-up question only when necessary to produce a better result.",
            `Selected country: ${country || "Worldwide / not specified"}.`,
            `Selected interface language: ${language || "auto"}.`
          ].join(" ");

          const ai = await runSeekveraAI(env, [{ role: "system", content: system }, { role: "user", content: message }]);
          return json(request, { ok: true, response: ai.response, model: ai.model, provider: "Cloudflare Workers AI" });
        } catch (error) {
          console.error("SEEKVERA AI error", error);
          return json(request, { ok: false, error: "AI is temporarily unavailable", retryable: true }, 503);
        }
      }

      return json(request, { ok: false, error: "Not found" }, 404);
    }

    return secure(await env.ASSETS.fetch(request));
  }
};
