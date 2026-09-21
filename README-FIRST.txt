SEEKVERA FINAL BUILD
This package contains the production-ready SEEKVERA website and Cloudflare Worker backend.
It includes the homepage, marketplace, department pages, shared assets, legal pages,
404 page, favicon, manifest, robots, sitemap, verification files and Cloudflare configuration.

Important:
- Search routes are live external provider/search routes.
- Real AI is connected through Cloudflare Workers AI using an AI binding.
- Primary AI model: @cf/google/gemma-4-26b-a4b-it.
- Fallback AI model: @cf/zai-org/glm-4.7-flash.
- Request Anything and marketplace data use the existing Supabase backend with RLS policies.
- Unknown searches fall back to General Search instead of a wrong department.
- No fake affiliate/tracking IDs are included. Add only real approved partner links.
- No Cloudflare Global API Key is stored in the repository.
