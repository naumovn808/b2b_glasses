import { useMemo, useState } from 'react';

import { Container, DropdownField } from '@/shared/ui';
import {
  deliveryOptions,
  salonOptions,
} from '../model/prescriptionOrderContent';
import { LensOrderCard } from './LensOrderCard';
import s from './PrescriptionOrderPage.module.scss';
import { useTranslation } from 'react-i18next';

export function PrescriptionOrderPage() {
  const { t } = useTranslation();
  const [salon, setSalon] = useState('');
  const [delivery, setDelivery] = useState('');
  const localizedSalonOptions = useMemo(
    () =>
      salonOptions.map((option) => ({
        ...option,
        label: t(`prescription.option.${option.value}`, option.label),
      })),
    [t],
  );
  const localizedDeliveryOptions = useMemo(
    () =>
      deliveryOptions.map((option) => ({
        ...option,
        label: t(`prescription.option.${option.value}`, option.label),
      })),
    [t],
  );

  return (
    <section className={s.page}>
      <Container>
        <div className={s.inner}>
          <h1>{t('prescription.orderTitle')}</h1>

          <div className={s.topFields}>
            <DropdownField
              className={s.topField}
              iconVariant="chevron"
              options={localizedSalonOptions}
              placeholder={t('prescription.salonPlaceholder')}
              value={salon}
              onChange={setSalon}
            />

            <DropdownField
              className={s.topField}
              iconVariant="chevron"
              options={localizedDeliveryOptions}
              placeholder={t('prescription.deliveryPlaceholder')}
              value={delivery}
              onChange={setDelivery}
            />
          </div>

          <LensOrderCard />
        </div>
      </Container>
    </section>
  );
}
