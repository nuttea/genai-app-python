'use client';

import { useEffect } from 'react';
import { datadogRum } from '@datadog/browser-rum';
import { DATADOG_CONFIG } from '@/lib/constants/config';

export function DatadogInit() {
  useEffect(() => {
    // Only initialize if credentials are provided
    if (!DATADOG_CONFIG.applicationId || !DATADOG_CONFIG.clientToken) {
      console.warn('Datadog RUM not initialized: missing credentials');
      return;
    }

    datadogRum.init({
      applicationId: DATADOG_CONFIG.applicationId,
      clientToken: DATADOG_CONFIG.clientToken,
      site: DATADOG_CONFIG.site,
      service: DATADOG_CONFIG.service,
      env: DATADOG_CONFIG.env,
      version: DATADOG_CONFIG.version,
      sessionSampleRate: DATADOG_CONFIG.sessionSampleRate,
      sessionReplaySampleRate: DATADOG_CONFIG.sessionReplayEnabled
        ? DATADOG_CONFIG.sessionSampleRate
        : 0,
      trackUserInteractions: true,
      trackResources: true,
      trackLongTasks: true,
      defaultPrivacyLevel: 'mask-user-input',
    });

    // Start session replay if enabled
    if (DATADOG_CONFIG.sessionReplayEnabled) {
      datadogRum.startSessionReplayRecording();
    }

    console.log('Datadog RUM initialized:', {
      service: DATADOG_CONFIG.service,
      env: DATADOG_CONFIG.env,
      version: DATADOG_CONFIG.version,
    });
  }, []);

  return null;
}
