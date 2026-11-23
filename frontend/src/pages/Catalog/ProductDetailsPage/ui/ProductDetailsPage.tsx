import { Container, EmptyState, Spinner } from '@/shared/ui';
import { Navigate, useParams } from 'react-router';
import {
  mapFrameToProduct,
  mapLensToProduct,
} from '../../CatalogPage/model/catalogApiMappers';
import {
  type CatalogProductType,
  type Frame,
  type Lens,
  type LensOptions,
  useGetFramesQuery,
  useGetLensOptionsQuery,
  useGetLensesQuery,
  useGetProductByIdQuery,
} from '@/entities/catalog';

import { ProductGallery } from './ProductGallery';
import { ProductInfo, type ProductDetailsOptionGroup } from './ProductInfo';
import { RelatedProductCard } from './RelatedProductCard';
import s from './ProductDetailsPage.module.scss';
import { useTranslation } from 'react-i18next';

function parseCatalogProductId(productId?: string): {
  id: number;
  type: CatalogProductType;
} | null {
  const [type, rawId] = productId?.split('-') ?? [];
  const id = Number(rawId);

  if (
    (type !== 'frame' && type !== 'lens') ||
    !Number.isInteger(id) ||
    id <= 0
  ) {
    return null;
  }

  return { id, type };
}

function getDiscountPercent(price: string, oldPrice?: string) {
  if (!oldPrice) return 0;

  const currentPrice = Number(price.replace(',', '.').replace(/[^\d.]/g, ''));
  const previousPrice = Number(
    oldPrice.replace(',', '.').replace(/[^\d.]/g, ''),
  );

  if (!currentPrice || !previousPrice) return 0;

  return Math.round(((previousPrice - currentPrice) / previousPrice) * 100);
}

function getLensOptionItems(rawOptions: unknown, selectedValue: string) {
  const normalizeOption = (rawOption: unknown) => {
    if (
      rawOption &&
      typeof rawOption === 'object' &&
      !Array.isArray(rawOption)
    ) {
      const option = rawOption as Record<string, unknown>;
      const id =
        option.id ?? option.value ?? option.slug ?? option.key ?? option.name;
      const label = option.name ?? option.label ?? option.title ?? id;

      return id !== undefined && label !== undefined
        ? { id: String(id), label: String(label) }
        : null;
    }

    if (typeof rawOption === 'string' || typeof rawOption === 'number') {
      return { id: String(rawOption), label: String(rawOption) };
    }

    return null;
  };
  const normalizedOptions = Array.isArray(rawOptions)
    ? rawOptions
        .map(normalizeOption)
        .filter((option): option is { id: string; label: string } =>
          Boolean(option),
        )
    : [];
  const hasSelectedOption = normalizedOptions.some(
    (option) => option.id === selectedValue,
  );
  const options = hasSelectedOption
    ? normalizedOptions
    : [{ id: selectedValue, label: selectedValue }, ...normalizedOptions];

  return options.map((option) => ({
    ...option,
    isSelected: option.id === selectedValue,
  }));
}

function getLensOptionGroups(
  lens?: Lens,
  lensOptions?: LensOptions,
): ProductDetailsOptionGroup[] | undefined {
  if (!lens) return undefined;

  return [
    { id: 'series', title: 'Серия', value: lens.series },
    { id: 'sph', title: 'SPH', value: lens.sph },
    { id: 'cyl', title: 'CYL', value: lens.cyl },
    {
      id: 'dia',
      title: 'DIA',
      value: lens.dia !== null && lens.dia !== undefined ? String(lens.dia) : '',
    },
  ]
    .filter((group) => group.value)
    .map((group) => ({
      id: group.id,
      title: group.title,
      options: getLensOptionItems(lensOptions?.[group.id], group.value),
    }));
}

function getFrameSizes(frame?: Frame) {
  if (!frame) return [];

  return [frame.size_a, frame.size_b, frame.size_d, frame.size_temple].filter(
    (size): size is string => Boolean(size),
  );
}

export function ProductDetailsPage() {
  const { t } = useTranslation();
  const { productId } = useParams();
  const parsedProductId = parseCatalogProductId(productId);
  const isFrame = parsedProductId?.type === 'frame';
  const isLens = parsedProductId?.type === 'lens';
  const {
    data: productData,
    isError: isProductError,
    isFetching: isProductFetching,
    isLoading: isProductLoading,
  } = useGetProductByIdQuery(
    {
      id: parsedProductId?.id ?? '',
      type: parsedProductId?.type ?? 'frame',
    },
    { skip: !parsedProductId },
  );
  const { data: framesData } = useGetFramesQuery(
    { page_size: 4 },
    { skip: !isFrame },
  );
  const { data: lensesData } = useGetLensesQuery(
    { page_size: 4 },
    { skip: !isLens },
  );
  const { data: lensOptions } = useGetLensOptionsQuery(undefined, {
    skip: !isLens,
  });
  const currentFrame =
    productData?.type === 'frame' ? productData.item : undefined;
  const currentLens =
    productData?.type === 'lens' ? productData.item : undefined;
  const product = currentFrame
    ? mapFrameToProduct(currentFrame)
    : currentLens
      ? mapLensToProduct(currentLens)
      : null;

  if (!parsedProductId) {
    return <Navigate replace to="/catalog" />;
  }

  if (isProductLoading || isProductFetching) {
    return (
      <section className={s.page}>
        <Container>
          <Spinner size="lg" />
        </Container>
      </section>
    );
  }

  if (isProductError || !product) {
    return (
      <section className={s.page}>
        <Container>
          <EmptyState title={t('catalog.productNotFound')} />
        </Container>
      </section>
    );
  }

  const sizes = currentFrame ? getFrameSizes(currentFrame) : product.sizes;
  const productDetails = {
    ...product,
    categoryKey: isFrame ? 'catalog.category.frames' : 'catalog.category.lenses',
    discountPercent: getDiscountPercent(product.price, product.oldPrice),
    gallery: product.images ?? [product.image],
    optionGroups: getLensOptionGroups(currentLens, lensOptions),
    selectedSize: sizes[0] ?? '',
    sizes,
  };
  const relatedProducts = (
    isFrame
      ? framesData?.results.map(mapFrameToProduct)
      : lensesData?.results.map(mapLensToProduct)
  )
    ?.filter((item) => item.id !== product.id)
    .slice(0, 4);

  return (
    <section className={s.page}>
      <Container>
        <div className={s.hero}>
          <ProductGallery
            images={productDetails.gallery}
            title={productDetails.title}
          />
          <ProductInfo key={productDetails.id} product={productDetails} />
        </div>

        <section className={s.relatedSection}>
          <h2>{t('product.related')}</h2>
          <div className={s.relatedGrid}>
            {relatedProducts?.map((relatedProduct) => (
              <RelatedProductCard
                key={relatedProduct.id}
                product={relatedProduct}
              />
            ))}
          </div>
        </section>
      </Container>
    </section>
  );
}
