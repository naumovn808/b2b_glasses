import { AboutUsPage } from '@/pages/AboutUsPage';
import { CatalogPage } from '@/pages/Catalog/CatalogPage';
import { ContactsPage } from '@/pages/ContactsPage';
import { EducationArticlePage } from '@/pages/Education/EducationArticlePage';
import { EducationPage } from '@/pages/Education/EducationPage';
import { HomePage } from '@/pages/HomePage';
import { Layout } from '@/widgets/layoutWidgets/layout/ui/Layout';
import { LensSelectionPage } from '@/pages/PrescriptionLenses/LensSelectionPage';
import { NewsArticlePage } from '@/pages/News/NewsArticlePage';
import { NewsPage } from '@/pages/News/NewsPage';
import { PrescriptionOrderPage } from '@/pages/PrescriptionLenses/PrescriptionOrderPage';
import { ProductDetailsPage } from '@/pages/Catalog/ProductDetailsPage';
import { createBrowserRouter } from 'react-router';

export default createBrowserRouter([
  {
    element: <Layout />,
    children: [
      {
        path: '/',
        element: <HomePage />,
      },
      {
        path: '/news',
        element: <NewsPage />,
      },
      {
        path: '/catalog',
        element: <CatalogPage />,
      },
      {
        path: '/catalog/:productId',
        element: <ProductDetailsPage />,
      },
      {
        path: '/news/:newsId',
        element: <NewsArticlePage />,
      },
      {
        path: '/education',
        element: <EducationPage />,
      },
      {
        path: '/education/:educationSlug',
        element: <EducationArticlePage />,
      },
      {
        path: '/about',
        element: <AboutUsPage />,
      },
      {
        path: '/contacts',
        element: <ContactsPage />,
      },
      {
        path: '/prescription-lenses',
        element: <PrescriptionOrderPage />,
      },
      {
        path: '/prescription-lenses/select',
        element: <LensSelectionPage />,
      },
    ],
  },
]);
