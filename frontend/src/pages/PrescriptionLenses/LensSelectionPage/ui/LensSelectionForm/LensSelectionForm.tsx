import { useMemo, useState } from 'react';

import { DropdownField } from '@/shared/ui';
import {
  coatingOptions,
  colorOptions,
  indexTags,
  lensDesignOptions,
  lensTypeOptions,
  manufacturerTags,
  propertyOptions,
} from '../../model/lensSelectionContent';
import { OptionTags } from '../OptionTags';
import s from './LensSelectionForm.module.scss';
import { useTranslation } from 'react-i18next';

export function LensSelectionForm() {
  const { t } = useTranslation();
  const [type, setType] = useState('');
  const [design, setDesign] = useState('');
  const [coating, setCoating] = useState('');
  const [properties, setProperties] = useState('');
  const [color, setColor] = useState('');
  const [product, setProduct] = useState('');
  const localizedLensTypeOptions = useMemo(
    () =>
      lensTypeOptions.map((option) => ({
        ...option,
        label: t(`prescription.option.${option.value}`, option.label),
      })),
    [t],
  );
  const localizedLensDesignOptions = useMemo(
    () =>
      lensDesignOptions.map((option) => ({
        ...option,
        label: t(`prescription.option.${option.value}`, option.label),
      })),
    [t],
  );
  const localizedCoatingOptions = useMemo(
    () =>
      coatingOptions.map((option) => ({
        ...option,
        label: t(`prescription.option.${option.value}`, option.label),
      })),
    [t],
  );
  const localizedPropertyOptions = useMemo(
    () =>
      propertyOptions.map((option) => ({
        ...option,
        label: t(`prescription.option.${option.value}`, option.label),
      })),
    [t],
  );
  const localizedColorOptions = useMemo(
    () =>
      colorOptions.map((option) => ({
        ...option,
        label: t(`prescription.option.${option.value}`, option.label),
      })),
    [t],
  );

  const reset = () => {
    setType('');
    setDesign('');
    setCoating('');
    setProperties('');
    setColor('');
    setProduct('');
  };

  return (
    <section className={s.formCard}>
      <div className={s.actionsTop}>
        <button type="button" onClick={reset}>
          {t('prescription.clear')}
        </button>
      </div>

      <div className={s.tagsPanel}>
        <OptionTags label={t('prescription.manufacturer')} tags={manufacturerTags} />
        <OptionTags label={t('prescription.index')} tags={indexTags} />
      </div>

      <div className={s.fieldsGrid}>
        <DropdownField
          label={t('prescription.type')}
          options={localizedLensTypeOptions}
          placeholder={t('prescription.selectType')}
          value={type}
          onChange={setType}
        />
        <DropdownField
          label={t('prescription.design')}
          options={localizedLensDesignOptions}
          placeholder={t('prescription.selectDesign')}
          value={design}
          onChange={setDesign}
        />
        <DropdownField
          label={t('prescription.coating')}
          options={localizedCoatingOptions}
          placeholder={t('prescription.selectCoating')}
          value={coating}
          onChange={setCoating}
        />
        <DropdownField
          label={t('prescription.properties')}
          options={localizedPropertyOptions}
          placeholder={t('prescription.selectProperties')}
          value={properties}
          onChange={setProperties}
        />
        <DropdownField
          label={t('prescription.propertyColor')}
          options={localizedColorOptions}
          placeholder={t('prescription.selectColor')}
          value={color}
          onChange={setColor}
        />
      </div>

      <div className={s.resultArea}>
        <label>
          <span>{t('prescription.lensSelection')}</span>
          <textarea
            readOnly
            value={t('prescription.lensSelectionHint')}
          />
        </label>

        <label>
          <span>{t('prescription.product')}</span>
          <input
            type="text"
            value={product}
            placeholder={t('prescription.productPlaceholder')}
            onChange={(event) => setProduct(event.target.value)}
          />
        </label>
      </div>

      <div className={s.actionsBottom}>
        <button className={s.cancelButton} type="button" onClick={reset}>
          {t('prescription.cancel')}
        </button>
        <button className={s.submitButton} type="button">
          {t('prescription.order')}
        </button>
      </div>
    </section>
  );
}
