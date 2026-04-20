import './app/styles/index.css';
import './app/providers/i18n';

import { Provider } from 'react-redux';
import { RouterProvider } from 'react-router';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import router from './app/providers/routes/routes';
import { store } from './app/providers/store/store';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Provider store={store}>
      <RouterProvider router={router} />
    </Provider>
  </StrictMode>,
);
