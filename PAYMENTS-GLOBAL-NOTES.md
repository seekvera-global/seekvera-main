# SEEKVERA Global Payment Requirements

Last verified: 2026-09-21

## Product rule
- SEEKVERA must remain worldwide and should not present the payment experience as Nigeria-only.
- Do not hard-code NGN-only pricing on public global plan pages.
- Final plan prices will be set later.
- Checkout should support global cardholders and present suitable payment methods by market when the chosen gateway supports them.

## Payoneer facts verified from Payoneer public documentation
- Payoneer Checkout states support for Visa, Mastercard and American Express plus local payment methods, across 120+ supported currencies.
- Customers do not need a Payoneer account to pay through Payoneer Checkout.
- Availability varies by integration, market, jurisdiction and merchant eligibility.
- Payoneer Checkout is not simply guaranteed for every Nigerian merchant/account. Current Payoneer disclosures state jurisdiction/entity eligibility restrictions, including US/Hong Kong-related Checkout availability and eligibility conditions.
- Payoneer Payment Request supports credit/debit card payments by Mastercard, Visa and American Express for eligible commercial payment requests, with additional methods depending on market.
- Standalone Verve is NOT listed by Payoneer as a supported card brand in the official material reviewed. Do not promise Verve support unless Payoneer explicitly confirms it for our merchant setup.
- A card denominated in a local currency can still be used when its issuing bank/network permits the international or cross-currency transaction; acceptance and conversion depend on the issuer, card network, merchant setup and supported transaction currency.

## Implementation requirement before activating paid plans
1. Confirm SEEKVERA merchant eligibility for Payoneer Checkout using the actual legal entity/account that will receive funds.
2. Confirm exact supported countries, transaction currencies and settlement currencies for that account.
3. Confirm whether Verve or another local payment method is available for Nigeria; do not infer it from Visa/Mastercard support.
4. Keep the site payment layer gateway-agnostic so a second gateway can be added if Payoneer cannot cover a required market/card network.
5. Only then activate prices, subscriptions, boosts and automatic payment confirmation.

## Important distinction
Payoneer account receiving features, Payment Request, and Payoneer Checkout are different products with different eligibility and permitted use cases. Do not treat a normal Payoneer receiving account as automatically equivalent to an embedded consumer checkout gateway.
