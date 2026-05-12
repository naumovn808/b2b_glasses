import { useParams } from 'react-router';
import { useRef, useState } from 'react';

import { Container, EmptyState, RichText, Spinner } from '@/shared/ui';
import { FaqItem } from './FaqItem';
import { getLocalizedField } from '@/shared/lib';
import { useGetFaqQuery } from '@/entities/faq';
import { useGetTrainingByIdQuery } from '@/entities/training';
import s from './EducationArticlePage.module.scss';
import { useTranslation } from 'react-i18next';

export function EducationArticlePage() {
  const { i18n, t } = useTranslation();
  const { educationSlug } = useParams();
  const videoRef = useRef<HTMLVideoElement>(null);
  const {
    data: trainingItem,
    isError: isTrainingError,
    isLoading: isTrainingLoading,
  } = useGetTrainingByIdQuery(educationSlug ?? '', {
    skip: !educationSlug,
  });
  const trainingTitle = trainingItem
    ? getLocalizedField(trainingItem, 'title', i18n.language)
    : '';
  const trainingDescription = trainingItem
    ? getLocalizedField(trainingItem, 'description', i18n.language)
    : '';
  const { data: faqData, isLoading: isFaqLoading } = useGetFaqQuery();
  const faqItems = faqData?.results ?? [];
  const [openFaqId, setOpenFaqId] = useState<number | null>(null);
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

  if (isTrainingLoading) {
    return (
      <section className={s.section}>
        <Container>
          <div className={s.faqLoader}>
            <Spinner size="lg" />
          </div>
        </Container>
      </section>
    );
  }

  if (isTrainingError || !trainingItem) {
    return (
      <section className={s.section}>
        <Container>
          <EmptyState title={t('common.notFound')} />
        </Container>
      </section>
    );
  }

  return (
    <section className={s.section}>
      <Container>
        <div className={s.hero}>
          <div className={s.heroLabelWrap}>
            <h1 className={s.heroLabel}>{t('pages.education')}</h1>
          </div>

          <div className={s.heroContent}>
            <h2 className={s.headline}>
              {trainingTitle || t('education.articleLead')}
            </h2>

            <div className={s.articleSections}>
              <section className={s.articleSection}>
                <h3 className={s.sectionTitle}>{trainingTitle}</h3>
                <RichText
                  className={s.sectionText}
                  html={trainingDescription}
                />
              </section>
            </div>
          </div>
        </div>

        {trainingItem.video ? (
          <div className={s.videoWrap}>
            <video
              ref={videoRef}
              className={s.videoPoster}
              poster={trainingItem.image}
              preload="metadata"
              playsInline
              src={trainingItem.video}
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
        ) : null}

        <div className={s.faqSection}>
          <h2 className={s.faqHeading}>{t('education.faq')}</h2>

          <div className={s.faqList}>
            {isFaqLoading ? (
              <div className={s.faqLoader}>
                <Spinner size="md" />
              </div>
            ) : null}

            {!isFaqLoading
              ? faqItems.map((item, index) => {
                  const isOpen =
                    openFaqId === item.id ||
                    (openFaqId === undefined && index === 0);

                  return (
                    <FaqItem
                      key={item.id}
                      answer={getLocalizedField(item, 'answer', i18n.language)}
                      isOpen={isOpen}
                      onToggle={() =>
                        setOpenFaqId(() => (isOpen ? null : item.id))
                      }
                      question={getLocalizedField(
                        item,
                        'question',
                        i18n.language,
                      )}
                    />
                  );
                })
              : null}
          </div>
        </div>
      </Container>
    </section>
  );
}
