# Security Notes

MentorSLM uses bcrypt password hashing and signed JWTs. Verification codes expire after a short TTL. Demo OTP exposure is controlled by `DEV_OTP_MODE` and must be disabled in production.

For production: deliver OTPs through a verified provider, move challenges to Redis, add refresh-token rotation/revocation, enforce HTTPS at the reverse proxy, add database migrations, audit authentication events, and apply per-account lockout/backoff in addition to API rate limiting.
