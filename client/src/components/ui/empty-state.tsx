interface EmptyStateProps {
  message: string
  className?: string
}

export function EmptyState({ message, className = "" }: EmptyStateProps): JSX.Element {
  return (
    <div
      className={`text-xs text-muted-foreground text-center py-2 border border-dashed rounded ${className}`}
    >
      {message}
    </div>
  )
}
