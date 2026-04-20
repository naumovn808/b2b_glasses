import { useMemo, useState } from 'react';

import { AccordionItem } from '@/shared/ui';
import type { CatalogFilterGroup } from '../../model/catalogContent';
import { Link } from 'react-router';
import clsx from 'clsx';
import s from './CatalogFilters.module.scss';
import { useTranslation } from 'react-i18next';

export type ActiveCatalogFilters = Record<string, string[]>;

type FilterActionButton = {
  label: string;
  onClick?: () => void;
  to?: string;
};

function isFilterActive(
  activeFilters: ActiveCatalogFilters,
  groupId: string,
  optionId: string,
) {
  return activeFilters[groupId]?.includes(optionId) ?? false;
}

export function CatalogFilters({
  activeFilters,
  actionButton,
  compact = false,
  groups,
  onFilterToggle,
  reserveActionSpace = true,
  showTitle = true,
}: {
  activeFilters: ActiveCatalogFilters;
  actionButton?: FilterActionButton;
  compact?: boolean;
  groups: CatalogFilterGroup[];
  onFilterToggle: (groupId: string, optionId: string) => void;
  reserveActionSpace?: boolean;
  showTitle?: boolean;
}) {
  const { t } = useTranslation();
  const groupIds = useMemo(() => groups.map((group) => group.id), [groups]);
  const groupSignature = groupIds.join('|');
  const [openState, setOpenState] = useState<{
    groupSignature: string;
    groupIds: string[];
  }>({
    groupSignature,
    groupIds: [],
  });
  const openGroupIds =
    openState.groupSignature === groupSignature ? openState.groupIds : [];

  const toggleGroup = (groupId: string) => {
    setOpenState((currentState) => {
      const currentGroupIds =
        currentState.groupSignature === groupSignature
          ? currentState.groupIds
          : [];

      return {
        groupSignature,
        groupIds: currentGroupIds.includes(groupId)
          ? currentGroupIds.filter((id) => id !== groupId)
          : [...currentGroupIds, groupId],
      };
    });
  };

  return (
    <aside className={clsx(s.filters, compact && s.filtersCompact)}>
      <div className={s.actionSlot} aria-hidden={!actionButton || undefined}>
        {actionButton ? (
          actionButton.to ? (
            <Link
              className={s.actionButton}
              to={actionButton.to}
              onClick={actionButton.onClick}
            >
              {actionButton.label}
            </Link>
          ) : (
            <button
              className={s.actionButton}
              type="button"
              onClick={actionButton.onClick}
            >
              {actionButton.label}
            </button>
          )
        ) : reserveActionSpace ? (
          <span className={s.actionButtonPlaceholder} />
        ) : null}
      </div>

      {showTitle ? <h2>{t('catalog.filters')}</h2> : null}

      {groups.map((group) => {
        const isOpen = openGroupIds.includes(group.id);

        if (group.variant === 'colors') {
          return (
            <AccordionItem
              buttonClassName={s.groupHeader}
              className={s.group}
              isOpen={isOpen}
              key={group.id}
              title={t(`catalog.filter.${group.id}`, group.title)}
              onToggle={() => toggleGroup(group.id)}
            >
              <div className={s.colorGrid}>
                {group.options.map((option) => (
                  <button
                    className={clsx(
                      s.colorOption,
                      isFilterActive(activeFilters, group.id, option.id) &&
                        s.colorOptionActive,
                    )}
                    key={option.id}
                    type="button"
                    style={{ backgroundColor: option.value }}
                    aria-label={t(`catalog.option.${option.id}`, option.label)}
                    aria-pressed={isFilterActive(
                      activeFilters,
                      group.id,
                      option.id,
                    )}
                    onClick={() => onFilterToggle(group.id, option.id)}
                  />
                ))}
              </div>
            </AccordionItem>
          );
        }
        if (group.variant === 'size') {
          return (
            <AccordionItem
              buttonClassName={s.groupHeader}
              className={s.group}
              isOpen={isOpen}
              key={group.id}
              title={t(`catalog.filter.${group.id}`, group.title)}
              onToggle={() => toggleGroup(group.id)}
            >
              <div className={s.sizeGrid}>
                {group.options.map((option) => (
                  <button
                    className={clsx(
                      s.sizeOption,
                      isFilterActive(activeFilters, group.id, option.id) &&
                        s.sizeOptionActive,
                    )}
                    key={option.id}
                    type="button"
                    aria-pressed={isFilterActive(
                      activeFilters,
                      group.id,
                      option.id,
                    )}
                    onClick={() => onFilterToggle(group.id, option.id)}
                  >
                    {option.label}{' '}
                  </button>
                ))}
              </div>
            </AccordionItem>
          );
        }
        return (
          <AccordionItem
            buttonClassName={s.groupHeader}
            className={s.group}
            isOpen={isOpen}
            key={group.id}
            title={t(`catalog.filter.${group.id}`, group.title)}
            onToggle={() => toggleGroup(group.id)}
          >
            <div
              className={
                group.variant === 'inline' ? s.inlineOptions : s.stackOptions
              }
            >
              {group.options.map((option) => (
                <button
                  className={clsx(
                    s.textOption,
                    isFilterActive(activeFilters, group.id, option.id) &&
                      s.textOptionActive,
                  )}
                  key={option.id}
                  type="button"
                  aria-pressed={isFilterActive(
                    activeFilters,
                    group.id,
                    option.id,
                  )}
                  onClick={() => onFilterToggle(group.id, option.id)}
                >
                  {t(`catalog.option.${option.id}`, option.label)}
                </button>
              ))}
            </div>
          </AccordionItem>
        );
      })}
    </aside>
  );
}
