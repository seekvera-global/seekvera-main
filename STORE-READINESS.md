# SEEKVERA Store Readiness — R23

Production web app: https://seekveraglobal.com/

## Core release status
- Worldwide country profile: 248 ISO country/territory entries.
- Supported app language matrix: 98 languages.
- Country selection atomically changes country, default language and currency.
- One in-app SEEKVERA AI entry point routes users toward the appropriate department.
- Voice, visual search, marketplace safety gate, PWA manifest, privacy policy and terms are present in the production project.
- R23 removes legacy DOM-polling category/UI watchers that could cause mobile layout shaking and retires the R21 service-worker injection.

## Native store stage
The current production product is a web/PWA application. Apple App Store and Google Play publication is the next packaging/signing stage, not a change to the production website. Before store submission we must provide or confirm:
1. Apple Developer and Google Play Console account ownership (individual or company).
2. Final legal publisher/company name, address, support email and privacy contact.
3. Final Android application ID and iOS bundle ID (recommended namespace to reserve: `com.seekvera.global`).
4. Native signing credentials generated inside the relevant store/developer accounts.
5. Store icon/screenshots, age/content declarations, data-safety/privacy answers and final listing copy.
6. Native wrapper/package build and device testing for Android and iOS.

## Autonomous company-email stage
The Deal Agent mission/database UI is intentionally safe-by-default. Autonomous outbound email is not declared active until a secure mail provider/OAuth connection and scheduled queue/worker are connected. No user password, OTP, PIN or CVV should ever be stored for this purpose. This external authorization is required before SEEKVERA can truthfully claim unattended email sending.

R23 is the production-stability release used as the baseline for the native-store stage.
