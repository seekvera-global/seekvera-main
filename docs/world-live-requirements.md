# World Live — approved scope and current implementation

The user authorized adding World Live to SEEKVERA on 12 October 2026.

## Implemented in the staged feature

- Reuses the app country and language controls; country changes propagate through the app locale state.
- 15 sourced public camera locations, city/area filtering, camera selection, and 69 provider country directories. Countries without catalogue entries have an explicit empty state.
- Camera source, timezone and local time. Maps show approximate area centres and label them as such.
- HTTPS provider links only. No rebroadcasting, private-camera discovery, scraped stream endpoints or unsupported embed permissions.
- A source-page HTTP check never asserts that the camera is live. Playback status remains unknown; providers control playback.
- Official USGS earthquake and GDACS natural-disaster reports within 500 km of the selected camera area, including timestamps, expiration and partial-provider/outage handling.
- AI routes direct public-camera requests to the page; the frontend preserves the query and infers supported camera locations. Country search does not issue an app country-change command.
- English, Arabic and French reviewed labels. Other app languages use complete label batches from the existing translation service; the page hides its content until a whole label pack is available.
- Mobile and RTL styles, native labelled controls, keyboard focus, safe external links and accessible status regions.

## Validation completed

The World Live test checks catalogue integrity, allowlisted URLs, country/city and unavailable-country filtering, area-map bounds, timezone formatting, stale/future/untrusted events, partial feeds, full outages, HTTP reachability versus stream state, Worker CORS integration and multilingual AI routing. Existing direct-voice and dialect tests pass with the new route.

Fresh USGS and GDACS feeds were parsed against all 15 camera areas. Source checks distinguish environment network blocks from unavailable cameras; no check certifies playback. Browser QA is unavailable in this execution environment.

## Remaining before release

- Review complete World Live translations in all 98 app languages and include these 36 new source strings in the next full-source locale inventory.
- Browser layout, keyboard, locale switching, map loading and query-routing verification; physical Android/iPhone/iPad/desktop audio tests.
- Permission and explicit provider support for any future in-app video embed. Current playback opens the source site.
- Broader camera catalogue and provider-specific stream-health integrations where available.
- Conflict and local emergency warnings are explicitly outside the current natural-disaster feeds.

This remains a staged feature. No production deployment of World Live or final app approval is recorded.
