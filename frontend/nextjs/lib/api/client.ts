import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { API_CONFIG } from '@/lib/constants/config';

/**
 * Create axios instance with default configuration
 */
function createApiClient(baseURL: string, timeout: number): AxiosInstance {
  const client = axios.create({
    baseURL,
    timeout,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor
  client.interceptors.request.use(
    (config) => {
      // Add any auth tokens here if needed
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor
  client.interceptors.response.use(
    (response) => response,
    (error) => {
      // Log error to Datadog
      console.error('API Error:', {
        url: error.config?.url,
        method: error.config?.method,
        status: error.response?.status,
        message: error.message,
      });

      return Promise.reject(error);
    }
  );

  return client;
}

/**
 * API clients for each service
 */
export const voteExtractorClient = createApiClient(
  API_CONFIG.voteExtractor.baseUrl,
  API_CONFIG.voteExtractor.timeout
);

export const contentCreatorClient = createApiClient(
  API_CONFIG.contentCreator.baseUrl,
  API_CONFIG.contentCreator.timeout
);

/**
 * Generic API request handler
 */
export async function apiRequest<T>(
  config: AxiosRequestConfig,
  client: AxiosInstance = axios
): Promise<T> {
  const response = await client.request<T>(config);
  return response.data;
}

