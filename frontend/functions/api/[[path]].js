const API_ORIGIN = "https://upl-match-intelligence-api.onrender.com";

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

  const response = await fetch(upstreamUrl.toString(), init);
  const responseHeaders = new Headers(response.headers);
  responseHeaders.set("cache-control", "no-store");

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: responseHeaders,
  });
}
