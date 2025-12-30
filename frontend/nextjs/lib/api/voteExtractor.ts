import { voteExtractorClient } from './client';

/**
 * Vote Extractor API types
 */

export interface VoteExtractionRequest {
  files: File[];
  llm_config?: {
    model?: string;
    temperature?: number;
    max_tokens?: number;
  };
}

export interface VoteResult {
  number: number;
  candidate_name?: string;
  party_name?: string;
  vote_count: number;
  vote_count_text?: string;
}

export interface BallotStatistics {
  ballots_allocated?: number;
  ballots_remaining?: number;
  ballots_used: number;
  good_ballots: number;
  bad_ballots: number;
  no_vote_ballots: number;
}

export interface FormInfo {
  date?: string;
  province?: string;
  district?: string;
  sub_district?: string;
  polling_station_number?: string;
  constituency_number?: string;
  form_type?: string;
}

export interface ExtractionData {
  form_info?: FormInfo;
  ballot_statistics?: BallotStatistics;
  vote_results?: VoteResult[];
}

export interface VoteExtractionResponse {
  success: boolean;
  pages_processed: number;
  reports_extracted: number;
  data: ExtractionData[];
  error?: string;
}

export interface ModelInfo {
  name: string;
  display_name: string;
  description: string;
}

/**
 * Vote Extractor API Client
 */
export const voteExtractorApi = {
  /**
   * Extract votes from uploaded files
   */
  extractVotes: async (
    files: File[],
    llmConfig?: {
      provider?: string;
      model?: string;
      temperature?: number;
      max_tokens?: number;
      top_p?: number;
      top_k?: number;
    }
  ): Promise<VoteExtractionResponse> => {
    const formData = new FormData();

    files.forEach((file) => {
      formData.append('files', file);
    });

    if (llmConfig) {
      formData.append('llm_config_json', JSON.stringify(llmConfig));
    }

    const response = await voteExtractorClient.post<VoteExtractionResponse>(
      '/api/v1/vote-extraction/extract',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 120000, // 2 minutes for processing images
      }
    );

    return response.data;
  },

  /**
   * List available LLM models
   */
  listModels: async (): Promise<ModelInfo[]> => {
    const response = await voteExtractorClient.get<ModelInfo[]>('/api/v1/vote-extraction/models');

    return response.data;
  },

  /**
   * Health check
   */
  healthCheck: async (): Promise<{ status: string }> => {
    const response = await voteExtractorClient.get('/health');
    return response.data;
  },
};
