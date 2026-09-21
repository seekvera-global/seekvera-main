# SEEKVERA

SEEKVERA is a worldwide discovery, comparison and marketplace site with a Cloudflare Worker backend.

## Production architecture

- Static marketplace and department pages are served from Cloudflare Worker Assets and mirrored on GitHub Pages.
- `worker.js` exposes `/api/health`, `/api/ai`, and `/api/request`.
- Workers AI binding: `AI`.
- Primary AI model: `@cf/google/gemma-4-26b-a4b-it`.
- AI fallback model: `@cf/zai-org/glm-4.7-flash`.
- Request and marketplace storage: Supabase project `seekvera-universal-global` with row-level security enabled.
- Public marketplace image uploads use the `marketplace-images` bucket with restricted MIME types and size limits.
- No Global API Key is stored in this repository.

## Deployment

Cloudflare Worker configuration is in `wrangler.jsonc`. A production deployment can be made with:

```bash
npx wrangler deploy
```

GitHub Actions validate the Worker source and run live production smoke tests for the AI, request storage, public pages and marketplace.
