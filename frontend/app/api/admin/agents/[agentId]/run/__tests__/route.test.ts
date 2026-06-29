/**
 * @jest-environment node
 */

import { POST } from "../route";

describe("POST /api/admin/agents/[agentId]/run", () => {
  const originalFetch = global.fetch;

  afterEach(() => {
    global.fetch = originalFetch;
    jest.restoreAllMocks();
  });

  it("forwards a successful backend JSON response without parsing it first", async () => {
    const backendBody = '{"job_id":"job-123","status":"pending"}';
    global.fetch = jest.fn().mockResolvedValue(
      new Response(backendBody, {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    const request = new Request("http://localhost/api/admin/agents/ugc_media_agent/run", {
      method: "POST",
      headers: { Authorization: "Bearer admin-token", "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: "Create a product video" }),
    });

    const response = await POST(request as never, {
      params: Promise.resolve({ agentId: "ugc_media_agent" }),
    });

    expect(response.status).toBe(200);
    expect(response.headers.get("content-type")).toContain("application/json");
    expect(await response.text()).toBe(backendBody);
  });

  it("turns an empty successful backend response into safe JSON", async () => {
    global.fetch = jest.fn().mockResolvedValue(
      new Response("", {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    const request = new Request("http://localhost/api/admin/agents/ugc_media_agent/run", {
      method: "POST",
      headers: { Authorization: "Bearer admin-token", "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: "Create a product video" }),
    });

    const response = await POST(request as never, {
      params: Promise.resolve({ agentId: "ugc_media_agent" }),
    });

    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({ ok: true, status: 200 });
  });
});
