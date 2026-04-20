import Arrow from '@/shared/assets/icons/arrow.svg?react';
import Tg from '@/shared/assets/icons/header/tg.svg';
import WhatsApp from '@/shared/assets/icons/header/whatsapp.svg';
import bg from '@/shared/assets/hero-background.png';
import { Link } from 'react-router';
import s from './Hero.module.scss';
import { useTranslation } from 'react-i18next';

export function Hero() {
  const { t } = useTranslation();

  return (
    <section className={s.heroSection} style={{ backgroundImage: `url(${bg})` }}>
      {/* <Container> */}
      <div className={s.heroContent}>
        <h1 className={s.heroTitle}>
          {t('hero.titleLine1')} <br /> {t('hero.titleLine2')}
        </h1>
        <Link className={s.heroCta} to="/catalog">
          {t('hero.cta')}
          <span className={s.heroCtaIcon} aria-hidden="true">
            <Arrow />
          </span>
        </Link>
      </div>
      <div className={s.heroSocials}>
        <a href="https://t.me/" aria-label="Telegram">
          <img src={Tg} alt="tg" />
        </a>
        <a href="https://wa.me/" aria-label="WhatsApp">
          <img src={WhatsApp} alt="WhatsApp" />
        </a>
      </div>
      {/* </Container> */}
    </section>
  );
}
