import clsx from 'clsx';
import s from './RichText.module.scss';

type RichTextProps = {
  className?: string;
  html: string;
};

export function RichText({ className, html }: RichTextProps) {
  return (
    <div
      className={clsx(s.root, className)}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
