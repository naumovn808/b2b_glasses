import { Container } from '@/shared/ui';
import LogoUrl from '@/shared/assets/logo-footer.svg';
import Tg from '@/shared/assets/icons/header/tg.svg';
import WhatsApp from '@/shared/assets/icons/header/whatsapp.svg';
import s from './Footer.module.scss';
import { useTranslation } from 'react-i18next';

export function Footer() {
  const { t } = useTranslation();

  return (
    <footer className={s.footer}>
      <Container className={s.footerContainer}>
        <div className={s.footerInner}>
          <div className={s.footerTop}>
            <div className={s.logoWrap}>
              <img src={LogoUrl} alt="Hikari Pure Vision" />
            </div>

            <nav className={s.links} aria-label="Footer">
              <a href="/news">{t('nav.news')}</a>
              <a href="/education">{t('nav.education')}</a>
              <a href="/about">{t('nav.about')}</a>
              <a href="/catalog">{t('nav.shop')}</a>
            </nav>

            <div className={s.socials} aria-label="Social links">
              <a href="https://t.me/" aria-label="Telegram">
                <img src={Tg} alt="tg" />
              </a>
              <a href="https://wa.me/" aria-label="WhatsApp">
                <img src={WhatsApp} alt="WhatsApp" />
              </a>
            </div>

            <div className={s.about}>
              <span className={s.aboutAddress}>{t('common.address')}</span>
              <a className={s.aboutPhone} href="tel:  +998903977999">
                + 998 903 977 999
              </a>
            </div>

            <div className={s.legal}>
              <a href="/terms">{t('footer.terms')}</a>
              <a href="/privacy">{t('footer.privacy')}</a>
            </div>
          </div>
          <div className={s.footerBottom}>
            <span>{t('footer.company')}</span>
            <span>{t('footer.taxId')}</span>
            <span>{t('footer.bank')}</span>
            <span>{t('footer.account')}</span>
            <span>{t('footer.mfo')}</span>
            <span>{t('footer.oked')}</span>
          </div>
        </div>
      </Container>
    </footer>
  );
}
