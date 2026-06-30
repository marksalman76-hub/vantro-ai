/**
 * @jest-environment node
 */

import { existsSync, readFileSync } from "node:fs";
import path from "node:path";

const frontendRoot = path.resolve(__dirname, "../../../../..");

function readFrontendFile(relativePath: string) {
  return readFileSync(path.join(frontendRoot, relativePath), "utf8");
}

describe("Next.js warning regressions", () => {
  it("keeps login route CSRF handling out of ignored route config exports", () => {
    const source = readFrontendFile("app/api/auth/login/route.ts");

    expect(source).not.toMatch(/export\s+const\s+config\b/);
    expect(source).not.toContain("skipCsrfProtection");
  });

  it("uses the Next 16 proxy convention instead of deprecated middleware.ts", () => {
    const proxySource = readFrontendFile("proxy.ts");

    expect(existsSync(path.join(frontendRoot, "middleware.ts"))).toBe(false);
    expect(proxySource).toMatch(/export\s+function\s+proxy\b/);
    expect(proxySource).toMatch(/matcher:/);
  });

  it("pins Turbopack to the frontend package root when repo tooling has its own lockfile", () => {
    const configSource = readFrontendFile("next.config.js");

    expect(configSource).toContain("turbopack");
    expect(configSource).toContain("root:");
    expect(configSource).toContain("__dirname");
  });
});
