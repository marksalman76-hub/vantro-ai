import * as Sentry from "@sentry/nextjs";

const SENTRY_DSN = process.env.SENTRY_DSN;

if (SENTRY_DSN) {
  Sentry.init({
    dsn: SENTRY_DSN,
    environment: process.env.NEXT_PUBLIC_ENVIRONMENT || "production",
    tracesSampleRate: 0.2,
    // Server-side: no replay
  });
}
