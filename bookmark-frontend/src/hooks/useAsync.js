import { useCallback, useEffect, useRef, useState } from 'react';

/* ============================================================
   useAsync — tiny data-fetching hook for consistent
   loading / error / reload handling across pages.

   Usage:
     const { data, loading, error, reload } = useAsync(
       () => someAPI.get(),
       [dep1, dep2],        // re-runs when deps change
       initialData,         // optional
     );
   ============================================================ */

export default function useAsync(asyncFn, deps = [], initialData = null) {
  const [data, setData] = useState(initialData);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const mounted = useRef(true);

  // Keep the latest fn without forcing it into the deps array.
  const fnRef = useRef(asyncFn);
  fnRef.current = asyncFn;

  const run = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fnRef.current();
      if (mounted.current) setData(result);
      return result;
    } catch (err) {
      if (mounted.current) {
        setError(err?.response?.data?.detail || err?.message || 'Something went wrong.');
      }
      return undefined;
    } finally {
      if (mounted.current) setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    mounted.current = true;
    run();
    return () => { mounted.current = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return { data, loading, error, reload: run, setData };
}
