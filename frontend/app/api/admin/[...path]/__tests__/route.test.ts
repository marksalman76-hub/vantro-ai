/**
 * @jest-environment node
 */

import { POST } from "../route";
import { NextRequest } from "next/server";

describe("POST /api/admin/[...path]", () => {
  const originalFetch = global.fetch;

  afterEach(() => {
    global.fetch = originalFetch;
    jest.restoreAllMocks();
  });

  it("does not convert an empty successful backend JSON response into a 500", async () => {
    global.fetch = jest.fn().mockResolvedValue(
      new Response("", {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    const request = new NextRequest("http://localhost/api/admin/agents/ugc_media_agent/run", {
      method: "POST",
      headers: { Authorization: "Bearer admin-token", "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: "Create a video" }),
    });

    const response = await POST(request, {
      params: Promise.resolve({ path: ["agents", "ugc_media_agent", "run"] }),
    });

    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({ ok: true, status: 200 });
  });
});
