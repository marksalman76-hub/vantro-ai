import { readFileSync } from "fs";
import { join } from "path";

const publicFacingFiles = [
  "app/create/page.tsx",
  "app/error.tsx",
  "app/not-found.tsx",
];

describe("public-facing dashboard CTA safety", () => {
  it("does not expose direct dashboard CTAs on public-facing pages", () => {
    for (const file of publicFacingFiles) {
      const source = readFileSync(join(process.cwd(), file), "utf8");

      expect(source).not.toContain('href="/dashboard"');
      expect(source).not.toContain("href='/dashboard'");
      expect(source).not.toMatch(/View in dashboard|Go to dashboard|Back to dashboard|>Dashboard</);
    }
  });
});
