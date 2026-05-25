import { API_BASE_URL } from "../../api/client";

export function ErrorPanel({ errorMessage }: { errorMessage: string }) {
  return (
    <section className="error-panel" role="alert">
      <h2>The data service is not returning data yet</h2>
      <p>{errorMessage}</p>
      <p>
        The hosted service may still be waking up. Check that the API is reachable at {API_BASE_URL}. If this only
        happens in one browser profile, a privacy or ad-blocking extension may be blocking the request.
      </p>
    </section>
  );
}
