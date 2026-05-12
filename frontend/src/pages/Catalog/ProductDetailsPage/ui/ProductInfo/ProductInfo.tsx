import Chosen from '@/shared/assets/icons/chosen.svg?react';
import ProductEye from '@/shared/assets/icons/product_eye.svg';
import {
  addCartItem as addLocalCartItem,
  type CartRootState,
  makeCartItemId,
  selectCartItemById,
  useAddCartItemMutation,
} from '@/entities/cart';
import { CartQuantityControl } from '@/features/cart-quantity-control';
import { QuantityControl, Spinner } from '@/shared/ui';
import clsx from 'clsx';
import s from './ProductInfo.module.scss';
import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useTranslation } from 'react-i18next';
import type { ProductCardProduct } from '@/features/product-card';

export type ProductDetailsOptionGroup = {
  id: string;
  title: string;
  options: Array<{
    id: string;
    isSelected: boolean;
    label: string;
  }>;
};

export type ProductDetails = ProductCardProduct & {
  categoryKey: string;
  discountPercent: number;
  gallery: string[];
  selectedSize: string;
  optionGroups?: ProductDetailsOptionGroup[];
};

type ProductInfoProps = {
  product: ProductDetails;
};

export function ProductInfo({ product }: ProductInfoProps) {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [addCartItem, { isLoading: isAddingToCart }] = useAddCartItemMutation();
  const [quantity, setQuantity] = useState(1);
  const [isChosen, setIsChosen] = useState(false);
  const [selectedSize, setSelectedSize] = useState(product.selectedSize);
  const [selectedColorId, setSelectedColorId] = useState(
    product.colors[0]?.id ?? '',
  );
  const selectedColor =
    product.colors.find((color) => color.id === selectedColorId) ??
    product.colors[0];
  const hasProductOptionGroups = Boolean(product.optionGroups?.length);
  const hasSizes = product.sizes.length > 0;
  const canAddToCart =
    !product.isSoldOut && !!product.apiProductId && !!product.apiProductType;
  const cartItemPayload = selectedColor
    ? {
        productId: product.id,
        title: product.title,
        image: product.image,
        price: product.price,
        oldPrice: product.oldPrice,
        color: t(`catalog.option.${selectedColor.id}`, selectedColor.name),
        colorId: selectedColor.id,
        size: selectedSize || '-',
        stockText: t('common.inStock'),
        quantity,
      }
    : null;
  const cartItemId = cartItemPayload ? makeCartItemId(cartItemPayload) : '';
  const cartItem = useSelector((state: CartRootState) =>
    selectCartItemById(state, cartItemId),
  );
  const quantityInCart = cartItem?.quantity ?? 0;
  const hasStockLimit = typeof product.stock === 'number';
  const isInitialQuantityStockReached = hasStockLimit && quantity >= product.stock!;
  const isCartQuantityStockReached =
    hasStockLimit && quantityInCart >= product.stock!;

  const addProductToCart = async () => {
    if (
      !canAddToCart ||
      !cartItemPayload ||
      (hasStockLimit && quantityInCart + quantity > product.stock!)
    ) {
      return;
    }

    try {
      await addCartItem({
        product_id: product.apiProductId!,
        product_type: product.apiProductType!,
        quantity,
      }).unwrap();
    } catch {
      return;
    }

    dispatch(addLocalCartItem(cartItemPayload));
  };
  return (
    <section className={s.info}>
      <div className={s.topLine}>
        <span className={s.category}>{t(product.categoryKey)}</span>
        <button
          className={clsx(s.favoriteButton, isChosen && s.favoriteButtonActive)}
          type="button"
          aria-label={t('common.favorite')}
          aria-pressed={isChosen}
          onClick={() => setIsChosen((current) => !current)}
        >
          <Chosen aria-hidden="true" />
        </button>
      </div>

      <h1>{product.title}</h1>

      <div className={s.priceRow}>
        <span className={s.price}>{product.price}</span>
        {product.oldPrice ? (
          <span className={s.oldPrice}>{product.oldPrice}</span>
        ) : null}
        {product.discountPercent > 0 ? (
          <span className={s.discount}>
            {t('productDetail.discountLabel', {
              percent: product.discountPercent,
            })}
          </span>
        ) : null}
      </div>

      <div className={s.viewers}>
        <img src={ProductEye} alt="" aria-hidden="true" />
        {t('productDetail.viewers.productNow', { quantity: 24 })}
      </div>

      {hasProductOptionGroups && product.optionGroups ? (
        <div className={s.lensOptions}>
          {product.optionGroups.map((group) => (
            <div className={s.lensOptionGroup} key={group.id}>
              <h2>{t(`catalog.filter.${group.id}`, group.title)}:</h2>
              <div className={s.lensOptionList}>
                {group.options.map((option) => (
                  <span
                    className={clsx(
                      s.lensOption,
                      option.isSelected && s.lensOptionActive,
                    )}
                    key={option.id}
                  >
                    {t(`catalog.option.${option.id}`, option.label)}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <>
          {hasSizes ? (
            <div className={s.optionGroup}>
              <h2>
                {t('common.size')}: {selectedSize}
              </h2>
              <div className={s.sizes}>
                {product.sizes.map((size) => (
                  <button
                    className={clsx(
                      s.sizeButton,
                      selectedSize === size && s.sizeActive,
                    )}
                    key={size}
                    type="button"
                    onClick={() => setSelectedSize(size)}
                  >
                    {size}
                  </button>
                ))}
              </div>
            </div>
          ) : null}

          <div className={s.optionGroup}>
            <h2>
              {t('common.color')}:{' '}
              {t(
                `catalog.option.${selectedColorId}`,
                product.colors.find((color) => color.id === selectedColorId)
                  ?.name ?? product.colors[0]?.name,
              )}
            </h2>
            <div className={s.colors}>
              {product.colors.map((color) => (
                <button
                  className={clsx(
                    s.colorButton,
                    selectedColorId === color.id && s.colorActive,
                  )}
                  key={color.id}
                  type="button"
                  style={{ backgroundColor: color.value }}
                  aria-label={t(`catalog.option.${color.id}`, color.name)}
                  aria-pressed={selectedColorId === color.id}
                  onClick={() => setSelectedColorId(color.id)}
                />
              ))}
            </div>
          </div>
        </>
      )}

      <div className={s.cartRow}>
        {cartItem && quantityInCart > 0 ? (
          <CartQuantityControl
            className={s.quantity}
            disabled={product.isSoldOut}
            increaseDisabled={isCartQuantityStockReached}
            itemId={cartItem.id}
            quantity={quantityInCart}
          />
        ) : (
          <QuantityControl
            className={s.quantity}
            decreaseDisabled={quantity <= 1}
            increaseDisabled={isInitialQuantityStockReached}
            quantity={quantity}
            onDecrease={() =>
              setQuantity((current) => Math.max(1, current - 1))
            }
            onIncrease={() =>
              setQuantity((current) =>
                hasStockLimit ? Math.min(current + 1, product.stock!) : current + 1,
              )
            }
          />
        )}

        <button
          className={s.cartButton}
          disabled={
            !canAddToCart ||
            isAddingToCart ||
            (hasStockLimit && quantityInCart + quantity > product.stock!)
          }
          onClick={addProductToCart}
          type="button"
        >
          {isAddingToCart ? <Spinner size="sm" /> : t('catalog.addToCart')}
        </button>
      </div>
    </section>
  );
}
