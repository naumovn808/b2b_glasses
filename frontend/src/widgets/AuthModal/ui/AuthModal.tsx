import { type FormEvent, useId, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ModalWindowShell } from '@/shared/ui';
import { useDispatch, useSelector } from 'react-redux';
import { loginByUsername, selectUserError, selectUserIsLoading } from '@/entities/user';
import type { AppDispatch } from '@/app/providers/store/store';
import s from './AuthModal.module.scss';

const useAppDispatch = () => useDispatch<AppDispatch>();

type AuthModalProps = {
  isOpen: boolean;
  onClose?: () => void;
};

export function AuthModal({ isOpen, onClose }: AuthModalProps) {
  const { t } = useTranslation();

  const loginId = useId();
  const passwordId = useId();

  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');

  const dispatch = useAppDispatch();
  const isLoading = useSelector(selectUserIsLoading);
  const error = useSelector(selectUserError);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const trimmedLogin = login.trim();
    const trimmedPassword = password.trim();

    if (!trimmedLogin || !trimmedPassword) {
      return;
    }

    const result = await dispatch(
      loginByUsername({ login: trimmedLogin, password: trimmedPassword }),
    );

    if (result.meta.requestStatus === 'fulfilled') {
      setLogin('');
      setPassword('');
      onClose?.();
    }
  };

  return (
    <ModalWindowShell
      isOpen={isOpen}
      modalClassName={s.authModalShell}
      position="center"
      title={<h2 className={s.title}>{t('auth.title')}</h2>}
      onClose={onClose}
    >
      <form className={s.form} onSubmit={handleSubmit}>
        {/* LOGIN */}
        <label className={s.field} htmlFor={loginId}>
          <span>{t('auth.loginLabel')}</span>
          <input
            id={loginId}
            name="login"
            type="text"
            autoComplete="username"
            placeholder={t('auth.loginPlaceholder')}
            value={login}
            onChange={(e) => setLogin(e.target.value)}
          />
        </label>

        {/* PASSWORD */}
        <label className={s.field} htmlFor={passwordId}>
          <span>{t('auth.passwordLabel')}</span>
          <input
            id={passwordId}
            name="password"
            type="password"
            autoComplete="current-password"
            placeholder={t('auth.passwordPlaceholder')}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>

        {error && <p className={s.error}>{error}</p>}

        {/* SUBMIT */}
        <button className={s.submitButton} type="submit" disabled={isLoading}>
          {isLoading ? t('auth.loading') : t('auth.submit')}
        </button>

        {/* FORGOT PASSWORD */}
        <a
          className={s.forgotPasswordLink}
          href="https://t.me/glasses_uz_test_bot?start=reset_password"
          target="_blank"
          rel="noopener noreferrer"
        >
          {t('auth.forgotPassword')}
        </a>

        {/* AGREEMENT */}
        <p className={s.agreement}>{t('auth.agreement')}</p>
      </form>
    </ModalWindowShell>
  );
}
