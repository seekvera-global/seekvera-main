import base from './worker-r31.js';

export default {
  async fetch(request, env, ctx) {
    const ua = request.headers.get('user-agent') || '';
    if (ua.includes('SEEKVERA-R76-TRANSLATE')) {
      return new Response(JSON.stringify({ok:false,error:'translation-build-fallback-disabled'}), {
        status: 503,
        headers: {'content-type':'application/json; charset=utf-8','cache-control':'no-store'}
      });
    }
    return base.fetch(request, env, ctx);
  }
};
