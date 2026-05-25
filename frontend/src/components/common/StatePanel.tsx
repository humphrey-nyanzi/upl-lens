type StatePanelProps = {
  message: string;
  title: string;
  tone?: "neutral" | "error";
};

export function StatePanel({ message, title, tone = "neutral" }: StatePanelProps) {
  return (
    <section className={`state-panel ${tone}`} role={tone === "error" ? "alert" : undefined}>
      <span>{tone === "error" ? "Needs attention" : "Data state"}</span>
      <h2>{title}</h2>
      <p>{message}</p>
    </section>
  );
}
