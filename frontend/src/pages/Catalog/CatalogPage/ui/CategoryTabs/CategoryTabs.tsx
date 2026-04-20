import clsx from 'clsx';
import s from './CategoryTabs.module.scss';
import { useTranslation } from 'react-i18next';

type CategoryTab = {
  id: string;
  title: string;
  image: string;
};

type CategoryTabsProps = {
  activeCategoryId: string;
  categories: CategoryTab[];
  onCategoryChange: (categoryId: string) => void;
};

export function CategoryTabs({
  activeCategoryId,
  categories,
  onCategoryChange,
}: CategoryTabsProps) {
  const { t } = useTranslation();

  return (
    <div className={s.tabs} aria-label={t('catalog.categoriesAria')}>
      {categories.map((category) => (
        <button
          className={clsx(s.tab, activeCategoryId === category.id && s.tabActive)}
          key={category.id}
          type="button"
          aria-pressed={activeCategoryId === category.id}
          onClick={() => onCategoryChange(category.id)}
        >
          <img src={category.image} alt="" aria-hidden="true" />
          <span>{t(`catalog.category.${category.id}`, category.title)}</span>
        </button>
      ))}
    </div>
  );
}
