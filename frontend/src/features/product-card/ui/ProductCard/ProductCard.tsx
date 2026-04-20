import { useState, type CSSProperties } from 'react';

import {
  addCartItem,
  type CartRootState,
  makeCartItemId,
  selectCartItemById,
} from '@/entities/cart';
import { CartQuantityControl } from '@/features/cart-quantity-control';
import clsx from 'clsx';
import { Link } from 'react-router';
import type { Product, ProductColor } from '@/entities/product';
import { useDispatch, useSelector } from 'react-redux';
import s from './ProductCard.module.scss';
import { useTranslation } from 'react-i18next';

type ProductCardProps = {
  product: Product;
  className?: string;
  initialQuantity?: number;
  onAddToCart?: (product: Product, quantity: number) => void;
};

type SwatchStyle = CSSProperties & {
  '--swatch-color'?: string;
  '--swatch-image'?: string;
};

function getSwatchStyle(color: ProductColor): SwatchStyle {
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
        quantity: initialQuantity,
      }
    : null;
  const cartItemId = cartItemPayload ? makeCartItemId(cartItemPayload) : '';
  const cartItem = useSelector((state: CartRootState) =>
    selectCartItemById(state, cartItemId),
  );
  const quantityInCart = cartItem?.quantity ?? 0;

  const addProductToCart = () => {
    if (product.isSoldOut || !cartItemPayload) return;

    onAddToCart?.(product, initialQuantity);

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
          {cartItem && quantityInCart > 0 ? (
            <div className={s.infoAction}>
              <CartQuantityControl
                className={s.quantity}
                disabled={product.isSoldOut}
                itemId={cartItem.id}
                quantity={quantityInCart}
              />
            </div>
          ) : null}
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
            disabled={product.isSoldOut}
            onClick={addProductToCart}
          >
            {t('catalog.addToCart')}
          </button>
        </div>
      </div>
    </div>
  );
}
