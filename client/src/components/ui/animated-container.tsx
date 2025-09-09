import { motion } from "framer-motion"
import { ReactNode } from "react"

interface AnimatedContainerProps {
  children: ReactNode
  className?: string
  delay?: number
  onClick?: () => void
}

export function AnimatedContainer({
  children,
  className = "",
  delay = 0,
  onClick,
}: AnimatedContainerProps): JSX.Element {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      transition={{ delay }}
      className={className}
      onClick={onClick}
    >
      {children}
    </motion.div>
  )
}
