import s from './OptionTags.module.scss';

type OptionTagsProps = {
  label: string;
  tags: string[];
};

export function OptionTags({ label, tags }: OptionTagsProps) {
  return (
    <div className={s.tagsRow}>
      <span>{label}</span>
      <div className={s.tags}>
        {tags.map((tag) => (
          <button key={tag} type="button">
            {tag}
          </button>
        ))}
      </div>
    </div>
  );
}
