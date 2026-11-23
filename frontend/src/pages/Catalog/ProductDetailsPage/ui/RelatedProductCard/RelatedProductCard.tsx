import { useState, type CSSProperties } from 'react';

import { Link } from 'react-router';
import clsx from 'clsx';
import type { ProductCardColor, ProductCardProduct } from '@/features/product-card';
import s from './RelatedProductCard.module.scss';
import { useAddCartItemMutation } from '@/entities/cart';
import { useTranslation } from 'react-i18next';

type RelatedProductCardProps = {
  product: ProductCardProduct;
};

type SwatchStyle = CSSProperties & {
  '--swatch-color'?: string;
  '--swatch-image'?: string;
};

function getSwatchStyle(color: ProductCardColor): SwatchStyle {
  return {
    '--swatch-color': color.value,
    '--swatch-image': color.backgroundImage,
  };
}

export function RelatedProductCard({ product }: RelatedProductCardProps) {
  const { t } = useTranslation();
  const [addCartItem, { isLoading: isAddingToCart }] =
    useAddCartItemMutation();
  const [selectedColorId, setSelectedColorId] = useState(
    product.colors[0]?.id ?? '',
  );
  const canAddToCart =
    !product.isSoldOut && !!product.apiProductId && !!product.apiProductType;

  const addProductToCart = async () => {
    if (!canAddToCart) return;

    await addCartItem({
      product_id: product.apiProductId!,
      product_type: product.apiProductType!,
      quantity: 1,
    }).unwrap();
  };

  return (
    <article className={s.card}>
      <Link className={s.imageWrap} to={`/catalog/${product.id}`}>
        <img className={s.image} src={product.image} alt={product.title} />

        {product.isSoldOut ? (
          <span className={s.soldOutBadge}>{t('common.soldOut')}</span>
        ) : null}
      </Link>

      <div className={s.body}>
        <Link className={s.productLink} to={`/catalog/${product.id}`}>
          <h3>{product.title}</h3>

          <div className={s.priceRow}>
            <span>{product.price}</span>
            {product.oldPrice ? <span>{product.oldPrice}</span> : null}
          </div>
        </Link>

        {product.colors.length > 0 ? (
          <div className={s.swatches} aria-label={t('common.color')}>
            {product.colors.map((color) => (
              <button
                className={clsx(
                  s.swatch,
                  selectedColorId === color.id && s.swatchActive,
                  color.backgroundImage && s.swatchPattern,
                )}
                key={color.id}
                type="button"
                style={getSwatchStyle(color)}
                title={t(`catalog.option.${color.id}`, color.name)}
                aria-label={t(`catalog.option.${color.id}`, color.name)}
                aria-pressed={selectedColorId === color.id}
                onClick={() => setSelectedColorId(color.id)}
              />
            ))}
          </div>
        ) : null}

        <div className={s.cartRow}>
          <button
            className={s.cartButton}
            type="button"
            disabled={!canAddToCart || isAddingToCart}
            onClick={addProductToCart}
          >
            {t('catalog.addToCart')}
          </button>
        </div>
      </div>
    </article>
  );
}
