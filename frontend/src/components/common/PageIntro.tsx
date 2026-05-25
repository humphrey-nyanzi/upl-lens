import type { ReactNode } from "react";

type PageIntroProps = {
  children?: ReactNode;
  eyebrow: string;
  text: string;
  title: string;
};

export function PageIntro({ children, eyebrow, text, title }: PageIntroProps) {
  return (
    <section className="page-intro">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p>{text}</p>
      </div>
      {children}
    </section>
  );
}
