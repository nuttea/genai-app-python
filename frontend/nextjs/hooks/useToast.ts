import toast, { Toast } from 'react-hot-toast';

/**
 * Custom hook for toast notifications with Datadog theme
 */
export function useToast() {
  const showToast = (message: string, type: 'success' | 'error' | 'loading' = 'success') => {
    switch (type) {
      case 'success':
        return toast.success(message, {
          duration: 4000,
          style: {
            background: '#27AE60',
            color: '#fff',
          },
        });

      case 'error':
        return toast.error(message, {
          duration: 5000,
          style: {
            background: '#E74C3C',
            color: '#fff',
          },
        });

      case 'loading':
        return toast.loading(message, {
          style: {
            background: '#774AA4',
            color: '#fff',
          },
        });

      default:
        return toast(message);
    }
  };

  const success = (message: string) => showToast(message, 'success');
  const error = (message: string) => showToast(message, 'error');
  const loading = (message: string) => showToast(message, 'loading');
  const dismiss = (toastId?: string) => toast.dismiss(toastId);

  return {
    showToast,
    success,
    error,
    loading,
    dismiss,
  };
}

