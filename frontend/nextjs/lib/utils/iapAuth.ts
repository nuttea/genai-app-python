/**
 * IAP (Identity-Aware Proxy) Authentication Utilities
 * 
 * Parses and validates Google Cloud IAP JWT headers
 */

export interface IAPUser {
  email: string;
  userId: string;
  name?: string;
  picture?: string;
  authMethod: 'iap' | 'development';
  raw?: any;
}

/**
 * Parse IAP JWT token (without verification - server-side only)
 * 
 * Note: This does NOT verify the JWT signature. 
 * For production, verification should be done on the backend.
 */
export function parseIAPToken(token: string): any {
  try {
    // JWT format: header.payload.signature
    const parts = token.split('.');
    if (parts.length !== 3) {
      throw new Error('Invalid JWT format');
    }

    // Decode the payload (base64url)
    const payload = parts[1];
    const decoded = Buffer.from(payload, 'base64').toString('utf8');
    return JSON.parse(decoded);
  } catch (error) {
    console.error('Failed to parse IAP token:', error);
    return null;
  }
}

/**
 * Extract user information from IAP headers
 */
export function extractIAPUser(headers: Headers | Record<string, string>): IAPUser | null {
  // Helper to get header value (works with both Headers object and plain object)
  const getHeader = (name: string): string | null => {
    if (headers instanceof Headers) {
      return headers.get(name);
    }
    return headers[name] || headers[name.toLowerCase()] || null;
  };

  // Check for IAP JWT assertion (Cloud Run IAP)
  const iapJWT = getHeader('x-goog-iap-jwt-assertion');
  if (iapJWT) {
    const payload = parseIAPToken(iapJWT);
    if (payload) {
      return {
        email: payload.email || 'unknown@iap',
        userId: payload.sub || 'unknown_iap_user',
        name: payload.name,
        picture: payload.picture,
        authMethod: 'iap',
        raw: payload,
      };
    }
  }

  // Check for authenticated user email header (alternative IAP format)
  const userEmail = getHeader('x-goog-authenticated-user-email');
  if (userEmail) {
    // Format: accounts.google.com:user@example.com
    const email = userEmail.split(':')[1] || userEmail;
    return {
      email,
      userId: email.split('@')[0] || 'unknown',
      authMethod: 'iap',
    };
  }

  // Development fallback
  return {
    email: 'dev@localhost',
    userId: 'dev_user',
    name: 'Development User',
    authMethod: 'development',
  };
}

/**
 * Format user display name
 */
export function formatUserName(user: IAPUser): string {
  if (user.name) return user.name;
  if (user.email) return user.email.split('@')[0];
  return user.userId;
}

