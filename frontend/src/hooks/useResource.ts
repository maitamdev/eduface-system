import { useCallback, useEffect, useRef, useState } from "react";
import { errorMessage } from "@/lib/format";

/** Ignore obsolete responses when filters change, a refresh overlaps, or a page unmounts. */
export function useResource<T>(loader: () => Promise<T>, initial: T) {
  const [data, setData] = useState(initial);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const generation = useRef(0);
  const reload = useCallback(async () => {
    const request = ++generation.current;
    setLoading(true);
    try {
      const next = await loader();
      if (request === generation.current) { setData(next); setError(null); }
    } catch (err) {
      if (request === generation.current) setError(errorMessage(err));
    } finally {
      if (request === generation.current) setLoading(false);
    }
  }, [loader]);
  useEffect(() => { void reload(); return () => { generation.current++; }; }, [reload]);
  return { data, setData, loading, error, reload };
}
