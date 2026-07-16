import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { testExports } from "./[[path]].js";

const { cacheSecondsFor, canUseEdgeCache, withCacheHeaders } = testExports;

describe("Cloudflare API proxy cache contract", () => {
  it("keeps public cache headers for unauthenticated cacheable GET misses", () => {
    const response = withCacheHeaders(new Response("ok", { status: 200 }), "health", "MISS");

    assert.equal(response.headers.get("x-upl-lens-cache"), "MISS");
    assert.equal(
      response.headers.get("cache-control"),
      "public, max-age=60, s-maxage=60, stale-while-revalidate=60",
    );
  });

  it("bypasses edge cache for credentialed cacheable requests", () => {
    const authorizedRequest = new Request("https://upl-lens.pages.dev/api/health", {
      headers: { authorization: "Bearer test-token" },
    });
    const cookieRequest = new Request("https://upl-lens.pages.dev/api/health", {
      headers: { cookie: "session=test" },
    });

    assert.equal(cacheSecondsFor("health"), 60);
    assert.equal(canUseEdgeCache(authorizedRequest, "health"), false);
    assert.equal(canUseEdgeCache(cookieRequest, "health"), false);
  });

  it("marks credentialed BYPASS responses private by using no-store", () => {
    const upstream = new Response("ok", {
      status: 200,
      headers: { "set-cookie": "session=test" },
    });

    const response = withCacheHeaders(upstream, "health", "BYPASS");

    assert.equal(response.headers.get("x-upl-lens-cache"), "BYPASS");
    assert.equal(response.headers.get("cache-control"), "no-store");
    assert.equal(response.headers.has("set-cookie"), false);
  });

  it("keeps non-cacheable paths no-store even when upstream succeeds", () => {
    const response = withCacheHeaders(new Response("ok", { status: 200 }), "admin/private", "BYPASS");

    assert.equal(response.headers.get("x-upl-lens-cache"), "BYPASS");
    assert.equal(response.headers.get("cache-control"), "no-store");
  });
});
