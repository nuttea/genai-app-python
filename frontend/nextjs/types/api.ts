/**
 * Common API types and interfaces
 */

export interface ApiError {
  message: string;
  code?: string;
  details?: any;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy';
  service: string;
  version?: string;
  timestamp?: string;
}

