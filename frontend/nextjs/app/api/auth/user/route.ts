/**
 * API Route: Get Current User from IAP Headers
 * 
 * Checks for Google Cloud IAP headers and returns user information.
 * This must be server-side because headers are only available in API routes.
 */

import { NextRequest, NextResponse } from 'next/server';
import { extractIAPUser } from '@/lib/utils/iapAuth';

export async function GET(request: NextRequest) {
  try {
    // Extract user from IAP headers
    const user = extractIAPUser(request.headers);

    // Log headers for debugging (remove in production)
    const headersList: Record<string, string> = {};
    request.headers.forEach((value, key) => {
      if (key.toLowerCase().includes('goog') || 
          key.toLowerCase().includes('auth') ||
          key.toLowerCase().includes('user')) {
        headersList[key] = value;
      }
    });

    console.log('📊 IAP Headers:', headersList);
    console.log('👤 Extracted User:', user);

    return NextResponse.json({
      user,
      headers: headersList,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('❌ Error extracting user:', error);
    return NextResponse.json(
      { 
        error: 'Failed to extract user information',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

