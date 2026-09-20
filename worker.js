const ALLOWED_ORIGINS = new Set([
  "https://seekvera-global.github.io",
  "https://seekvera-main.seekvera-global.workers.dev"
]);

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
  secured.headers.set("content-security-policy", "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self' https://seekvera-main.seekvera-global.workers.dev; form-action 'self' mailto:; base-uri 'self'; frame-ancestors 'none'");
  return secured;
};

function clean(value, max = 300) {
  return String(value ?? "").replace(/[\u0000-\u001F\u007F]/g, " ").trim().slice(0, max);
}

function requestId() {
  const date = new Date().toISOString().slice(0, 10).replaceAll("-", "");
  const token = crypto.randomUUID().replaceAll("-", "").slice(0, 8).toUpperCase();
  return `SV-${date}-${token}`;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname.startsWith("/api/")) {
      if (request.method === "OPTIONS") {
        return new Response(null, { status: 204, headers: corsHeaders(request) });
      }

      if (url.pathname === "/api/health") {
        return json(request, {
          ok: true,
          service: "SEEKVERA",
          aiBinding: Boolean(env.AI),
          requestsDbBinding: Boolean(env.REQUESTS_DB),
          model: "@cf/zai-org/glm-4.7-flash"
        });
      }

      if (url.pathname === "/api/request") {
        if (request.method !== "POST") {
          return json(request, { ok: false, error: "Method not allowed" }, 405);
        }

        try {
          const contentLength = Number(request.headers.get("content-length") || 0);
          if (contentLength > 16000) {
            return json(request, { ok: false, error: "Request too large" }, 413);
          }

          const body = await request.json();
          const country = clean(body?.country, 100);
          const city = clean(body?.city, 120);
          const type = clean(body?.type, 60) || "Other";
          const budget = clean(body?.budget, 120);
          const requestedDate = clean(body?.date, 30);
          const contact = clean(body?.contact, 180);
          const description = clean(body?.description, 2500);
          const honeypot = clean(body?.website, 200);

          if (honeypot) {
            return json(request, { ok: true, accepted: true });
          }
          if (!country || !description) {
            return json(request, { ok: false, error: "Country and description are required" }, 400);
          }
          if (!env.REQUESTS_DB) {
            return json(request, { ok: false, error: "Request storage is not connected yet", storageReady: false }, 503);
          }

          const id = requestId();
          const createdAt = new Date().toISOString();
          await env.REQUESTS_DB.prepare(
            `INSERT INTO requests (id, created_at, country, city, request_type, budget, requested_date, contact, description, status, source)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, 'new', 'web')`
          ).bind(id, createdAt, country, city, type, budget, requestedDate, contact, description).run();

          return json(request, { ok: true, id, createdAt });
        } catch (error) {
          console.error("SEEKVERA request storage error", error);
          return json(request, { ok: false, error: "Unable to save request right now", retryable: true }, 503);
        }
      }

      if (url.pathname === "/api/ai") {
        if (request.method !== "POST") {
          return json(request, { ok: false, error: "Method not allowed" }, 405);
        }

        try {
          const contentLength = Number(request.headers.get("content-length") || 0);
          if (contentLength > 12000) {
            return json(request, { ok: false, error: "Request too large" }, 413);
          }

          const body = await request.json();
          const message = String(body?.message || "").trim().slice(0, 1800);
          const country = String(body?.country || "").trim().slice(0, 80);
          const language = String(body?.language || "").trim().slice(0, 40);

          if (!message) {
            return json(request, { ok: false, error: "Message is required" }, 400);
          }

          if (!env.AI) {
            return json(request, { ok: false, error: "AI binding unavailable" }, 503);
          }

          const system = [
            "You are SEEKVERA AI, a concise multilingual guide inside a global discovery and comparison website.",
            "Reply in the same language as the user unless they clearly ask for another language.",
            "Help classify what they need and give practical next steps for travel, hotels, shopping, property, business software, education, solar, health services, web hosting, jobs, import/export, cars and other lawful marketplace needs.",
            "Never invent a live price, availability, provider approval, discount, booking, job opening, medical diagnosis, legal guarantee, or affiliate relationship.",
            "When the user asks for a product or service from another country, explain the best search route and the details they should provide, including destination, budget, quantity or dates when relevant.",
            "If current provider data is not available, say that clearly and tell the user what details to enter in SEEKVERA search or Request Anything.",
            "Keep normal answers short and useful: usually 2 to 5 sentences. Ask at most one useful follow-up question when necessary.",
            `Selected country: ${country || "not specified"}.`,
            `Selected interface language: ${language || "not specified"}.`
          ].join(" ");

          const result = await env.AI.run("@cf/zai-org/glm-4.7-flash", {
            messages: [
              { role: "system", content: system },
              { role: "user", content: message }
            ],
            max_completion_tokens: 260,
            temperature: 0.25
          });

          const response = typeof result?.response === "string"
            ? result.response.trim()
            : typeof result?.result?.response === "string"
              ? result.result.response.trim()
              : "";

          if (!response) {
            return json(request, { ok: false, error: "AI response unavailable", retryable: true }, 503);
          }

          return json(request, { ok: true, response, model: "glm-4.7-flash" });
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
