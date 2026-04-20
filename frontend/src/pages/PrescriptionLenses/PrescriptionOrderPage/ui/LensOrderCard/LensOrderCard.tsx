import { useEffect, useMemo, useState } from 'react';

import { DropdownField } from '@/shared/ui';
import { lensTypeOptions } from '../../model/prescriptionOrderContent';
import s from './LensOrderCard.module.scss';
import { useNavigate } from 'react-router';
import { useTranslation } from 'react-i18next';

export function LensOrderCard() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [rightLens, setRightLens] = useState('');
  const [leftLens, setLeftLens] = useState('');
  const localizedLensTypeOptions = useMemo(
    () =>
      lensTypeOptions.map((option) => ({
        ...option,
        label: t(`prescription.option.${option.value}`, option.label),
      })),
    [t],
  );
  useEffect(() => {
    if (rightLens && leftLens) {
      navigate('/prescription-lenses/select');
    }
  }, [rightLens, leftLens]);
  return (
    <section className={s.card}>
      <header className={s.header}>{t('prescription.lenses')}</header>

      <div className={s.body}>
        <DropdownField
          className={s.lensField}
          label={t('prescription.right')}
          options={localizedLensTypeOptions}
          placeholder={t('prescription.selectLens')}
          value={rightLens}
          onChange={setRightLens}
        />

        <button
          className={s.copyButton}
          type="button"
          aria-label={t('prescription.copyRightToLeft')}
          onClick={() => setLeftLens(rightLens)}
        >
          ⇆
        </button>

        <DropdownField
          className={s.lensField}
          label={t('prescription.left')}
          options={localizedLensTypeOptions}
          placeholder={t('prescription.selectLens')}
          value={leftLens}
          onChange={setLeftLens}
        />
      </div>
    </section>
  );
}
