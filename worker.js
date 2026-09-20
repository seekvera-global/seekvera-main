const json = (data, status = 200) => new Response(JSON.stringify(data), {
  status,
  headers: {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store",
    "x-content-type-options": "nosniff"
  }
});

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/api/ai") {
      if (request.method !== "POST") {
        return json({ ok: false, error: "Method not allowed" }, 405);
      }

      try {
        const contentLength = Number(request.headers.get("content-length") || 0);
        if (contentLength > 12000) {
          return json({ ok: false, error: "Request too large" }, 413);
        }

        const body = await request.json();
        const message = String(body?.message || "").trim().slice(0, 1800);
        const country = String(body?.country || "").trim().slice(0, 80);
        const language = String(body?.language || "").trim().slice(0, 40);

        if (!message) {
          return json({ ok: false, error: "Message is required" }, 400);
        }

        const system = [
          "You are SEEKVERA AI, the concise multilingual guide inside a global discovery and comparison website.",
          "Reply in the same language as the user unless they clearly ask for another language.",
          "Help classify what they need and give practical next steps for travel, hotels, shopping, property, business software, education, solar, health services, web hosting, jobs, import/export, cars and other marketplace needs.",
          "Never invent a live price, availability, provider approval, discount, booking, job opening, medical diagnosis, legal guarantee, or affiliate relationship.",
          "If current provider data is not available, say that clearly and tell the user what details to enter in SEEKVERA search or Request Anything.",
          "Keep normal answers short: usually 2 to 5 sentences. Ask at most one useful follow-up question when necessary.",
          `Selected country: ${country || "not specified"}.`,
          `Selected interface language: ${language || "not specified"}.`
        ].join(" ");

        const result = await env.AI.run("@cf/zai-org/glm-4.7-flash", {
          messages: [
            { role: "system", content: system },
            { role: "user", content: message }
          ],
          max_completion_tokens: 220,
          temperature: 0.25
        });

        const response = typeof result?.response === "string"
          ? result.response.trim()
          : typeof result?.result?.response === "string"
            ? result.result.response.trim()
            : "";

        if (!response) {
          return json({ ok: false, error: "AI response unavailable" }, 503);
        }

        return json({ ok: true, response, model: "glm-4.7-flash" });
      } catch (error) {
        console.error("SEEKVERA AI error", error);
        return json({ ok: false, error: "AI is temporarily unavailable" }, 503);
      }
    }

    return env.ASSETS.fetch(request);
  }
};
