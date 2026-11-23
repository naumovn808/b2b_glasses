export type NavLinkItem = {
  labelKey: string;
  href: string;
  authOnly?: boolean;
};

export const LINKS: NavLinkItem[] = [
  { labelKey: 'nav.catalog', href: '/catalog', authOnly: true },
  { labelKey: 'nav.news', href: '/news' },
  { labelKey: 'nav.education', href: '/education' },
  { labelKey: 'nav.about', href: '/about' },
  { labelKey: 'nav.contacts', href: '/contacts' },
];
