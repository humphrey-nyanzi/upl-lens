const API_ORIGIN = "https://upl-match-intelligence-api.onrender.com";

const CACHE_RULES = [
  { pattern: /^health$/, seconds: 60 },
  { pattern: /^seasons(?:\/overview)?$/, seconds: 600 },
  { pattern: /^trends\/seasons$/, seconds: 1800 },
  { pattern: /^overview\/intelligence$/, seconds: 600 },
  { pattern: /^insights\/goal-timing$/, seconds: 1800 },
  { pattern: /^matches(?:\/intelligence)?$/, seconds: 300 },
  { pattern: /^matches\/\d+$/, seconds: 1800 },
  { pattern: /^teams(?:\/[^/]+\/profile)?$/, seconds: 600 },
  { pattern: /^players(?:\/leaderboards|\/[^/]+)?$/, seconds: 600 },
  { pattern: /^events$/, seconds: 300 },
  { pattern: /^officials$/, seconds: 600 },
];

function cacheSecondsFor(path) {
  const normalizedPath = path.replace(/^\/+|\/+$/g, "");
  const rule = CACHE_RULES.find((candidate) => candidate.pattern.test(normalizedPath));
  return rule?.seconds ?? 0;
}

function canUseEdgeCache(request, path) {
  if (request.method !== "GET" && request.method !== "HEAD") return false;
  if (request.headers.has("authorization") || request.headers.has("cookie")) return false;
  return cacheSecondsFor(path) > 0;
}

function withCacheHeaders(response, path, cacheStatus) {
  const headers = new Headers(response.headers);
  const cacheSeconds = cacheSecondsFor(path);

  if (cacheSeconds > 0 && response.ok) {
    headers.set("cache-control", `public, max-age=60, s-maxage=${cacheSeconds}, stale-while-revalidate=60`);
  } else {
    headers.set("cache-control", "no-store");
  }

  headers.delete("set-cookie");
  headers.set("x-upl-lens-cache", cacheStatus);
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}

export async function onRequest({ request, params }) {
  const pathParam = params.path;
  const path = Array.isArray(pathParam) ? pathParam.join("/") : pathParam || "";
  const upstreamUrl = new URL(request.url);
  const apiOrigin = new URL(API_ORIGIN);
  upstreamUrl.protocol = apiOrigin.protocol;
  upstreamUrl.hostname = apiOrigin.hostname;
  upstreamUrl.pathname = `/${path}`;

  const headers = new Headers(request.headers);
  headers.delete("host");

  const init = {
    method: request.method,
    headers,
    redirect: "manual",
  };

  if (request.method !== "GET" && request.method !== "HEAD") {
    init.body = request.body;
  }

  const shouldCache = canUseEdgeCache(request, path);
  const cache = shouldCache ? caches.default : null;
  const cacheKey = shouldCache ? new Request(request.url, { method: request.method }) : null;
  if (cache && cacheKey) {
    const cachedResponse = await cache.match(cacheKey);
    if (cachedResponse) {
      return withCacheHeaders(cachedResponse, path, "HIT");
    }
  }

  const response = await fetch(upstreamUrl.toString(), init);
  const proxiedResponse = withCacheHeaders(response, path, shouldCache ? "MISS" : "BYPASS");
  if (cache && cacheKey && proxiedResponse.ok) {
    await cache.put(cacheKey, proxiedResponse.clone());
  }

  return proxiedResponse;
}

export const testExports = {
  cacheSecondsFor,
  canUseEdgeCache,
};
