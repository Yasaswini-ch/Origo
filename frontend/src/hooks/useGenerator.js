import { useCallback, useState } from "react";
import { generateProject, generateComponent, generatePreview } from "../services/api";

export default function useGenerator() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [output, setOutput] = useState(null);

  const handleCall = useCallback(async (fn, payload) => {
    setLoading(true);
    setError("");
    try {
      const result = await fn(payload);
      setOutput(result);
      return result;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
      throw e;
    } finally {
      setLoading(false);
    }
  }, []);

  const generate = useCallback(
    (payload) => handleCall(generateProject, payload),
    [handleCall]
  );

  const generateComponentHook = useCallback(
    (payload) => handleCall(generateComponent, payload),
    [handleCall]
  );

  const generatePreviewHook = useCallback(
    (payload) => handleCall(generatePreview, payload),
    [handleCall]
  );

  return {
    loading,
    error,
    output,
    generate,
    generateComponent: generateComponentHook,
    generatePreview: generatePreviewHook,
  };
}
