import { useState, type CSSProperties } from 'react';

import { addCartItem } from '@/entities/cart';
import { QuantityControl, Spinner } from '@/shared/ui';
import clsx from 'clsx';
import { Link } from 'react-router';
import type { ProductCardColor, ProductCardProduct } from '../../model/types';
import { useDispatch } from 'react-redux';
import s from './ProductCard.module.scss';
import { useTranslation } from 'react-i18next';

type ProductCardProps = {
  product: ProductCardProduct;
  className?: string;
  initialQuantity?: number;
  onAddToCart?: (
    product: ProductCardProduct,
    quantity: number,
  ) => Promise<void> | void;
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

export function ProductCard({
  className,
  initialQuantity = 1,
  onAddToCart,
  product,
}: ProductCardProps) {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [quantity, setQuantity] = useState(initialQuantity);
  const [isAddingToCart, setIsAddingToCart] = useState(false);
  const [selectedColorId, setSelectedColorId] = useState(
    product.colors[0]?.id ?? '',
  );
  const selectedColor =
    product.colors.find((color) => color.id === selectedColorId) ??
    product.colors[0];
  const cartItemPayload = selectedColor
    ? {
        productId: product.id,
        title: product.title,
        image: product.image,
        price: product.price,
        oldPrice: product.oldPrice,
        color: t(`catalog.option.${selectedColor.id}`, selectedColor.name),
        colorId: selectedColor.id,
        size: '-',
        stockText: t('common.inStock'),
        quantity,
      }
    : null;
  const hasStockLimit = typeof product.stock === 'number';
  const isQuantityStockReached = hasStockLimit && quantity >= product.stock!;

  const addProductToCart = async () => {
    if (
      product.isSoldOut ||
      !cartItemPayload ||
      (hasStockLimit && quantity > product.stock!)
    ) {
      return;
    }

    setIsAddingToCart(true);

    try {
      await onAddToCart?.(product, quantity);
    } catch {
      return;
    } finally {
      setIsAddingToCart(false);
    }

    dispatch(addCartItem(cartItemPayload));
  };

  return (
    <div className={clsx(s.card, className)}>
      <Link className={s.imageWrap} to={`/catalog/${product.id}`}>
        <img className={s.image} src={product.image} alt={product.title} />

        {product.isSoldOut ? (
          <span className={s.soldOutBadge}>{t('common.soldOut')}</span>
        ) : null}
      </Link>

      <div className={s.body}>
        <div className={s.info}>
          <Link className={s.infoTitle} to={`/catalog/${product.id}`}>
            <h3 className={s.title}>{product.title}</h3>

            <div className={s.priceRow}>
              <span className={s.price}>{product.price}</span>
              {product.oldPrice ? (
                <span className={s.oldPrice}>{product.oldPrice}</span>
              ) : null}
            </div>
          </Link>
          <div className={s.infoAction}>
            <QuantityControl
              className={s.quantity}
              decreaseDisabled={quantity <= 1}
              disabled={product.isSoldOut}
              increaseDisabled={isQuantityStockReached}
              quantity={quantity}
              onDecrease={() =>
                setQuantity((current) => Math.max(1, current - 1))
              }
              onIncrease={() =>
                setQuantity((current) =>
                  hasStockLimit
                    ? Math.min(current + 1, product.stock!)
                    : current + 1,
                )
              }
            />
          </div>
        </div>

        <div className={s.bodyBottom}>
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
                aria-label={t(`catalog.option.${color.id}`, color.name)}
                aria-pressed={selectedColorId === color.id}
                onClick={() => setSelectedColorId(color.id)}
              />
            ))}
          </div>
          <button
            className={s.cartButton}
            type="button"
            disabled={
              product.isSoldOut ||
              isAddingToCart ||
              (hasStockLimit && quantity > product.stock!)
            }
            onClick={addProductToCart}
          >
            {isAddingToCart ? <Spinner size="sm" /> : t('catalog.addToCart')}
          </button>
        </div>
      </div>
    </div>
  );
}
