import type { ReactNode } from 'react';
import cls from './Container.module.scss';

export type ContainerProps = {
  children: ReactNode;
  className?: string;
};

export function Container({ children, className }: ContainerProps) {
  const classes = className ? `${cls.container} ${className}` : cls.container;

  return <div className={classes}>{children}</div>;
}
