# World Live — approved request, 12 October 2026

The user authorized adding World Live to SEEKVERA. This request must remain part of the overall release scope.

## Required final behavior
- Worldwide country/territory selection, city/area and camera selection, map view.
- Public authorized cameras only; permit embedding only where the provider allows it, otherwise link out.
- Never imply every country has cameras or guarantee 24/7 uptime.
- Display camera source, location, timezone, live/offline/unknown state; distinguish recorded video.
- Inherit the app country and language; support the complete app language inventory without mixed text.
- AI/voice navigation to available cameras in any supported spoken language.
- Separate official, timestamped earthquake/weather/conflict alerts from video. A quiet camera must never be interpreted as proof of safety.
- Keyboard/mobile/RTL accessibility, safe external links, no private-camera discovery.

## Current implementation and remaining work
world-live.html is an English/Arabic directory prototype, NOT the finished feature. It selects any existing app country and a city text value, but provider links deliberately open worldwide directories and do not filter by those selections. It does not embed or certify individual streams. No camera catalog, map, realtime status, official alert ingestion, AI/voice integration, or complete app-language integration exists yet. Do not announce completion or deploy this prototype as a finished release.

## Release checks
Verify provider permission and current links; unavailable-country empty state; stale/offline handling; timezones; all app locales; voice routing; malicious URL rejection; mobile/RTL/keyboard behavior; no regression of current fixed category order; official alert attribution and expiry. Confirm production deployment separately.
