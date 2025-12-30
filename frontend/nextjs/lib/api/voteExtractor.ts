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

export interface CandidateVote {
  candidate_number: number;
  candidate_name: string;
  votes: number;
  vote_type: string;
}

export interface VoteExtractionResponse {
  election_unit: string;
  total_voters: number;
  votes_cast: number;
  valid_votes: number;
  invalid_votes: number;
  candidates: CandidateVote[];
  extracted_at: string;
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
      model?: string;
      temperature?: number;
      max_tokens?: number;
    }
  ): Promise<VoteExtractionResponse> => {
    const formData = new FormData();

    files.forEach((file) => {
      formData.append('files', file);
    });

    if (llmConfig) {
      formData.append('llm_config', JSON.stringify(llmConfig));
    }

    const response = await voteExtractorClient.post<VoteExtractionResponse>(
      '/api/v1/vote-extraction/extract',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return response.data;
  },

  /**
   * List available LLM models
   */
  listModels: async (): Promise<ModelInfo[]> => {
    const response = await voteExtractorClient.get<ModelInfo[]>(
      '/api/v1/vote-extraction/models'
    );

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

