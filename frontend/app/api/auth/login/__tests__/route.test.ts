/**
 * @jest-environment node
 */

import { POST } from "../route";

describe("POST /api/auth/login", () => {
  const originalFetch = global.fetch;

  afterEach(() => {
    global.fetch = originalFetch;
    jest.restoreAllMocks();
  });

  it("preserves the backend access_token for admin login consumers", async () => {
    global.fetch = jest.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          access_token: "backend-access-token",
          token_type: "bearer",
          user_id: "user-123",
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        },
      ),
    );

    const request = new Request("http://localhost/api/auth/login", {
      method: "POST",
      body: JSON.stringify({
        email: "mark.salman76@gmail.com",
        password: "Admin123",
      }),
    });

    const response = await POST(request as never);
    const body = await response.json();

    expect(response.status).toBe(200);
    expect(body).toEqual({
      access_token: "backend-access-token",
      token: "backend-access-token",
      user_id: "user-123",
    });
  });

  it("returns detail when the backend login request fails before a response", async () => {
    global.fetch = jest.fn().mockRejectedValue(new Error("connect ECONNREFUSED"));

    const request = new Request("http://localhost/api/auth/login", {
      method: "POST",
      body: JSON.stringify({
        email: "mark.salman76@gmail.com",
        password: "Admin123",
      }),
    });

    const response = await POST(request as never);
    const body = await response.json();

    expect(response.status).toBe(500);
    expect(body).toEqual({
      detail: "Internal server error",
      error: "Internal server error",
    });
  });
});
