import { LINKS } from '@/widgets/layoutWidgets/header/model/links';
import { ModalWindowShell } from '@/shared/ui';
import { NavLink } from 'react-router';
import Tg from '@/shared/assets/icons/header/tg.svg';
import WhatsApp from '@/shared/assets/icons/header/whatsapp.svg';
import s from './BurgerModal.module.scss';
import { useTranslation } from 'react-i18next';
import { useSelector, useDispatch } from 'react-redux';
import { selectUserIsAuth, userActions } from '@/entities/user';

export default function BurgerModal({
  isOpen,
  onClose,
}: {
  isOpen: boolean;
  onClose: () => void;
}) {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const isAuth = useSelector(selectUserIsAuth);

  const visibleLinks = LINKS.filter((item) => !item.authOnly || isAuth);

  const handleOpenAuth = () => {
    onClose();
    dispatch(userActions.openAuthModal());
  };

  return (
    <ModalWindowShell
      isOpen={isOpen}
      position="right"
      className={s.burgerMenuModal}
      title={t('nav.menu')}
      onClose={onClose}
    >
      <div className={s.burgerContent}>
        <ul className={s.burgerLinks}>
          {visibleLinks.map((item) => (
            <li key={item.href}>
              <NavLink
                className={s.burgerLink}
                to={item.href}
                onClick={onClose}
              >
                {t(item.labelKey)}
              </NavLink>
            </li>
          ))}
          {isAuth ? (
            <li>
              <NavLink
                className={s.burgerLink}
                to="/profile"
                onClick={onClose}
              >
                {t('profile.title')}
              </NavLink>
            </li>
          ) : (
            <li>
              <button
                type="button"
                className={s.burgerLink}
                onClick={handleOpenAuth}
                style={{ background: 'none', border: 'none', cursor: 'pointer', textAlign: 'left', width: '100%', color: '#ffc516' }}
              >
                {t('auth.submit')}
              </button>
            </li>
          )}
        </ul>

        <div className={s.burgerDivider} />

        <div className={s.burgerContacts}>
          <a className={s.burgerContact} href="tel:+998903977999">
            +998 903 977 999
          </a>
          <a className={s.burgerContact} href="mailto:info@torgroup.uz">
            info@torgroup.uz
          </a>
          <div className={s.burgerAddress}>{t('common.address')}</div>
        </div>

        <div className={s.burgerDivider} />

        <div className={s.burgerSocials}>
          <a href="https://t.me/" aria-label="Telegram">
            <img src={Tg} alt="Telegram" />
          </a>
          <a href="https://wa.me/" aria-label="WhatsApp">
            <img src={WhatsApp} alt="WhatsApp" />
          </a>
        </div>
      </div>
    </ModalWindowShell>
  );
}
