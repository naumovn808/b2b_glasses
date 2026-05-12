import {
  AccordionItem,
  Container,
  EmptyState,
  Pagination,
  Spinner,
} from '@/shared/ui';
import {
  PRODUCTS_PER_PAGE,
  clearCatalogFilterParams,
  createFramesParams,
  createLensesParams,
  getCatalogCategory,
  getCatalogFilterGroups,
  getCatalogFilters,
  getCatalogPage,
  getCatalogSort,
  hasCatalogFilters,
  mapFrameToProduct,
  mapLensToProduct,
  sortCatalogProducts,
  updateCatalogSearchParams,
} from '../model/catalogApiMappers';
import { catalogCategories, catalogSortOptions } from '../model/catalogContent';
import {
  useGetFrameFiltersQuery,
  useGetFramesQuery,
  useGetLensOptionsQuery,
  useGetLensesQuery,
} from '@/entities/catalog';
import { useMemo, useState } from 'react';

import { CatalogFilters } from './CatalogFilters';
import { CategoryTabs } from './CategoryTabs';
import { ProductCard, type ProductCardProduct } from '@/features/product-card';
import clsx from 'clsx';
import s from './CatalogPage.module.scss';
import { useAddCartItemMutation } from '@/entities/cart';
import { useDebouncedValue } from '@/shared/lib';
import { useSearchParams } from 'react-router';
import { useTranslation } from 'react-i18next';

