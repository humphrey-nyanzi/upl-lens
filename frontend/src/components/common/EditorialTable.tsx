import type { ReactNode } from "react";

type EditorialTableProps = {
  children: ReactNode;
  className?: string;
};

type EditorialTableHeaderProps = {
  className?: string;
  columns: Array<{ align?: "left" | "right" | "center"; label: string }>;
};

export function EditorialTable({ children, className }: EditorialTableProps) {
  const classes = ["editorial-table-shell", className].filter(Boolean).join(" ");
  return <div className={classes}>{children}</div>;
}

export function EditorialTableHeader({ className, columns }: EditorialTableHeaderProps) {
  const classes = ["editorial-table-header", className].filter(Boolean).join(" ");

  return (
    <div className={classes} aria-hidden="true">
      {columns.map((column) => (
        <span className={column.align ? `is-${column.align}` : ""} key={column.label}>
          {column.label}
        </span>
      ))}
    </div>
  );
}
