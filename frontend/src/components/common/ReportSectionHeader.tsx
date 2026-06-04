import type { ReactNode } from "react";

type ReportSectionHeaderProps = {
  eyebrow?: string;
  title: string;
  text: string;
  children?: ReactNode;
};

export function ReportSectionHeader({ children, eyebrow, text, title }: ReportSectionHeaderProps) {
  return (
    <div className="section-heading compact report-section-heading">
      <div>
        {eyebrow ? <span className="eyebrow">{eyebrow}</span> : null}
        <h2>{title}</h2>
        <p>{text}</p>
      </div>
      {children}
    </div>
  );
}
