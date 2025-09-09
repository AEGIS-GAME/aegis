import { Button } from "@/components/ui/button"
import { ReactNode } from "react"

interface ErrorMessageProps {
  title: string
  message: string
  actionText?: string
  onAction?: () => void
  children?: ReactNode
}

export function ErrorMessage({
  title,
  message,
  actionText,
  onAction,
  children,
}: ErrorMessageProps): JSX.Element {
  return (
    <div className="p-4 bg-red-50 border border-red-200 rounded-md">
      <div className="flex">
        <div className="ml-3">
          <h3 className="text-sm font-medium text-red-800">{title}</h3>
          <div className="mt-2 text-sm text-red-700">
            <p>{message}</p>
          </div>
          {children}
          {actionText && onAction && (
            <div className="mt-4">
              <Button type="button" variant="outline" size="sm" onClick={onAction}>
                {actionText}
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
