import type { ReactNode } from 'react'

interface SectionCardProps {
  icon: string
  title: string
  children: ReactNode
  delay?: number
  className?: string
}

export default function SectionCard({ icon, title, children, delay = 0, className = '' }: SectionCardProps) {
  return (
    <section
      className={`animate-fade-in rounded-xl border bg-[var(--card)] p-5 shadow-sm transition-all duration-300 hover:shadow-md ${className}`}
      style={{ animationDelay: `${delay}ms`, animationFillMode: 'both' }}
    >
      <div className="mb-4 flex items-center gap-2.5">
        <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--primary)]/10 text-base">
          {icon}
        </span>
        <h2 className="text-sm font-semibold text-[var(--card-foreground)]">{title}</h2>
      </div>
      {children}
    </section>
  )
}
