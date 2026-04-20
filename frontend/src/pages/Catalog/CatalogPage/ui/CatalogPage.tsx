import { AccordionItem, Container, Pagination } from '@/shared/ui';
import { CatalogFilters, type ActiveCatalogFilters } from './CatalogFilters';
import { CategoryTabs } from './CategoryTabs';
import { ProductCard } from '@/features/product-card';
import {
  catalogCategories,
  catalogFiltersByCategory,
  catalogProducts,
  catalogSortOptions,
} from '../model/catalogContent';
import clsx from 'clsx';
import s from './CatalogPage.module.scss';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

const PRODUCTS_PER_PAGE = 6;

function hasActiveFilters(activeFilters: ActiveCatalogFilters) {
  return Object.values(activeFilters).some((filters) => filters.length > 0);
}

function getPriceValue(price: string) {
  const normalizedPrice = price.replace(',', '.').replace(/[^\d.]/g, '');

  return Number(normalizedPrice) || 0;
}

function getDiscountValue(price: string, oldPrice?: string) {
  if (!oldPrice) return 0;

  const currentPrice = getPriceValue(price);
  const previousPrice = getPriceValue(oldPrice);

  if (previousPrice <= 0) return 0;

  return Math.round(((previousPrice - currentPrice) / previousPrice) * 100);
}

