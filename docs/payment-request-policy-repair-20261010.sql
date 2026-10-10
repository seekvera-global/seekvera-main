-- Applied in Supabase migration guard_public_payment_request_state.
-- Anonymous visitors may initiate requests; verified payment state is server controlled.
ALTER POLICY "public can create marketplace payment requests" ON public.marketplace_payment_requests WITH CHECK (status = 'initiated' AND provider_reference IS NULL AND char_length(gateway) BETWEEN 1 AND 20 AND (contact IS NULL OR char_length(contact)<=240) AND (plan_code IS NULL OR char_length(plan_code)<=120) AND (ad_ref IS NULL OR char_length(ad_ref)<=80));

-- Verification in a rollback-only transaction (does not retain test rows).
BEGIN;
SET LOCAL ROLE anon;
DO $$ BEGIN
 INSERT INTO public.marketplace_payment_requests(purpose,gateway,status,contact) VALUES ('other','paystack','initiated','SEEKVERA rollback verification');
 BEGIN
  INSERT INTO public.marketplace_payment_requests(purpose,gateway,status) VALUES ('other','paystack','paid');
  RAISE EXCEPTION 'Forged paid state was accepted';
 EXCEPTION WHEN insufficient_privilege THEN NULL; END;
 BEGIN
  INSERT INTO public.marketplace_payment_requests(purpose,gateway,status,provider_reference) VALUES ('other','paystack','initiated','forged-verification');
  RAISE EXCEPTION 'Forged provider reference was accepted';
 EXCEPTION WHEN insufficient_privilege THEN NULL; END;
END $$;
RESET ROLE;
SELECT 'PASS: initiated accepted; paid and provider-reference forgery rejected; transaction rolled back' AS result;
ROLLBACK;
