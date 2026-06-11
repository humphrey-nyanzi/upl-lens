import type { ReactNode } from "react";

type DisclosureSectionProps = {
  children: ReactNode;
  className?: string;
  defaultOpen?: boolean;
  description?: string;
  eyebrow?: string;
  title: string;
};

export function DisclosureSection({
  children,
  className = "panel",
  defaultOpen = false,
  description,
  eyebrow,
  title,
}: DisclosureSectionProps) {
  return (
    <section className={`disclosure-section ${className}`}>
      <details {...(defaultOpen ? { open: true } : {})}>
        <summary>
          <span>
            {eyebrow ? <small>{eyebrow}</small> : null}
            <strong>{title}</strong>
            {description ? <em>{description}</em> : null}
          </span>
        </summary>
        <div className="disclosure-section-body">{children}</div>
      </details>
    </section>
  );
}
