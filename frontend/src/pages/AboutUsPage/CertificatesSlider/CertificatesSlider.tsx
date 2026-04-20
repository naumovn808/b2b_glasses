import 'swiper/css';
import 'swiper/css/pagination';

import { Navigation, Pagination } from 'swiper/modules';
import { Swiper, SwiperSlide } from 'swiper/react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { CertificateCard } from './CertificateCard';
import { CertificateImageModal } from './CertificateImageModal';
import s from './CertificatesSlider.module.scss';

export type CertificateSlide = {
  id: string;
  image: string;
  title: string;
};

type CertificatesSliderProps = {
  certificates: CertificateSlide[];
};

export function CertificatesSlider({ certificates }: CertificatesSliderProps) {
  const { t } = useTranslation();
  const [viewedCertificate, setViewedCertificate] =
    useState<CertificateSlide | null>(null);

  return (
    <>
      <div className={s.slider}>
        <Swiper
          className={s.certificateSlider}
          modules={[Navigation, Pagination]}
          navigation={{
            nextEl: `.${s.nextButton}`,
          }}
          pagination={{
            clickable: true,
            el: `.${s.pagination}`,
          }}
          slidesPerView={1}
          spaceBetween={16}
          speed={420}
          loop
          breakpoints={{
            900: {
              slidesPerView: 3,
              spaceBetween: 24,
            },
            1200: {
              slidesPerView: 3,
              spaceBetween: 48,
            },
          }}
        >
          {certificates.map((certificate) => (
            <SwiperSlide key={certificate.id}>
              <CertificateCard
                certificate={certificate}
                onView={setViewedCertificate}
              />
            </SwiperSlide>
          ))}
        </Swiper>

        <button
          className={`${s.navButton} ${s.nextButton}`}
          type="button"
          aria-label={t('certificates.next')}
        >
          <span className={s.arrowRight} aria-hidden="true" />
        </button>

        <div className={s.pagination} />
      </div>

      <CertificateImageModal
        certificate={viewedCertificate}
        onClose={() => setViewedCertificate(null)}
      />
    </>
  );
}
