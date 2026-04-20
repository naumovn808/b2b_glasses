import { Navigate, useParams } from 'react-router';
import {
  educationFaqItems,
  educationSections,
  getEducationItemBySlug,
} from '@/pages/Education/EducationPage/model/educationContent';
import { useRef, useState } from 'react';

import { Container } from '@/shared/ui';
import { FaqItem } from './FaqItem';
import heroBackground from '@/shared/assets/hero-background.png';
import s from './EducationArticlePage.module.scss';
import { useTranslation } from 'react-i18next';

export function EducationArticlePage() {
  const { t } = useTranslation();
  const { educationSlug } = useParams();
  const videoRef = useRef<HTMLVideoElement>(null);
  const educationItem = educationSlug
    ? getEducationItemBySlug(educationSlug)
    : undefined;
  const [openFaqId, setOpenFaqId] = useState<number>(
    educationFaqItems[0]?.id ?? 0,
  );
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);

  const handleVideoToggle = () => {
    const video = videoRef.current;

    if (!video) {
      return;
    }

    if (video.paused) {
      void video.play().catch(() => undefined);
      return;
    }

    video.pause();
  };

  if (!educationItem) {
    return <Navigate replace to="/education" />;
  }

  return (
    <section className={s.section}>
      <Container>
        <div className={s.hero}>
          <div className={s.heroLabelWrap}>
            <h1 className={s.heroLabel}>{t('pages.education')}</h1>
          </div>

          <div className={s.heroContent}>
            <h2 className={s.headline}>{t('education.articleLead')}</h2>

            <div className={s.articleSections}>
              {educationSections.map((section, index) => (
                <section key={section.title} className={s.articleSection}>
                  <h3 className={s.sectionTitle}>
                    {t(
                      index === 0 ? 'about.historyTitle' : 'about.missionTitle',
                      section.title,
                    )}
                  </h3>
                  <p className={s.sectionText}>
                    {t(
                      index === 0 ? 'about.historyText' : 'about.missionText',
                      section.text,
                    )}
                  </p>
                </section>
              ))}
            </div>
          </div>
        </div>

        <div className={s.videoWrap}>
          <video
            ref={videoRef}
            className={s.videoPoster}
            poster={heroBackground}
            preload="metadata"
            playsInline
            controls={isVideoPlaying}
            onPlay={() => setIsVideoPlaying(true)}
            onPause={() => setIsVideoPlaying(false)}
            onEnded={() => setIsVideoPlaying(false)}
          />

          {!isVideoPlaying ? <span className={s.videoShade} /> : null}

          {!isVideoPlaying ? (
            <button
              className={s.playButton}
              type="button"
              aria-label={t('education.playVideo')}
              onClick={handleVideoToggle}
            >
              <span className={s.playTriangle} aria-hidden="true" />
            </button>
          ) : null}
        </div>

        <div className={s.faqSection}>
          <h2 className={s.faqHeading}>{t('education.faq')}</h2>

          <div className={s.faqList}>
            {educationFaqItems.map((item) => (
              <FaqItem
                key={item.id}
                answer={item.answer}
                isOpen={openFaqId === item.id}
                onToggle={() =>
                  setOpenFaqId((currentId) =>
                    currentId === item.id ? 0 : item.id,
                  )
                }
                question={t('education.faqQuestion', item.question)}
              />
            ))}
          </div>
        </div>
      </Container>
    </section>
  );
}
