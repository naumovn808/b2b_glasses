import { useEffect, useState } from 'react';

export function useDebouncedValue<T>(value: T, delay: number) {
  const [debouncedValue, setDebouncedValue] = useState(value);
  const [isDebouncing, setIsDebouncing] = useState(false);

  useEffect(() => {
    setIsDebouncing(true);

    const timeoutId = window.setTimeout(() => {
      setDebouncedValue(value);
      setIsDebouncing(false);
    }, delay);

    return () => window.clearTimeout(timeoutId);
  }, [delay, value]);

  return [debouncedValue, isDebouncing] as const;
}
