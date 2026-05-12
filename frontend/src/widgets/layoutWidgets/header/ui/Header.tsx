import { Container, IconButton } from '@/shared/ui';
import { Link, NavLink } from 'react-router';
import { selectCartTotalQuantity, useGetCartQuery } from '@/entities/cart';
import {
  selectUserIsAuth,
  selectUserToken,
  userActions,
} from '@/entities/user';
import { useDispatch, useSelector } from 'react-redux';

import BurgerIcon from '@/shared/assets/icons/header/burger-menu.svg?react';
import BurgerModal from '@/widgets/BurgerModal/ui/BurgerModal';
import CartIcon from '@/shared/assets/icons/header/cart.svg?react';
import { CartModal } from '../../../CartModal/ui/CartModal';
import { LINKS } from '../model/links';
import { LanguageSwitch } from '@/features/switch-language';
import LogoUrl from '@/shared/assets/icons/header/logo.svg';
import ProfileIcon from '@/shared/assets/icons/header/profile.svg?react';
import clsx from 'clsx';
import s from './Header.module.scss';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

export function Header() {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const token = useSelector(selectUserToken);
  const [isBurgerOpen, setIsBurgerOpen] = useState(false);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const localCartTotalQuantity = useSelector(selectCartTotalQuantity);
  const { data: cart } = useGetCartQuery(undefined, {
    skip: !token,
  });
  const serverCartTotalQuantity =
    cart?.items.reduce((total, item) => total + (item.quantity ?? 1), 0) ?? 0;
  const cartTotalQuantity = Math.max(
    localCartTotalQuantity,
    serverCartTotalQuantity,
  );
  const isAuth = useSelector(selectUserIsAuth);

  const handleAccountClick = () => {
    if (isAuth) {
      if (window.confirm('Вы уверены, что хотите выйти?')) {
        dispatch(userActions.logout());
      }
    }
  };

  return (
    <header className={s.header}>
      <Container>
        <nav className={s.headerInner}>
          <Link to={'/'} className={s.headerLogo}>
            <img src={LogoUrl} alt="Hikari Pure Vision" />
          </Link>

          <div className={s.headerLinks}>
            <ul className={s.navList}>
              {LINKS.map((item) => (
                <li key={item.href}>
                  <NavLink
                    className={({ isActive }) =>
                      clsx(s.navLink, isActive && s.navLinkActive)
                    }
                    to={item.href}
                  >
                    {t(item.labelKey)}
                  </NavLink>
                </li>
              ))}
            </ul>
          </div>

          <div className={s.headerActions}>
            <IconButton
              aria-label="Menu"
              className={clsx(s.actionBtn, s.burger)}
              icon={<BurgerIcon />}
              onClick={() => setIsBurgerOpen(true)}
            />
            <LanguageSwitch />
            <IconButton
              aria-label="Cart"
              className={clsx(s.actionBtn, s.cartBtn)}
              icon={
                <>
                  <CartIcon />
                  {cartTotalQuantity > 0 ? (
                    <span className={s.cartBadge}>{cartTotalQuantity}</span>
                  ) : null}
                </>
              }
              onClick={() => setIsCartOpen(true)}
            />
            <IconButton
              aria-label="Account"
              onClick={handleAccountClick}
              className={clsx(s.actionBtn, isAuth && s.activeAuth)}
              icon={<ProfileIcon />}
            />
          </div>
        </nav>
      </Container>

      <BurgerModal
        isOpen={isBurgerOpen}
        onClose={() => setIsBurgerOpen(false)}
      />
      <CartModal isOpen={isCartOpen} onClose={() => setIsCartOpen(false)} />
    </header>
  );
}
