import React from "react";

export function BrandLockup({ compact }: { compact?: boolean }) {
  if (compact) {
    return (
      <span className="brand-lockup-compact">
        <span className="brand-mark-compact">UPL</span>
        <span className="brand-title-compact">Lens</span>
      </span>
    );
  }

  return (
    <span className="brand-lockup-stacked">
      <span className="brand-up">UPL</span>
      <span className="brand-lens">Lens</span>
    </span>
  );
}

export default BrandLockup;
