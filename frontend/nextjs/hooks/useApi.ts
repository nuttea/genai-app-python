import { useState } from 'react';
import { AxiosError } from 'axios';

/**
 * Generic hook for API requests with loading and error states
 */
export function useApi<T, P = any>() {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const execute = async (apiCall: (params: P) => Promise<T>, params: P): Promise<T | null> => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiCall(params);
      setData(result);
      return result;
    } catch (err) {
      const errorMessage = err instanceof AxiosError
        ? err.response?.data?.message || err.message
        : 'An unexpected error occurred';

      setError(errorMessage);
      console.error('API Error:', err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setData(null);
    setError(null);
    setLoading(false);
  };

  return { data, loading, error, execute, reset };
}

/**
 * Hook specifically for file uploads with progress tracking
 */
export function useFileUpload() {
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const upload = async <T,>(
    uploadFn: (file: File, onProgress?: (progress: number) => void) => Promise<T>,
    file: File
  ): Promise<T | null> => {
    setUploading(true);
    setProgress(0);
    setError(null);

    try {
      const result = await uploadFn(file, setProgress);
      setProgress(100);
      return result;
    } catch (err) {
      const errorMessage = err instanceof AxiosError
        ? err.response?.data?.message || err.message
        : 'Upload failed';

      setError(errorMessage);
      console.error('Upload Error:', err);
      return null;
    } finally {
      setUploading(false);
    }
  };

  const reset = () => {
    setProgress(0);
    setError(null);
    setUploading(false);
  };

  return { progress, uploading, error, upload, reset };
}

