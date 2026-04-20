import type { ButtonHTMLAttributes, ReactElement } from 'react'
import clsx from 'clsx'
import s from './IconButton.module.scss'

type IconButtonProps = {
  icon: ReactElement
} & ButtonHTMLAttributes<HTMLButtonElement>

export default function IconButton({ icon, className, ...rest }: IconButtonProps) {
  return (
    <button {...rest} className={clsx(s.iconButton, className)}>
      {icon}
    </button>
  )
}
