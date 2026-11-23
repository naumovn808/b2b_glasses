import { useState, type FormEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router';
import {
  selectUserIsAuth,
  selectUserData,
  useGetUserProfileQuery,
  useSetPasswordMutation,
  userActions,
} from '@/entities/user';
import { useGetOrderHistoryQuery, type Order } from '@/entities/cart';
import { Container, ModalWindowShell, Spinner } from '@/shared/ui';
import clsx from 'clsx';
import s from './ProfilePage.module.scss';

function formatCurrency(amount?: string | number): string {
  if (amount === undefined || amount === null) return '0 UZS';
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;
  if (isNaN(num)) return '0 UZS';
  return `${Math.round(num).toLocaleString('ru-RU')} UZS`;
}

function formatDate(dateStr: string, locale: string): string {
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString(locale === 'UZ' ? 'uz-UZ' : locale === 'EN' ? 'en-US' : 'ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateStr;
  }
}

export function ProfilePage() {
  const { t, i18n } = useTranslation();
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const isAuth = useSelector(selectUserIsAuth);
  const localUser = useSelector(selectUserData);

  const { data: userProfile, isLoading: isProfileLoading } = useGetUserProfileQuery(
    undefined,
    { skip: !isAuth },
  );

  const {
    data: ordersData,
    isLoading: isOrdersLoading,
  } = useGetOrderHistoryQuery(undefined, {
    skip: !isAuth,
  });

  const [setPasswordMutation, { isLoading: isPasswordSaving }] = useSetPasswordMutation();

  // Password change state
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordStatus, setPasswordStatus] = useState<{
    type: 'success' | 'error';
    text: string;
  } | null>(null);

  // Expanded orders accordion
  const [expandedOrders, setExpandedOrders] = useState<Set<number>>(new Set());

  // Logout modal state
  const [isLogoutModalOpen, setIsLogoutModalOpen] = useState(false);

  // Redirect or show login if not authenticated
  if (!isAuth) {
    return (
      <section className={s.page}>
        <Container>
          <div className={s.emptyBox}>
            <div className={s.emptyIcon}>🔒</div>
            <h2 className={s.emptyTitle}>{t('auth.title')}</h2>
            <p className={s.emptyText}>
              Для доступа к личному кабинету необходимо авторизоваться.
            </p>
            <button
              type="button"
              className={s.primaryBtn}
              onClick={() => dispatch(userActions.openAuthModal())}
            >
              {t('auth.submit')}
            </button>
          </div>
        </Container>
      </section>
    );
  }

  const user = userProfile || localUser;
  const companyName = userProfile?.company || t('profile.notSpecified');
  const displayName =
    user?.first_name || user?.last_name
      ? `${user.first_name || ''} ${user.last_name || ''}`.trim()
      : user?.username || user?.login || t('profile.notSpecified');

  const orders: Order[] = Array.isArray(ordersData)
    ? ordersData
    : (ordersData as any)?.results || [];

  const toggleOrderExpand = (orderId: number) => {
    setExpandedOrders((prev) => {
      const next = new Set(prev);
      if (next.has(orderId)) {
        next.delete(orderId);
      } else {
        next.add(orderId);
      }
      return next;
    });
  };

  const handlePasswordSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setPasswordStatus(null);

    if (newPassword.length < 4) {
      setPasswordStatus({
        type: 'error',
        text: t('profile.passwordTooShort'),
      });
      return;
    }

    if (newPassword !== confirmPassword) {
      setPasswordStatus({
        type: 'error',
        text: t('profile.passwordsDoNotMatch'),
      });
      return;
    }

    try {
      await setPasswordMutation({
        password: newPassword,
        password_confirm: confirmPassword,
      }).unwrap();

      setPasswordStatus({
        type: 'success',
        text: t('profile.passwordChanged'),
      });
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      const errorMsg =
        err?.data?.password?.[0] ||
        err?.data?.error ||
        'Произошла ошибка при смене пароля.';
      setPasswordStatus({
        type: 'error',
        text: errorMsg,
      });
    }
  };

  const handleConfirmLogout = () => {
    dispatch(userActions.logout());
    setIsLogoutModalOpen(false);
    navigate('/');
  };

  return (
    <section className={s.page}>
      <Container>
        {/* Page Header */}
        <div className={s.header}>
          <div className={s.titleWrapper}>
            <h1 className={s.title}>{t('profile.title')}</h1>
            <span className={s.b2bBadge}>✦ {t('profile.b2bClient')}</span>
          </div>

          <button
            type="button"
            className={s.logoutBtn}
            onClick={() => setIsLogoutModalOpen(true)}
          >
            {t('profile.logout')}
          </button>
        </div>

        {/* User Info & Security Grid */}
        <div className={s.grid}>
          {/* Company & Profile Info Card */}
          <div className={s.card}>
            <h2 className={s.cardTitle}>
              <span>🏢</span> {t('profile.company')}
            </h2>

            {isProfileLoading ? (
              <Spinner size="md" />
            ) : (
              <div className={s.infoList}>
                <div className={s.infoItem}>
                  <span className={s.infoLabel}>{t('profile.company')}:</span>
                  <span className={clsx(s.infoValue, s.companyHighlight)}>
                    {companyName}
                  </span>
                </div>

                <div className={s.infoItem}>
                  <span className={s.infoLabel}>{t('profile.login')}:</span>
                  <span className={s.infoValue}>{displayName}</span>
                </div>

                <div className={s.infoItem}>
                  <span className={s.infoLabel}>{t('profile.phone')}:</span>
                  <span className={s.infoValue}>
                    {user?.phone_number || t('profile.notSpecified')}
                  </span>
                </div>

                <div className={s.infoItem}>
                  <span className={s.infoLabel}>{t('profile.telegram')}:</span>
                  <span className={s.infoValue}>
                    {user?.telegram_username
                      ? `@${user.telegram_username}`
                      : t('profile.notSpecified')}
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Security & Password Card */}
          <div className={s.card}>
            <h2 className={s.cardTitle}>
              <span>🔒</span> {t('profile.securityTitle')}
            </h2>

            <form onSubmit={handlePasswordSubmit} className={s.formGroup}>
              <div className={s.field}>
                <label htmlFor="new-pass">{t('profile.newPassword')}</label>
                <input
                  id="new-pass"
                  type="password"
                  className={s.input}
                  placeholder="••••••••"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                />
              </div>

              <div className={s.field}>
                <label htmlFor="confirm-pass">{t('profile.confirmPassword')}</label>
                <input
                  id="confirm-pass"
                  type="password"
                  className={s.input}
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                />
              </div>

              {passwordStatus && (
                <div
                  className={clsx(
                    s.feedbackMessage,
                    passwordStatus.type === 'success'
                      ? s.successMessage
                      : s.errorMessage,
                  )}
                >
                  {passwordStatus.text}
                </div>
              )}

              <button
                type="submit"
                className={s.submitBtn}
                disabled={isPasswordSaving || !newPassword || !confirmPassword}
              >
                {isPasswordSaving ? <Spinner size="sm" /> : t('profile.savePassword')}
              </button>
            </form>

            <div className={s.telegramHintBox}>
              <div>{t('profile.telegramResetHint')}</div>
              <a
                href="https://t.me/glasses_uz_test_bot?start=reset_password"
                target="_blank"
                rel="noopener noreferrer"
                className={s.telegramLink}
              >
                💬 {t('profile.resetViaTelegram')} →
              </a>
            </div>
          </div>
        </div>

        {/* Orders History Section */}
        <div className={s.ordersSection}>
          <div className={s.sectionHeader}>
            <h2 className={s.sectionTitle}>{t('profile.ordersTitle')}</h2>
            <span className={s.ordersCount}>
              {t('profile.itemsCount', { count: orders.length })}
            </span>
          </div>

          {isOrdersLoading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '3rem 0' }}>
              <Spinner size="lg" />
            </div>
          ) : orders.length === 0 ? (
            <div className={s.emptyBox}>
              <div className={s.emptyIcon}>📦</div>
              <h3 className={s.emptyTitle}>{t('profile.noOrders')}</h3>
              <p className={s.emptyText}>{t('profile.noOrdersDesc')}</p>
              <button
                type="button"
                className={s.secondaryBtn}
                onClick={() => navigate('/catalog')}
              >
                {t('nav.catalog')}
              </button>
            </div>
          ) : (
            <div className={s.ordersList}>
              {orders.map((order) => {
                const isExpanded = expandedOrders.has(order.id);
                const orderStatus = order.status || 'pending';
                const statusLabel =
                  t(`profile.status.${orderStatus}`) || orderStatus;

                return (
                  <div key={order.id} className={s.orderCard}>
                    <div
                      className={s.orderHeader}
                      onClick={() => toggleOrderExpand(order.id)}
                    >
                      <div className={s.orderMeta}>
                        <span className={s.orderNumber}>
                          {t('profile.orderNum', { id: order.id })}
                        </span>
                        <span className={s.orderDate}>
                          {formatDate(order.created_at, i18n.language)}
                        </span>
                      </div>

                      <div className={s.orderRight}>
                        <span
                          className={clsx(
                            s.statusBadge,
                            s[`status_${orderStatus}`] || s.status_pending,
                          )}
                        >
                          {statusLabel}
                        </span>

                        <span className={s.orderPrice}>
                          {formatCurrency(order.total_price)}
                        </span>

                        <span
                          className={clsx(
                            s.expandIcon,
                            isExpanded && s.expandedIcon,
                          )}
                        >
                          ▼
                        </span>
                      </div>
                    </div>

                    {isExpanded && (
                      <div className={s.orderItems}>
                        <div className={s.itemsList}>
                          {order.items && order.items.length > 0 ? (
                            order.items.map((item) => (
                              <div key={item.id} className={s.orderItemRow}>
                                <div className={s.itemProduct}>
                                  {item.image ? (
                                    <img
                                      src={item.image}
                                      alt={item.product}
                                      className={s.itemImage}
                                    />
                                  ) : (
                                    <div className={s.itemNoImage}>Оптика</div>
                                  )}
                                  <span className={s.itemName}>
                                    {item.product}
                                  </span>
                                </div>

                                <div className={s.itemQtyPrice}>
                                  <span className={s.itemQty}>
                                    {item.quantity ?? 1} шт.
                                  </span>
                                  <span className={s.itemPrice}>
                                    {formatCurrency(
                                      item.total_price || item.price_at_order,
                                    )}
                                  </span>
                                </div>
                              </div>
                            ))
                          ) : (
                            <div style={{ color: '#7d8289', fontSize: '0.9rem' }}>
                              Информация о позициях заказа отсутствует
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </Container>

      {/* Logout Confirmation Modal */}
      <ModalWindowShell
        isOpen={isLogoutModalOpen}
        onClose={() => setIsLogoutModalOpen(false)}
        position="center"
        className={s.confirmModalOverlay}
        modalClassName={s.confirmModalShell}
      >
        <div className={s.confirmModal}>
          <h3 className={s.confirmModalTitle}>{t('profile.logout')}</h3>
          <p className={s.confirmModalText}>{t('profile.logoutConfirm')}</p>
          <div className={s.confirmModalActions}>
            <button
              type="button"
              className={s.confirmCancelBtn}
              onClick={() => setIsLogoutModalOpen(false)}
            >
              {t('profile.logoutCancel')}
            </button>
            <button
              type="button"
              className={s.confirmYesBtn}
              onClick={handleConfirmLogout}
            >
              {t('profile.logoutYes')}
            </button>
          </div>
        </div>
      </ModalWindowShell>
    </section>
  );
}
