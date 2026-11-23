import {
  selectIsAuthModalOpen,
  userActions,
} from '@/entities/user';
import { useDispatch, useSelector } from 'react-redux';

import { AuthModal } from '@/widgets/AuthModal/ui/AuthModal';
import { Footer } from '../../footer/ui/Footer';
import { Header } from '../../header/ui/Header';
import { Outlet } from 'react-router';
import { useEffect } from 'react';

export function Layout() {
  const dispatch = useDispatch();
  const isAuthModalOpen = useSelector(selectIsAuthModalOpen);

  useEffect(() => {
    dispatch(userActions.initAuthData());
  }, [dispatch]);

  return (
    <>
      <Header />
      <main>
        <Outlet />
      </main>
      <Footer />
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => dispatch(userActions.closeAuthModal())}
      />
    </>
  );
}
