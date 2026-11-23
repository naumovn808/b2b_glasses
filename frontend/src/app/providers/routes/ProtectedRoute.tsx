import { type ReactNode } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { selectUserIsAuth, selectUserInited, userActions } from '@/entities/user';
import { Container, Spinner } from '@/shared/ui';
import { useTranslation } from 'react-i18next';

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const isAuth = useSelector(selectUserIsAuth);
  const inited = useSelector(selectUserInited);

  if (!inited) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '5rem 0' }}>
        <Spinner size="lg" />
      </div>
    );
  }

  if (!isAuth) {
    return (
      <section style={{ padding: '7.5rem 0 4rem', minHeight: '60vh', display: 'flex', alignItems: 'center' }}>
        <Container>
          <div style={{ textAlign: 'center', padding: '3rem 1.5rem', background: '#ffffff', borderRadius: '14px', maxWidth: '520px', margin: '0 auto', boxShadow: '0 4px 20px rgba(0,0,0,0.05)' }}>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', fontWeight: 700 }}>{t('auth.title')}</h2>
            <p style={{ color: '#55585d', marginBottom: '1.8rem', lineHeight: 1.5 }}>
              Доступ к данному разделу открыт только для авторизованных B2B партнеров.
            </p>
            <button
              type="button"
              onClick={() => dispatch(userActions.openAuthModal())}
              style={{ padding: '0.85rem 1.8rem', background: '#ffc516', color: '#111111', fontWeight: 600, border: 'none', borderRadius: '8px', cursor: 'pointer' }}
            >
              {t('auth.submit')}
            </button>
          </div>
        </Container>
      </section>
    );
  }

  return <>{children}</>;
}
