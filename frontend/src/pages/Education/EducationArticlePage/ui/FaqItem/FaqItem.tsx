import { AnimatePresence, motion } from 'framer-motion';

import s from './FaqItem.module.scss';

type FaqItemProps = {
  answer: string;
  isOpen: boolean;
  onToggle: () => void;
  question: string;
};

export function FaqItem({ answer, isOpen, onToggle, question }: FaqItemProps) {
  return (
    <article className={`${s.item} ${isOpen ? s.itemOpen : ''}`}>
      <button
        className={s.trigger}
        type="button"
        onClick={onToggle}
        aria-expanded={isOpen}
      >
        <span className={s.question}>{question}</span>
        <motion.span
          className={s.icon}
          aria-hidden="true"
          animate={isOpen ? 'open' : 'closed'}
          initial={false}
          transition={{ duration: 0.22, ease: 'easeOut' }}
        >
          <span className={s.iconLine} />
          <motion.span
            className={s.iconLine}
            variants={{
              closed: { opacity: 1, rotate: 90, scaleY: 1 },
              open: { opacity: 0, rotate: 90, scaleY: 0.4 },
            }}
            transition={{ duration: 0.22, ease: 'easeOut' }}
          />
        </motion.span>
      </button>

      <AnimatePresence initial={false}>
        {isOpen ? (
          <motion.div
            key="answer"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.28, ease: 'easeOut' }}
            className={s.answerWrap}
          >
            <p className={s.answer}>{answer}</p>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </article>
  );
}
