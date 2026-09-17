import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, apiFetch } from "./api";
import { setTokens } from "./auth";

afterEach(() => {
  vi.restoreAllMocks();
  localStorage.clear();
});

describe("apiFetch", () => {
  it("serializes JSON and adds the access token", async () => {
    setTokens({ access: "access-token", refresh: "refresh-token" });
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { "content-type": "application/json" },
    }));

    await expect(apiFetch("/health/", { method: "POST", body: { ready: true } })).resolves.toEqual({ ok: true });
    expect(fetchMock).toHaveBeenCalledWith("http://localhost:8000/api/v1/health/", expect.objectContaining({
      headers: expect.objectContaining({
        Authorization: "Bearer access-token",
        "Content-Type": "application/json",
      }),
      body: JSON.stringify({ ready: true }),
    }));
  });

  it("returns structured API errors for failed requests", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(JSON.stringify({ detail: "Denied" }), {
      status: 403,
      headers: { "content-type": "application/json" },
    }));

    await expect(apiFetch("/private/")).rejects.toEqual(expect.objectContaining({
      name: "ApiError",
      status: 403,
      data: { detail: "Denied" },
    } satisfies Partial<ApiError>));
  });
});
