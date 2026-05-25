import { useEffect, useState } from "react";

import { parsePageHash } from "../app/pages";
import type { PageKey } from "../app/types";

export function useHashNavigation() {
  const [currentPage, setCurrentPage] = useState<PageKey>(parsePageHash);

  useEffect(() => {
    function syncPageFromHash() {
      setCurrentPage(parsePageHash());
    }

    window.addEventListener("hashchange", syncPageFromHash);
    return () => window.removeEventListener("hashchange", syncPageFromHash);
  }, []);

  function setPage(page: PageKey) {
    window.location.hash = `/${page}`;
    setCurrentPage(page);
  }

  return { currentPage, setPage };
}
