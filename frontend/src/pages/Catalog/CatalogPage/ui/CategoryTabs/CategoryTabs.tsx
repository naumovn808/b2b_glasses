import clsx from 'clsx';
import s from './CategoryTabs.module.scss';
import { useTranslation } from 'react-i18next';

type CategoryTab = {
  id: string;
  title: string;
  image: string;
  disabled?: boolean;
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
      {categories.map((category) => {
        const isActive = activeCategoryId === category.id;

        return (
          <button
            className={clsx(
              s.tab,
              isActive && s.tabActive,
              category.disabled && s.tabDisabled,
            )}
            key={category.id}
            type="button"
            aria-disabled={category.disabled}
            aria-pressed={isActive}
            disabled={category.disabled}
            onClick={() => onCategoryChange(category.id)}
          >
            <img src={category.image} alt="" aria-hidden="true" />
            <span>{t(`catalog.category.${category.id}`, category.title)}</span>
          </button>
        );
      })}
    </div>
  );
}
