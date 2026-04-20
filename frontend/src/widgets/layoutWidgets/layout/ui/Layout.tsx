import { Footer } from '../../footer/ui/Footer';
import { Header } from '../../header/ui/Header';
import { Outlet } from 'react-router';
import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { selectUserInited, selectUserIsAuth, userActions } from '@/entities/user';
import { AuthModal } from '@/widgets/AuthModal/ui/AuthModal';

export function Layout() {
  const dispatch = useDispatch();
  const isAuth = useSelector(selectUserIsAuth);
  const inited = useSelector(selectUserInited);

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
      {inited && !isAuth && (
        <AuthModal isOpen={!isAuth} />
      )}
    </>
  );
}
