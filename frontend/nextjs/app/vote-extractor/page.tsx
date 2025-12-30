'use client';

import { useState } from 'react';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { FileUpload } from '@/components/shared/FileUpload';
import { voteExtractorApi } from '@/lib/api/voteExtractor';
import { useApi } from '@/hooks/useApi';
import { useToast } from '@/hooks/useToast';
import { 
  FileText, 
  Download, 
  AlertCircle, 
  CheckCircle, 
  XCircle,
  ChevronDown,
  ChevronUp,
  Info
} from 'lucide-react';
import Image from 'next/image';

// Types for extraction response
interface VoteResult {
  number: number;
  candidate_name?: string;
  party_name?: string;
  vote_count: number;
  vote_count_text?: string;
}

interface BallotStatistics {
  ballots_allocated?: number;
  ballots_remaining?: number;
  ballots_used: number;
  good_ballots: number;
  bad_ballots: number;
  no_vote_ballots: number;
}

interface FormInfo {
  date?: string;
  province?: string;
  district?: string;
  sub_district?: string;
  polling_station_number?: string;
  constituency_number?: string;
  form_type?: string;
}

interface ExtractionData {
  form_info?: FormInfo;
  ballot_statistics?: BallotStatistics;
  vote_results?: VoteResult[];
}

interface ExtractionResult {
  success: boolean;
  pages_processed: number;
  reports_extracted: number;
  data: ExtractionData[];
  error?: string;
}