export function CatalogPage() {
  const { t } = useTranslation();
  const [activeCategoryId, setActiveCategoryId] = useState(
    catalogCategories[0]?.id ?? '',
  );
  const [activeFilters, setActiveFilters] = useState<ActiveCatalogFilters>({});
  const [currentPage, setCurrentPage] = useState(1);
  const [isSortOpen, setIsSortOpen] = useState(false);
  const [isMobileFiltersOpen, setIsMobileFiltersOpen] = useState(false);
  const [isMobileSortOpen, setIsMobileSortOpen] = useState(false);
  const [activeSortId, setActiveSortId] = useState(
    catalogSortOptions[0]?.id ?? '',
  );
  const activeFilterGroups =
    catalogFiltersByCategory[activeCategoryId] ??
    catalogFiltersByCategory.frames;
  const categoryProducts = useMemo(
    () =>
      catalogProducts.filter(
        (product) => product.categoryId === activeCategoryId,
      ),
    [activeCategoryId],
  );
  const filteredProducts = useMemo(() => {
    const products = categoryProducts.filter((product) =>
      Object.entries(activeFilters).every(([groupId, selectedOptionIds]) => {
        if (selectedOptionIds.length === 0) return true;

        const productOptionIds = product.filterTags?.[groupId] ?? [];

        return selectedOptionIds.some((optionId) =>
          productOptionIds.includes(optionId),
        );
      }),
    );

    return [...products].sort((firstProduct, secondProduct) => {
      if (activeSortId === 'cheap-first') {
        return (
          getPriceValue(firstProduct.price) - getPriceValue(secondProduct.price)
        );
      }

      if (activeSortId === 'expensive-first') {
        return (
          getPriceValue(secondProduct.price) - getPriceValue(firstProduct.price)
        );
      }

      if (activeSortId === 'discount-first') {
        return (
          getDiscountValue(secondProduct.price, secondProduct.oldPrice) -
          getDiscountValue(firstProduct.price, firstProduct.oldPrice)
        );
      }

      return 0;
    });
  }, [activeFilters, activeSortId, categoryProducts]);
  const totalPages = Math.max(
    1,
    Math.ceil(filteredProducts.length / PRODUCTS_PER_PAGE),
  );
  const visibleProducts = filteredProducts.slice(
    (currentPage - 1) * PRODUCTS_PER_PAGE,
    currentPage * PRODUCTS_PER_PAGE,
  );
  const suggestedProducts =
    categoryProducts.length >= 3
      ? categoryProducts.slice(0, 3)
      : catalogProducts.slice(0, 3);
  const isEmptySearch =
    hasActiveFilters(activeFilters) && filteredProducts.length === 0;
  const filterActionButton =
    activeCategoryId === 'lenses'
      ? {
          label: t('catalog.orderPrescriptionLenses'),
          to: '/prescription-lenses',
        }
      : undefined;

  const handleCategoryChange = (categoryId: string) => {
    setActiveCategoryId(categoryId);
    setActiveFilters({});
    setCurrentPage(1);
    setIsMobileFiltersOpen(false);
    setIsMobileSortOpen(false);
  };

  const handleFilterToggle = (groupId: string, optionId: string) => {
    setCurrentPage(1);
    setActiveFilters((currentFilters) => {
      const currentGroupFilters = currentFilters[groupId] ?? [];
      const nextGroupFilters = currentGroupFilters.includes(optionId)
        ? currentGroupFilters.filter((id) => id !== optionId)
        : [...currentGroupFilters, optionId];

      if (nextGroupFilters.length === 0) {
        const nextFilters = { ...currentFilters };
        delete nextFilters[groupId];
        return nextFilters;
      }

      return {
        ...currentFilters,
        [groupId]: nextGroupFilters,
      };
    });
  };

  return (
    <section className={s.page}>
      <Container>
        <h1 className={s.title}>{t('catalog.title')}</h1>

        <CategoryTabs
          activeCategoryId={activeCategoryId}
          categories={catalogCategories}
          onCategoryChange={handleCategoryChange}
        />

        <div className={s.catalogShell}>
          <div className={s.desktopFilters}>
            <CatalogFilters
              activeFilters={activeFilters}
              actionButton={filterActionButton}
              groups={activeFilterGroups}
              onFilterToggle={handleFilterToggle}
            />
          </div>

          <div className={s.productsArea}>
            <div className={s.catalogToolbar}>
              <AccordionItem
                buttonClassName={s.sortButton}
                className={clsx(s.sortAccordion, s.desktopSort)}
                contentClassName={s.sortContent}
                iconClassName={s.sortIcon}
                iconOpenClassName={s.sortIconOpen}
                isOpen={isSortOpen}
                title={t('catalog.sortByPrice')}
                onToggle={() => setIsSortOpen((current) => !current)}
              >
                <div className={s.sortOptions}>
                  {catalogSortOptions.map((option) => (
                    <button
                      className={clsx(
                        s.sortOption,
                        activeSortId === option.id && s.sortOptionActive,
                      )}
                      key={option.id}
                      type="button"
                      aria-pressed={activeSortId === option.id}
                      onClick={() => {
                        setActiveSortId(option.id);
                        setCurrentPage(1);
                      }}
                    >
                      {t(`catalog.sort.${option.id}`, option.label)}
                    </button>
                  ))}
                </div>
              </AccordionItem>
            </div>

            <div className={s.mobileCatalogControls}>
              <AccordionItem
                bodyClassName={s.mobileControlPanelBody}
                buttonClassName={s.mobileControlButton}
                className={s.mobileControlAccordion}
                contentClassName={s.mobileControlPanel}
                iconClassName={s.mobileControlIcon}
                iconOpenClassName={s.mobileControlIconOpen}
                isOpen={isMobileFiltersOpen}
                title={t('catalog.filters')}
                onToggle={() => {
                  setIsMobileFiltersOpen((current) => !current);
                  setIsMobileSortOpen(false);
                }}
              >
                <CatalogFilters
                  activeFilters={activeFilters}
                  actionButton={filterActionButton}
                  compact
                  groups={activeFilterGroups}
                  showTitle={false}
                  onFilterToggle={handleFilterToggle}
                />
              </AccordionItem>

              <AccordionItem
                bodyClassName={s.mobileControlPanelBody}
                buttonClassName={s.mobileControlButton}
                className={s.mobileControlAccordion}
                contentClassName={s.mobileControlPanel}
                iconClassName={s.mobileControlIcon}
                iconOpenClassName={s.mobileControlIconOpen}
                isOpen={isMobileSortOpen}
                title={t('catalog.sortByPrice')}
                onToggle={() => {
                  setIsMobileSortOpen((current) => !current);
                  setIsMobileFiltersOpen(false);
                }}
              >
                <div className={s.sortOptions}>
                  {catalogSortOptions.map((option) => (
                    <button
                      className={clsx(
                        s.sortOption,
                        activeSortId === option.id && s.sortOptionActive,
                      )}
                      key={option.id}
                      type="button"
                      aria-pressed={activeSortId === option.id}
                      onClick={() => {
                        setActiveSortId(option.id);
                        setCurrentPage(1);
                        setIsMobileSortOpen(false);
                      }}
                    >
                      {t(`catalog.sort.${option.id}`, option.label)}
                    </button>
                  ))}
                </div>
              </AccordionItem>
            </div>

            {isEmptySearch ? (
              <div className={s.emptyState}>
                <h2>{t('catalog.emptyTitle')}</h2>
                <div className={s.emptyDivider} />
                <p>{t('catalog.emptySuggestion')}</p>
                <div className={s.productGrid}>
                  {suggestedProducts.map((product) => (
                    <ProductCard key={product.id} product={product} />
                  ))}
                </div>
              </div>
            ) : (
              <div className={s.productGrid}>
                {visibleProducts.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
            )}

            {!isEmptySearch && filteredProducts.length > PRODUCTS_PER_PAGE ? (
              <Pagination
                className={s.pagination}
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={setCurrentPage}
              />
            ) : null}
          </div>
        </div>
      </Container>
    </section>
  );
}
