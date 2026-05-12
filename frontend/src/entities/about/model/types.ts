export type Certificate = {
  id: number;
  title?: string;
  image: string;
};

export type Partner = {
  id: number;
  name?: string;
  image: string;
  link?: string | null;
};

export type AboutUs = {
  title?: string;
  title_ru?: string | null;
  title_en?: string | null;
  title_uz?: string | null;
  text: string;
  certificates: Certificate[];
  partners: Partner[];
};
