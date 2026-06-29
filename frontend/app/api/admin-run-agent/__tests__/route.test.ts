/**
 * @jest-environment node
 */

import { POST } from "../route";

describe("POST /api/admin-run-agent", () => {
  const originalFetch = global.fetch;

  afterEach(() => {
    global.fetch = originalFetch;
    jest.restoreAllMocks();
  });

  it("forwards a successful admin agent run response through a route outside /api/admin", async () => {
    const backendBody = '{"job_id":"job-123","status":"pending"}';
    global.fetch = jest.fn().mockResolvedValue(
      new Response(backendBody, {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    const request = new Request("http://localhost/api/admin-run-agent", {
      method: "POST",
      headers: { Authorization: "Bearer admin-token", "Content-Type": "application/json" },
      body: JSON.stringify({
        agent_id: "ugc_media_agent",
        prompt: "Create a product video",
        context: { media_request: { video_quality: "720p" } },
      }),
    });

    const response = await POST(request as never);

    expect(global.fetch).toHaveBeenCalledWith(
      "https://api.vantro.ai/api/admin/agents/ugc_media_agent/run",
      {
        method: "POST",
        headers: { Authorization: "Bearer admin-token", "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: "Create a product video",
          context: { media_request: { video_quality: "720p" } },
        }),
      },
    );
    expect(response.status).toBe(200);
    expect(response.headers.get("content-type")).toContain("application/json");
    expect(await response.text()).toBe(backendBody);
  });

  it("rejects missing agent IDs before calling the backend", async () => {
    global.fetch = jest.fn();

    const request = new Request("http://localhost/api/admin-run-agent", {
      method: "POST",
      headers: { Authorization: "Bearer admin-token", "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: "Create a product video" }),
    });

    const response = await POST(request as never);

    expect(global.fetch).not.toHaveBeenCalled();
    expect(response.status).toBe(400);
    expect(await response.json()).toEqual({ error: "Missing agent_id" });
  });

  it("falls back to the standard agent run endpoint when the admin backend route fails", async () => {
    const backendBody = '{"job_id":"job-fallback","status":"pending_approval"}';
    global.fetch = jest
      .fn()
      .mockResolvedValueOnce(
        new Response("Internal Server Error", {
          status: 500,
          headers: { "Content-Type": "text/plain" },
        }),
      )
      .mockResolvedValueOnce(
        new Response(backendBody, {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      );

    const request = new Request("http://localhost/api/admin-run-agent", {
      method: "POST",
      headers: { Authorization: "Bearer admin-token", "Content-Type": "application/json" },
      body: JSON.stringify({
        agent_id: "ugc_media_agent",
        prompt: "Create a product video",
        context: { media_request: { video_quality: "720p" } },
      }),
    });

    const response = await POST(request as never);

    expect(global.fetch).toHaveBeenNthCalledWith(
      1,
      "https://api.vantro.ai/api/admin/agents/ugc_media_agent/run",
      expect.any(Object),
    );
    expect(global.fetch).toHaveBeenNthCalledWith(
      2,
      "https://api.vantro.ai/api/agents/ugc_media_agent/run",
      {
        method: "POST",
        headers: { Authorization: "Bearer admin-token", "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: "Create a product video",
          context: { media_request: { video_quality: "720p" } },
        }),
      },
    );
    expect(response.status).toBe(200);
    expect(await response.text()).toBe(backendBody);
  });
});
