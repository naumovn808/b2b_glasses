import { AnimatePresence, motion } from 'framer-motion';

import clsx from 'clsx';
import s from './ProductGallery.module.scss';
import { useState } from 'react';

type ProductGalleryProps = {
  images: string[];
  title: string;
};

export function ProductGallery({ images, title }: ProductGalleryProps) {
  const [activeImage, setActiveImage] = useState(images[0] ?? '');

  return (
    <div className={s.gallery}>
      <div className={s.thumbs}>
        {images.map((image, index) => (
          <button
            className={clsx(s.thumb, activeImage === image && s.thumbActive)}
            key={`${image}-${index}`}
            type="button"
            onClick={() => setActiveImage(image)}
          >
            <img src={image} alt={`${title} ${index + 1}`} />
          </button>
        ))}
      </div>

      <div className={s.mainImage}>
        <AnimatePresence mode="wait" initial={false}>
          <motion.img
            key={activeImage}
            src={activeImage}
            alt={title}
            initial={{ opacity: 0, scale: 1.025 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.985 }}
            transition={{ duration: 0.24, ease: 'easeOut' }}
          />
        </AnimatePresence>
      </div>
    </div>
  );
}