export function CatalogPage() {
  const { t } = useTranslation();
  const [searchParams, setSearchParams] = useSearchParams();
  const [isSortOpen, setIsSortOpen] = useState(false);
  const [isMobileFiltersOpen, setIsMobileFiltersOpen] = useState(false);
  const [isMobileSortOpen, setIsMobileSortOpen] = useState(false);
  const [addCartItem] = useAddCartItemMutation();

  const activeCategoryId = getCatalogCategory(searchParams);
  const activeFilters = useMemo(
    () => getCatalogFilters(searchParams),
    [searchParams],
  );
  const currentPage = getCatalogPage(searchParams);
  const activeSortId = getCatalogSort(
    searchParams,
    catalogSortOptions[0]?.id ?? '',
  );

  const framesParams = useMemo(
    () => createFramesParams(activeFilters, currentPage),
    [activeFilters, currentPage],
  );
  const lensesParams = useMemo(
    () => createLensesParams(activeFilters, currentPage),
    [activeFilters, currentPage],
  );
  const [debouncedFramesParams, isFramesParamsDebouncing] = useDebouncedValue(
    framesParams,
    350,
  );
  const [debouncedLensesParams, isLensesParamsDebouncing] = useDebouncedValue(
    lensesParams,
    350,
  );

  const { data: frameFiltersData, isFetching: isFrameFiltersFetching } =
    useGetFrameFiltersQuery(undefined, {
      skip: activeCategoryId !== 'frames',
    });
  const { data: lensOptionsData, isFetching: isLensOptionsFetching } =
    useGetLensOptionsQuery(undefined, {
      skip: activeCategoryId !== 'lenses',
    });
  const { data: framesData, isFetching: isFramesFetching } = useGetFramesQuery(
    debouncedFramesParams,
    { skip: activeCategoryId !== 'frames' },
  );
  const { data: lensesData, isFetching: isLensesFetching } = useGetLensesQuery(
    debouncedLensesParams,
    { skip: activeCategoryId !== 'lenses' },
  );

  const filterGroups = useMemo(
    () =>
      getCatalogFilterGroups(
        activeCategoryId,
        activeCategoryId === 'frames' ? frameFiltersData : lensOptionsData,
      ),
    [activeCategoryId, frameFiltersData, lensOptionsData],
  );
  const products = useMemo(() => {
    const categoryProducts =
      activeCategoryId === 'frames'
        ? framesData?.results.map(mapFrameToProduct)
        : lensesData?.results.map(mapLensToProduct);

    return sortCatalogProducts(categoryProducts ?? [], activeSortId);
  }, [
    activeCategoryId,
    activeSortId,
    framesData?.results,
    lensesData?.results,
  ]);

  const productsCount =
    activeCategoryId === 'frames' ? framesData?.count : lensesData?.count;
  const totalPages = Math.max(
    1,
    Math.ceil((productsCount ?? 0) / PRODUCTS_PER_PAGE),
  );
  const isProductsLoading =
    (activeCategoryId === 'frames' &&
      (isFramesFetching || isFramesParamsDebouncing)) ||
    (activeCategoryId === 'lenses' &&
      (isLensesFetching || isLensesParamsDebouncing));
  const isFiltersLoading =
    (activeCategoryId === 'frames' && isFrameFiltersFetching) ||
    (activeCategoryId === 'lenses' && isLensOptionsFetching);
  const isEmptySearch =
    hasCatalogFilters(activeFilters) && products.length === 0;
  const filterActionButton =
    activeCategoryId === 'lenses'
      ? {
          label: t('catalog.orderPrescriptionLenses'),
          to: '/prescription-lenses',
        }
      : undefined;

  const handleCategoryChange = (categoryId: string) => {
    setSearchParams(
      updateCatalogSearchParams(searchParams, (params) => {
        params.set('category', categoryId);
        params.delete('page');
        clearCatalogFilterParams(params);
      }),
    );
    setIsMobileFiltersOpen(false);
    setIsMobileSortOpen(false);
  };

  const handleFilterToggle = (groupId: string, optionId: string) => {
    setSearchParams(
      updateCatalogSearchParams(searchParams, (params) => {
        const currentValues =
          params.get(groupId)?.split(',').filter(Boolean) ?? [];
        const nextValues = currentValues.includes(optionId)
          ? currentValues.filter((id) => id !== optionId)
          : [...currentValues, optionId];

        if (nextValues.length > 0) {
          params.set(groupId, nextValues.join(','));
        } else {
          params.delete(groupId);
        }

        params.delete('page');
      }),
    );
  };

  const handleSortChange = (sortId: string) => {
    setSearchParams(
      updateCatalogSearchParams(searchParams, (params) => {
        params.set('sort', sortId);
        params.delete('page');
      }),
    );
  };

  const handlePageChange = (page: number) => {
    setSearchParams(
      updateCatalogSearchParams(searchParams, (params) => {
        if (page > 1) {
          params.set('page', String(page));
          return;
        }

        params.delete('page');
      }),
    );
  };

  const handleAddToCart = async (
    product: ProductCardProduct,
    quantity: number,
  ) => {
    if (!product.apiProductId || !product.apiProductType) {
      return;
    }

    await addCartItem({
      product_id: product.apiProductId,
      product_type: product.apiProductType,
      quantity,
    }).unwrap();
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
            {isFiltersLoading ? (
              <div className={s.filtersLoader}>
                <Spinner size="md" />
              </div>
            ) : (
              <CatalogFilters
                activeFilters={activeFilters}
                actionButton={filterActionButton}
                groups={filterGroups}
                onFilterToggle={handleFilterToggle}
              />
            )}
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
                      onClick={() => handleSortChange(option.id)}
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
                {isFiltersLoading ? (
                  <div className={s.filtersLoader}>
                    <Spinner size="md" />
                  </div>
                ) : (
                  <CatalogFilters
                    activeFilters={activeFilters}
                    actionButton={filterActionButton}
                    compact
                    groups={filterGroups}
                    showTitle={false}
                    onFilterToggle={handleFilterToggle}
                  />
                )}
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
                        handleSortChange(option.id);
                        setIsMobileSortOpen(false);
                      }}
                    >
                      {t(`catalog.sort.${option.id}`, option.label)}
                    </button>
                  ))}
                </div>
              </AccordionItem>
            </div>

            {isProductsLoading ? (
              <div className={s.loader}>
                <Spinner size="lg" />
              </div>
            ) : isEmptySearch ? (
              <div className={s.emptyState}>
                <h2>{t('catalog.emptyTitle')}</h2>
                <div className={s.emptyDivider} />
                <p>{t('catalog.emptySuggestion')}</p>
              </div>
            ) : products.length === 0 ? (
              <EmptyState title={t('catalog.emptyProducts')} />
            ) : (
              <div className={s.productGrid}>
                {products.map((product) => (
                  <ProductCard
                    key={product.id}
                    product={product}
                    onAddToCart={handleAddToCart}
                  />
                ))}
              </div>
            )}

            {!isProductsLoading && !isEmptySearch && totalPages > 1 ? (
              <Pagination
                className={s.pagination}
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={handlePageChange}
              />
            ) : null}
          </div>
        </div>
      </Container>
    </section>
  );
}