export default function VoteExtractorPage() {
  const [files, setFiles] = useState<File[]>([]);
  const [previewUrls, setPreviewUrls] = useState<string[]>([]);
  const [extractionResult, setExtractionResult] = useState<ExtractionResult | null>(null);
  const [selectedReportIdx, setSelectedReportIdx] = useState(0);
  const [activeTab, setActiveTab] = useState<'summary' | 'votes' | 'ballots' | 'json'>('summary');
  const [showInstructions, setShowInstructions] = useState(false);
  const [showLLMConfig, setShowLLMConfig] = useState(false);
  
  const { loading, execute } = useApi<ExtractionResult, FormData>();
  const toast = useToast();

  const handleFilesSelected = (selectedFiles: File[]) => {
    setFiles(selectedFiles);
    setExtractionResult(null); // Clear previous results
    
    // Create preview URLs
    const urls = selectedFiles.map(file => URL.createObjectURL(file));
    setPreviewUrls(urls);
    
    toast.success(`${selectedFiles.length} file(s) selected`);
  };

  const handleExtract = async () => {
    if (files.length === 0) {
      toast.error('Please select files first');
      return;
    }

    try {
      const result = await execute(voteExtractorApi.extractVotes, files);
      setExtractionResult(result);
      setSelectedReportIdx(0);
      setActiveTab('summary');
      
      if (result && result.success) {
        toast.success(`Successfully extracted ${result.reports_extracted} report(s)`);
      } else if (result) {
        toast.error('Extraction completed with errors');
      }
    } catch (error) {
      console.error('Extraction error:', error);
      toast.error('Failed to extract data from images');
    }
  };

  const handleDownloadCSV = (report: ExtractionData) => {
    if (!report.vote_results || report.vote_results.length === 0) {
      toast.error('No vote results to download');
      return;
    }

    // Convert to CSV
    const headers = ['Number', 'Candidate/Party Name', 'Vote Count', 'Vote Count (Text)'];
    const rows = report.vote_results.map(r => [
      r.number,
      r.candidate_name || r.party_name || 'N/A',
      r.vote_count,
      r.vote_count_text || ''
    ]);

    const csv = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `vote_results_${report.form_info?.form_type || 'data'}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    
    toast.success('CSV downloaded');
  };

  const handleDownloadJSON = (data: any, filename: string) => {
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
    
    toast.success('JSON downloaded');
  };

  const currentReport = extractionResult?.data?.[selectedReportIdx];

  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header title="Vote Extractor" />
        
        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-7xl mx-auto space-y-6">
            {/* Page Header */}
            <div>
              <h1 className="text-3xl font-bold text-foreground mb-2">
                🗳️ Thai Election Form Vote Extractor
              </h1>
              <p className="text-muted-foreground">
                Extract structured data from Thai election documents (Form S.S. 5/18).
                Upload multiple pages of the same report to get consolidated results.
              </p>
            </div>

            {/* Instructions Collapsible */}
            <Card>
              <CardHeader 
                className="cursor-pointer hover:bg-accent/50 transition-colors"
                onClick={() => setShowInstructions(!showInstructions)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Info className="w-5 h-5 text-blue-500" />
                    <CardTitle className="text-lg">How to use</CardTitle>
                  </div>
                  {showInstructions ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                </div>
              </CardHeader>
              {showInstructions && (
                <CardContent className="prose prose-sm max-w-none">
                  <h3>Instructions:</h3>
                  <ol>
                    <li><strong>Prepare your images</strong>: Scan or photograph election form pages (JPG or PNG format)</li>
                    <li><strong>Upload files</strong>: Drag & drop or click to select all pages of the same report</li>
                    <li><strong>Extract data</strong>: Click "Extract Vote Data" button</li>
                    <li><strong>Review results</strong>: View extracted data in organized tabs</li>
                  </ol>
                  
                  <h3>Supported Formats:</h3>
                  <ul>
                    <li>Image types: JPG, JPEG, PNG</li>
                    <li>Multiple pages: Yes (will be consolidated into single report)</li>
                    <li>Form types: Constituency (candidates) and PartyList (parties)</li>
                  </ul>
                  
                  <h3>What gets extracted:</h3>
                  <ul>
                    <li><strong>Form Information</strong>: Date, Province, District, Polling Station, etc.</li>
                    <li><strong>Ballot Statistics</strong>: Total ballots used, valid, void, and no-vote counts</li>
                    <li><strong>Vote Results</strong>: Complete table of candidates/parties with vote counts</li>
                  </ul>
                </CardContent>
              )}
            </Card>

            {/* File Upload Section */}
            <Card>
              <CardHeader>
                <CardTitle>📤 Upload Election Form Images</CardTitle>
                <p className="text-sm text-muted-foreground">
                  ⚠️ Limits: 10MB per file, 30MB total upload size
                </p>
              </CardHeader>
              <CardContent>
                <FileUpload
                  onFilesSelected={handleFilesSelected}
                  maxFiles={10}
                />
                
                {/* Preview uploaded images */}
                {previewUrls.length > 0 && (
                  <div className="mt-6">
                    <h3 className="text-sm font-semibold mb-3">
                      🖼️ Preview uploaded images ({files.length} file{files.length !== 1 ? 's' : ''})
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {previewUrls.map((url, idx) => (
                        <div key={idx} className="border rounded-lg overflow-hidden">
                          <Image
                            src={url}
                            alt={`Page ${idx + 1}`}
                            width={200}
                            height={300}
                            className="w-full h-48 object-cover"
                          />
                          <div className="p-2 bg-accent text-xs text-center">
                            Page {idx + 1}: {files[idx].name}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Extract Button */}
            <div className="flex justify-center">
              <Button
                onClick={handleExtract}
                disabled={files.length === 0 || loading}
                size="lg"
                className="px-12"
              >
                {loading ? (
                  <>
                    <span className="animate-spin mr-2">⏳</span>
                    Processing...
                  </>
                ) : (
                  <>
                    🚀 Extract Vote Data
                  </>
                )}
              </Button>
            </div>

            {/* Extraction Results */}
            {extractionResult && (
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>📊 Extraction Results</CardTitle>
                    {extractionResult.success ? (
                      <div className="flex items-center space-x-2 text-green-600">
                        <CheckCircle className="w-5 h-5" />
                        <span className="text-sm font-medium">
                          {extractionResult.reports_extracted} report(s) from {extractionResult.pages_processed} page(s)
                        </span>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2 text-red-600">
                        <XCircle className="w-5 h-5" />
                        <span className="text-sm font-medium">Extraction failed</span>
                      </div>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  {extractionResult.error && (
                    <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg flex items-start space-x-2">
                      <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
                      <p className="text-sm text-yellow-800">{extractionResult.error}</p>
                    </div>
                  )}

                  {extractionResult.data && extractionResult.data.length > 0 ? (
                    <>
                      {/* Report Selector */}
                      {extractionResult.data.length > 1 && (
                        <div className="mb-6">
                          <label className="block text-sm font-medium mb-2">
                            Select Report to View Details
                          </label>
                          <select
                            value={selectedReportIdx}
                            onChange={(e) => setSelectedReportIdx(Number(e.target.value))}
                            className="w-full p-2 border rounded-lg"
                          >
                            {extractionResult.data.map((report, idx) => (
                              <option key={idx} value={idx}>
                                Report #{idx + 1} - {report.form_info?.district || 'Unknown'} Station {report.form_info?.polling_station_number || 'N/A'}
                              </option>
                            ))}
                          </select>
                        </div>
                      )}

                      {/* Tabs */}
                      {currentReport && (
                        <>
                          <div className="border-b mb-4">
                            <div className="flex space-x-4">
                              {[
                                { id: 'summary', label: '📋 Summary' },
                                { id: 'votes', label: '📊 Vote Results' },
                                { id: 'ballots', label: '📦 Ballot Statistics' },
                                { id: 'json', label: '🔍 Raw JSON' },
                              ].map((tab) => (
                                <button
                                  key={tab.id}
                                  onClick={() => setActiveTab(tab.id as any)}
                                  className={`px-4 py-2 font-medium border-b-2 transition-colors ${
                                    activeTab === tab.id
                                      ? 'border-purple-600 text-purple-600'
                                      : 'border-transparent text-muted-foreground hover:text-foreground'
                                  }`}
                                >
                                  {tab.label}
                                </button>
                              ))}
                            </div>
                          </div>

                          {/* Tab Content */}
                          <div className="mt-6">
                            {activeTab === 'summary' && <SummaryTab report={currentReport} />}
                            {activeTab === 'votes' && <VoteResultsTab report={currentReport} onDownloadCSV={handleDownloadCSV} />}
                            {activeTab === 'ballots' && <BallotStatisticsTab report={currentReport} />}
                            {activeTab === 'json' && <RawJSONTab report={currentReport} allReports={extractionResult.data} reportIdx={selectedReportIdx} onDownload={handleDownloadJSON} />}
                          </div>
                        </>
                      )}
                    </>
                  ) : (
                    <p className="text-muted-foreground text-center py-8">No data extracted</p>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

// Tab Components
function SummaryTab({ report }: { report: ExtractionData }) {
  const form = report.form_info || {};
  
  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">Form Information</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard label="Province" value={form.province || 'N/A'} />
        <MetricCard label="District" value={form.district || 'N/A'} />
        {form.sub_district && <MetricCard label="Sub-district" value={form.sub_district} />}
        <MetricCard label="Polling Station" value={form.polling_station_number || 'N/A'} />
        <MetricCard label="Constituency" value={form.constituency_number || 'N/A'} />
        <MetricCard label="Form Type" value={form.form_type || 'N/A'} />
        <MetricCard label="Date" value={form.date || 'N/A'} />
      </div>
    </div>
  );
}

function VoteResultsTab({ report, onDownloadCSV }: { report: ExtractionData; onDownloadCSV: (report: ExtractionData) => void }) {
  const results = report.vote_results || [];
  const formType = report.form_info?.form_type || '';
  
  if (results.length === 0) {
    return <p className="text-muted-foreground text-center py-8">No vote results found</p>;
  }

  const totalVotes = results.reduce((sum, r) => sum + r.vote_count, 0);

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Vote Results Table ({formType})</h3>
        <Button onClick={() => onDownloadCSV(report)} variant="outline" size="sm">
          <Download className="w-4 h-4 mr-2" />
          Download CSV
        </Button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-accent">
              <th className="border p-2 text-left">Number</th>
              {formType === 'PartyList' ? (
                <th className="border p-2 text-left">Party Name</th>
              ) : (
                <>
                  <th className="border p-2 text-left">Candidate Name</th>
                  <th className="border p-2 text-left">Party Name</th>
                </>
              )}
              <th className="border p-2 text-right">Vote Count</th>
              <th className="border p-2 text-left">Vote Count (Text)</th>
            </tr>
          </thead>
          <tbody>
            {results.map((result, idx) => (
              <tr key={idx} className="hover:bg-accent/50">
                <td className="border p-2">{result.number}</td>
                {formType === 'PartyList' ? (
                  <td className="border p-2">{result.party_name || 'N/A'}</td>
                ) : (
                  <>
                    <td className="border p-2">{result.candidate_name || 'N/A'}</td>
                    <td className="border p-2">{result.party_name || 'N/A'}</td>
                  </>
                )}
                <td className="border p-2 text-right font-mono">{result.vote_count.toLocaleString()}</td>
                <td className="border p-2">{result.vote_count_text || ''}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="grid grid-cols-2 gap-4 mt-6">
        <MetricCard label="Total Votes Counted" value={totalVotes.toLocaleString()} />
        <MetricCard label="Total Candidates/Parties" value={results.length.toString()} />
      </div>
    </div>
  );
}

function BallotStatisticsTab({ report }: { report: ExtractionData }) {
  const stats = report.ballot_statistics;
  
  if (!stats) {
    return <p className="text-muted-foreground text-center py-8">No ballot statistics found</p>;
  }

  const totalAccounted = stats.good_ballots + stats.bad_ballots + stats.no_vote_ballots;
  const ballotsMatch = totalAccounted === stats.ballots_used;

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">Ballot Statistics</h3>
      
      {(stats.ballots_allocated || stats.ballots_remaining) && (
        <>
          <h4 className="text-md font-medium mb-3">Ballot Allocation</h4>
          <div className="grid grid-cols-2 gap-4 mb-6">
            {stats.ballots_allocated && (
              <MetricCard label="Ballots Allocated" value={stats.ballots_allocated.toLocaleString()} />
            )}
            {stats.ballots_remaining && (
              <MetricCard label="Ballots Remaining" value={stats.ballots_remaining.toLocaleString()} />
            )}
          </div>
          <h4 className="text-md font-medium mb-3">Ballot Usage</h4>
        </>
      )}
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <MetricCard label="Ballots Used" value={stats.ballots_used.toLocaleString()} />
        <MetricCard label="Valid Ballots" value={stats.good_ballots.toLocaleString()} />
        <MetricCard label="Void Ballots" value={stats.bad_ballots.toLocaleString()} />
        <MetricCard label="No Vote" value={stats.no_vote_ballots.toLocaleString()} />
      </div>

      {ballotsMatch ? (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg flex items-start space-x-2">
          <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
          <p className="text-sm text-green-800">
            ✅ Ballot counts match (Valid + Void + No Vote = Total Used)
          </p>
        </div>
      ) : (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-2">
          <XCircle className="w-5 h-5 text-red-600 mt-0.5" />
          <p className="text-sm text-red-800">
            ❌ Ballot count mismatch: Total Used ({stats.ballots_used}) ≠ Sum ({totalAccounted})
          </p>
        </div>
      )}
    </div>
  );
}

function RawJSONTab({ 
  report, 
  allReports, 
  reportIdx, 
  onDownload 
}: { 
  report: ExtractionData; 
  allReports: ExtractionData[]; 
  reportIdx: number;
  onDownload: (data: any, filename: string) => void;
}) {
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Complete Extracted Data (JSON)</h3>
        <div className="flex space-x-2">
          <Button 
            onClick={() => onDownload(report, `vote_data_report_${reportIdx + 1}.json`)}
            variant="outline" 
            size="sm"
          >
            <Download className="w-4 h-4 mr-2" />
            This Report
          </Button>
          {allReports.length > 1 && (
            <Button 
              onClick={() => onDownload(allReports, 'vote_data_all_reports.json')}
              variant="outline" 
              size="sm"
            >
              <Download className="w-4 h-4 mr-2" />
              All Reports
            </Button>
          )}
        </div>
      </div>

      <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
        {JSON.stringify(report, null, 2)}
      </pre>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <Card>
      <CardContent className="p-4">
        <p className="text-sm text-muted-foreground mb-1">{label}</p>
        <p className="text-lg font-semibold">{value}</p>
      </CardContent>
    </Card>
  );
}

