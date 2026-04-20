import { Container } from '@/shared/ui';
import { catalogProducts } from '../../CatalogPage/model/catalogContent';
import { Navigate, useParams } from 'react-router';
import { ProductGallery } from './ProductGallery';
import { createProductDetails } from '../model/productDetailsContent';
import { ProductInfo } from './ProductInfo';
import { RelatedProductCard } from './RelatedProductCard';
import s from './ProductDetailsPage.module.scss';
import { useTranslation } from 'react-i18next';

export function ProductDetailsPage() {
  const { t } = useTranslation();
  const { productId } = useParams();
  const product = catalogProducts.find((item) => item.id === productId);

  if (!product) {
    return <Navigate replace to="/catalog" />;
  }

  const productDetails = createProductDetails(product);
  const relatedProducts = catalogProducts
    .filter(
      (item) =>
        item.id !== product.id && item.categoryId === product.categoryId,
    )
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
            {relatedProducts.map((relatedProduct) => (
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
