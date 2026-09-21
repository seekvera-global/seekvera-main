from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"Missing expected pattern: {label}")
    return text.replace(old, new, 1)

worker_path = Path("worker.js")
worker = worker_path.read_text()

worker = replace_once(
    worker,
    'const FALLBACK_AI_MODEL = "@cf/google/gemma-4-26b-a4b-it";\n',
    'const FALLBACK_AI_MODEL = "@cf/google/gemma-4-26b-a4b-it";\nconst VISION_AI_MODEL = "@cf/meta/llama-3.2-11b-vision-instruct";\n',
    "vision model constant",
)
worker = replace_once(
    worker,
    'const token = crypto.randomUUID().replaceAll("-", "").slice(0, 8).toUpperCase();',
    'const token = crypto.randomUUID().replaceAll("-", "").slice(0, 16).toUpperCase();',
    "stronger request id",
)
worker = replace_once(
    worker,
    '          fallbackModel: FALLBACK_AI_MODEL\n',
    '          fallbackModel: FALLBACK_AI_MODEL,\n          visionModel: VISION_AI_MODEL,\n          safetyGateVersion: "2026-09-21-v2"\n',
    "health vision model",
)
worker = replace_once(
    worker,
    '          if (!env.AI) return json(request, { ok: true, allowed: true, reviewRequired: true, reason: "ai_unavailable_manual_review_required", source: "rules" });',
    '          if (!env.AI) return json(request, { ok: true, allowed: false, reviewRequired: true, reason: "ai_unavailable_hold", source: "fail-closed" });',
    "text fail closed",
)
worker = replace_once(
    worker,
    '            "Return exactly one line in this format: ALLOW|REVIEW or BLOCK|short_reason."',
    '            "Return exactly one line: ALLOW|safe, REVIEW|short_reason, or BLOCK|short_reason. Use REVIEW when uncertain, suspicious, or needing human verification."',
    "text moderation output contract",
)
old_tail = '''          if (/^BLOCK\\|/i.test(out)) return json(request, { ok: true, allowed: false, reviewRequired: true, reason: out.split("|").slice(1).join("|").slice(0, 120) || "ai_safety_block", source: "ai" });\n          return json(request, { ok: true, allowed: true, reviewRequired: true, reason: "pending_human_review", source: "ai" });\n        } catch (error) {\n          console.error("SEEKVERA moderation error", error);\n          return json(request, { ok: true, allowed: true, reviewRequired: true, reason: "moderation_unavailable_manual_review_required", source: "fallback" });\n        }\n      }\n\n      if (url.pathname === "/api/request") {'''
vision_route = '''          if (/^BLOCK\\|/i.test(out)) return json(request, { ok: true, allowed: false, reviewRequired: true, reason: out.split("|").slice(1).join("|").slice(0, 120) || "ai_safety_block", source: "ai", model: ai.model });\n          if (/^REVIEW\\|/i.test(out)) return json(request, { ok: true, allowed: true, reviewRequired: true, reason: out.split("|").slice(1).join("|").slice(0, 120) || "ai_review_required", source: "ai", model: ai.model });\n          if (/^ALLOW\\|/i.test(out)) return json(request, { ok: true, allowed: true, reviewRequired: false, reason: "safe", source: "ai", model: ai.model });\n          return json(request, { ok: true, allowed: false, reviewRequired: true, reason: "unrecognized_ai_moderation_result", source: "fail-closed", model: ai.model });\n        } catch (error) {\n          console.error("SEEKVERA moderation error", error);\n          return json(request, { ok: true, allowed: false, reviewRequired: true, reason: "moderation_unavailable_hold", source: "fail-closed" });\n        }\n      }\n\n      if (url.pathname === "/api/vision") {\n        if (request.method !== "POST") return json(request, { ok: false, error: "Method not allowed" }, 405);\n        try {\n          const contentLength = Number(request.headers.get("content-length") || 0);\n          if (contentLength > 8 * 1024 * 1024) return json(request, { ok: false, error: "Request too large" }, 413);\n          const body = await request.json();\n          const image = String(body?.image || "");\n          const context = clean(body?.context, 1500);\n          const match = image.match(/^data:(image\\/(?:jpeg|png|webp));base64,([A-Za-z0-9+/=]+)$/);\n          if (!match) return json(request, { ok: false, error: "Valid JPG, PNG or WebP image data is required" }, 400);\n          const estimatedBytes = Math.floor(match[2].length * 3 / 4);\n          if (estimatedBytes < 32 || estimatedBytes > 5 * 1024 * 1024) return json(request, { ok: false, error: "Image size is invalid" }, 413);\n          if (!env.AI) return json(request, { ok: true, allowed: false, reviewRequired: true, reason: "vision_ai_unavailable_hold", source: "fail-closed" });\n\n          const system = [\n            "You are SEEKVERA marketplace image safety moderation.",\n            "Inspect the uploaded marketplace image and decide if it may be published.",\n            "BLOCK images showing weapons, ammunition, explosives, military/police operational gear, explicit nudity or pornography, controlled drugs, fake identity documents, extremist/terrorist material, graphic exploitation, clearly stolen-goods evidence, or exposed private identity/financial documents.",\n            "REVIEW images that are ambiguous, suspicious, unreadable, heavily obscured, or where safety cannot be determined confidently.",\n            "ALLOW ordinary lawful products, property, vehicles, hotels, food, services, landscapes, and normal people when no prohibited content is visible.",\n            "Do not rely only on the accompanying text; inspect the image itself.",\n            "Return exactly one line: ALLOW|safe, REVIEW|short_reason, or BLOCK|short_reason."\n          ].join(" ");\n          const result = await env.AI.run(VISION_AI_MODEL, {\n            messages: [\n              { role: "system", content: system },\n              { role: "user", content: context ? `Listing context: ${context}` : "Review this marketplace image." }\n            ],\n            image,\n            max_tokens: 100,\n            temperature: 0\n          }, { rejectIfBusy: true });\n          const out = extractAIText(result).replace(/\\s+/g, " ").trim();\n          if (/^BLOCK\\|/i.test(out)) return json(request, { ok: true, allowed: false, reviewRequired: true, reason: out.split("|").slice(1).join("|").slice(0, 160) || "vision_safety_block", source: "ai-vision", model: VISION_AI_MODEL });\n          if (/^REVIEW\\|/i.test(out)) return json(request, { ok: true, allowed: true, reviewRequired: true, reason: out.split("|").slice(1).join("|").slice(0, 160) || "vision_review_required", source: "ai-vision", model: VISION_AI_MODEL });\n          if (/^ALLOW\\|/i.test(out)) return json(request, { ok: true, allowed: true, reviewRequired: false, reason: "safe", source: "ai-vision", model: VISION_AI_MODEL });\n          return json(request, { ok: true, allowed: false, reviewRequired: true, reason: "unrecognized_vision_result", source: "fail-closed", model: VISION_AI_MODEL });\n        } catch (error) {\n          console.error("SEEKVERA vision moderation error", error);\n          return json(request, { ok: true, allowed: false, reviewRequired: true, reason: "vision_moderation_unavailable_hold", source: "fail-closed" });\n        }\n      }\n\n      if (url.pathname === "/api/request") {'''
worker = replace_once(worker, old_tail, vision_route, "vision endpoint and fail-closed moderation")
worker_path.write_text(worker)

