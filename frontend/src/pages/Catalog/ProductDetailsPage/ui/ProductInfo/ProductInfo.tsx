import { useEffect, useState } from 'react';

import Chosen from '@/shared/assets/icons/chosen.svg?react';
import NotFillStarIcon from '@/shared/assets/icons/not-fill_star.svg?react';
import type { ProductDetails } from '../../model/productDetailsContent';
import ProductEye from '@/shared/assets/icons/product_eye.svg';
import { QuantityControl } from '@/shared/ui';
import StarIcon from '@/shared/assets/icons/star.svg?react';
import { addCartItem } from '@/entities/cart';
import clsx from 'clsx';
import s from './ProductInfo.module.scss';
import { useDispatch } from 'react-redux';
import { useTranslation } from 'react-i18next';

const TIMER_INITIAL_SECONDS = 5 * 24 * 60 * 60 + 59 * 60 + 47;
const SECONDS_IN_DAY = 24 * 60 * 60;
const SECONDS_IN_HOUR = 60 * 60;
const SECONDS_IN_MINUTE = 60;

function formatTimePart(value: number) {
  return String(value).padStart(2, '0');
}

function formatCountdown(totalSeconds: number) {
  const safeSeconds = Math.max(0, totalSeconds);
  const days = Math.floor(safeSeconds / SECONDS_IN_DAY);
  const hours = Math.floor((safeSeconds % SECONDS_IN_DAY) / SECONDS_IN_HOUR);
  const minutes = Math.floor(
    (safeSeconds % SECONDS_IN_HOUR) / SECONDS_IN_MINUTE,
  );
  const seconds = safeSeconds % SECONDS_IN_MINUTE;

  return [
    formatTimePart(days),
    formatTimePart(hours),
    formatTimePart(minutes),
    formatTimePart(seconds),
  ].join(' : ');
}

type ProductInfoProps = {
  product: ProductDetails;
};

export function ProductInfo({ product }: ProductInfoProps) {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const [quantity, setQuantity] = useState(1);
  const [timerSeconds, setTimerSeconds] = useState(TIMER_INITIAL_SECONDS);
  const [isChosen, setIsChosen] = useState(false);
  const [selectedSize, setSelectedSize] = useState(product.selectedSize);
  const [selectedLensOptions, setSelectedLensOptions] = useState(() =>
    Object.fromEntries(
      product.optionGroups?.map((group) => [
        group.id,
        group.selectedOptionId,
      ]) ?? [],
    ),
  );
  const [selectedColorId, setSelectedColorId] = useState(
    product.colors[0]?.id ?? '',
  );
  const selectedColor =
    product.colors.find((color) => color.id === selectedColorId) ??
    product.colors[0];
  const hasProductOptionGroups = Boolean(product.optionGroups?.length);

  useEffect(() => {
    const timerId = window.setInterval(() => {
      setTimerSeconds((currentSeconds) => Math.max(0, currentSeconds - 1));
    }, 1000);

    return () => window.clearInterval(timerId);
  }, []);

  const addProductToCart = () => {
    if (!selectedColor) return;

    dispatch(
      addCartItem({
        productId: product.id,
        title: product.title,
        image: product.image,
        price: product.price,
        oldPrice: product.oldPrice,
        color: t(`catalog.option.${selectedColor.id}`, selectedColor.name),
        colorId: selectedColor.id,
        size: selectedSize,
        stockText: t(product.frameNoticeKey),
        quantity,
      }),
    );
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

      <div className={s.ratingRow}>
        <span
          className={s.stars}
          aria-label={t('common.rating', { rating: product.rating })}
        >
          {Array.from({ length: 5 }, (_, index) =>
            index >= product.rating ? (
              <NotFillStarIcon key={index} aria-hidden="true" />
            ) : (
              <StarIcon key={index} aria-hidden="true" />
            ),
          )}
        </span>
        <span>({product.reviewCount})</span>
      </div>

      <div className={s.priceRow}>
        <span className={s.price}>{product.price}</span>
        {product.oldPrice ? (
          <span className={s.oldPrice}>{product.oldPrice}</span>
        ) : null}
        <span className={s.discount}>
          {t('productDetail.discountLabel', {
            percent: product.discountPercent,
          })}
        </span>
      </div>

      <div className={s.viewers}>
        <img src={ProductEye} alt="" aria-hidden="true" />{' '}
        {t(product.viewersTextKey)}
      </div>

      <div className={s.timer}>
        <span>{t(product.stockTextKey)}</span>
        <strong>{formatCountdown(timerSeconds)}</strong>
      </div>

      <div className={s.notice}>
        <span>{t(product.frameNoticeKey)}</span>
        <span className={s.noticeBar} />
      </div>

      {hasProductOptionGroups && product.optionGroups ? (
        <div className={s.lensOptions}>
          {product.optionGroups.map((group) => (
            <div className={s.lensOptionGroup} key={group.id}>
              <h2>{t(`catalog.filter.${group.id}`, group.title)}:</h2>
              <div className={s.lensOptionList}>
                {group.options.map((option) => (
                  <button
                    className={clsx(
                      s.lensOption,
                      option.id === selectedLensOptions[group.id] &&
                        s.lensOptionActive,
                    )}
                    key={option.id}
                    type="button"
                    aria-pressed={option.id === selectedLensOptions[group.id]}
                    onClick={() =>
                      setSelectedLensOptions((currentOptions) => ({
                        ...currentOptions,
                        [group.id]: option.id,
                      }))
                    }
                  >
                    {t(`catalog.option.${option.id}`, option.label)}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <>
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

      {/* {!hasProductOptionGroups ? ( */}
      <div className={s.cartRow}>
        <QuantityControl
          className={s.quantity}
          decreaseDisabled={quantity <= 1}
          quantity={quantity}
          onDecrease={() => setQuantity((current) => Math.max(1, current - 1))}
          onIncrease={() => setQuantity((current) => current + 1)}
        />

        <button
          className={s.cartButton}
          onClick={addProductToCart}
          type="button"
        >
          {t('catalog.addToCart')}
        </button>
      </div>
      {/* ) : null} */}
    </section>
  );
}
