import type { ReactNode } from 'react';
import clsx from 'clsx';

import { Container } from '../Container/Container';
import s from './SectionContainer.module.scss';

type SectionContainerProps = {
  title: ReactNode;
  children: ReactNode;
  className?: string;
  innerClassName?: string;
  headingClassName?: string;
};

export function SectionContainer({
  title,
  children,
  className,
  innerClassName,
  headingClassName,
}: SectionContainerProps) {
  return (
    <section className={clsx(s.section, className)}>
      <Container>
        <div className={clsx(s.inner, innerClassName)}>
          <h1 className={clsx(s.heading, headingClassName)}>{title}</h1>
          {children}
        </div>
      </Container>
    </section>
  );
}