post_path = Path("post-ad.html")
post = post_path.read_text()
post = replace_once(
    post,
    '🛡️ SEEKVERA Safety Gate · text screening + pending review',
    '🛡️ SEEKVERA Safety Gate · AI text + AI Vision + automatic review',
    "safety badge",
)
post = replace_once(
    post,
    "MODERATION=SB+'/functions/v1/marketplace-moderate';",
    "MODERATION=SB+'/functions/v1/marketplace-moderate',REVIEW=SB+'/functions/v1/marketplace-review';",
    "review endpoint constant",
)
post = replace_once(
    post,
    "return 'SV-'+day+'-'+((a[0]^a[1])>>>0).toString(36).toUpperCase().padStart(8,'0').slice(0,8)",
    "return 'SV-'+day+'-'+(crypto.randomUUID().replaceAll('-','').slice(0,16).toUpperCase())",
    "stronger ad reference",
)
old_moderate = '''async function moderate(body){\n const text=[body.title,body.description,body.category,body.listing_type,body.country,body.city].filter(Boolean).join(' ');\n const local=localSafetyReason(text);if(local)return{allowed:false,reviewRequired:true,reason:local,source:'local-rules'};\n const payload=JSON.stringify({title:body.title,description:body.description,category:body.category,listing_type:body.listing_type,text});\n try{\n  const r=await fetch(MODERATION,{method:'POST',headers:{...H,'content-type':'application/json'},body:payload});\n  if(r.ok){const d=await r.json();if(typeof d?.allowed==='boolean')return d}\n }catch{}\n try{\n  const r=await fetch(WORKER+'/api/moderate',{method:'POST',headers:{'content-type':'application/json'},body:payload});\n  if(r.ok){const d=await r.json();if(typeof d?.allowed==='boolean')return d}\n }catch{}\n return{allowed:false,reviewRequired:true,reason:'Safety check temporarily unavailable. Please try again.',source:'fail-closed'}\n}'''
new_moderate = '''async function moderate(body){\n const text=[body.title,body.description,body.category,body.listing_type,body.country,body.city].filter(Boolean).join(' ');\n const local=localSafetyReason(text);if(local)return{allowed:false,reviewRequired:true,reason:local,source:'local-rules'};\n const payload=JSON.stringify({title:body.title,description:body.description,category:body.category,listing_type:body.listing_type,text});\n try{\n  const r=await fetch(WORKER+'/api/moderate',{method:'POST',headers:{'content-type':'application/json'},body:payload});\n  if(r.ok){const d=await r.json();if(typeof d?.allowed==='boolean')return d}\n }catch{}\n return{allowed:false,reviewRequired:true,reason:'Safety check temporarily unavailable. Please try again.',source:'fail-closed'}\n}'''
post = replace_once(post, old_moderate, new_moderate, "worker-first moderation")
old_finish = "st.textContent='Submitted. Reference: '+ad_ref+' — pending safety review and not public yet.';e.target.reset();photos.innerHTML=''"
new_finish = "st.textContent='AI Safety Gate is reviewing text and images…';let reviewStatus='pending';try{const rr=await fetch(REVIEW,{method:'POST',headers:{...H,'content-type':'application/json'},body:JSON.stringify({ad_ref})});if(rr.ok){const rd=await rr.json();reviewStatus=rd?.status||'pending';if(reviewStatus==='approved')st.textContent='Approved automatically by SEEKVERA Safety Gate. Reference: '+ad_ref;else if(reviewStatus==='rejected')st.textContent='Rejected by SEEKVERA Safety Gate. Reference: '+ad_ref;else st.textContent='Submitted safely. Reference: '+ad_ref+' — held for review and not public yet.'}else st.textContent='Submitted safely. Reference: '+ad_ref+' — held for review and not public yet.'}catch{st.textContent='Submitted safely. Reference: '+ad_ref+' — held for review and not public yet.'}e.target.reset();photos.innerHTML=''"
post = replace_once(post, old_finish, new_finish, "automatic server review trigger")
post_path.write_text(post)

print("Safety Gate v2 source patch applied successfully")
