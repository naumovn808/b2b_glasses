import s from './FeedbackForm.module.scss';
import { useTranslation } from 'react-i18next';

export function FeedbackForm() {
  const { t } = useTranslation();

  return (
    <form
      className={s.form}
      onSubmit={(event) => {
        event.preventDefault();
      }}
    >
      <h2 className={s.title}>{t('form.feedback')}</h2>

      <label className={s.field}>
        <span>{t('form.name')}</span>
        <input
          name="name"
          type="text"
          placeholder={t('form.name')}
          autoComplete="name"
        />
      </label>

      <label className={s.field}>
        <span>E-mail</span>
        <input
          name="email"
          type="email"
          placeholder="E-mail"
          autoComplete="email"
        />
      </label>

      <label className={s.field}>
        <span>{t('form.message')}</span>
        <textarea name="message" placeholder={t('form.message')} rows={7} />
      </label>

      <button className={s.submitButton} type="submit">
        {t('form.submit')}
      </button>

      <p className={s.agreement}>{t('form.agreement')}</p>
    </form>
  );
}
