import type { ReactNode } from "react";

type PageIntroVariant = "dense" | "hero";

type PageIntroProps = {
  children?: ReactNode;
  eyebrow: string;
  text: string;
  title: string;
  variant: PageIntroVariant;
};

export function PageIntro({ children, eyebrow, text, title, variant }: PageIntroProps) {
  const isHero = variant === "hero";
  const className = ["page-intro", `page-intro-${variant}`, isHero ? "lens-fused-hero" : null].filter(Boolean).join(" ");
  const copyClassName = ["page-intro-copy", isHero ? "lens-fused-hero-copy" : null].filter(Boolean).join(" ");

  return (
    <section className={className}>
      <div className={copyClassName}>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p>{text}</p>
      </div>
      {children}
    </section>
  );
}
