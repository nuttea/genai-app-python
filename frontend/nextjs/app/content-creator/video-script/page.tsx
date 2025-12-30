'use client';

import { useState } from 'react';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { FileUpload } from '@/components/shared/FileUpload';
import { contentCreatorApi, VideoScriptRequest, VideoScriptResponse } from '@/lib/api/contentCreator';
import { useApi } from '@/hooks/useApi';
import { useToast } from '@/hooks/useToast';
import { Download, Copy, Sparkles, Play, Clock } from 'lucide-react';
import { copyToClipboard, downloadBlob } from '@/lib/utils';

export default function VideoScriptPage() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [platform, setPlatform] = useState('youtube_shorts');
  const [tone, setTone] = useState('engaging');
  const [files, setFiles] = useState<File[]>([]);
  const [uploadedFileIds, setUploadedFileIds] = useState<string[]>([]);
  const [generatedScript, setGeneratedScript] = useState<VideoScriptResponse | null>(null);

  const { loading, error, execute } = useApi<VideoScriptResponse, VideoScriptRequest>();
  const toast = useToast();

  const handleFilesSelected = async (selectedFiles: File[]) => {
    setFiles(selectedFiles);

    if (selectedFiles.length > 0) {
      try {
        const uploadPromises = selectedFiles.map((file) => contentCreatorApi.uploadFile(file));
        const results = await Promise.all(uploadPromises);
        const fileIds = results.map((r) => r.file_id);
        setUploadedFileIds(fileIds);
        toast.success(`Uploaded ${fileIds.length} file(s) successfully`);
      } catch (err) {
        toast.error('Failed to upload files');
        console.error('Upload error:', err);
      }
    }
  };

  const handleGenerate = async () => {
    if (!title.trim()) {
      toast.error('Please enter a title');
      return;
    }

    if (!description.trim()) {
      toast.error('Please enter a description');
      return;
    }

    const request: VideoScriptRequest = {
      title: title.trim(),
      description: description.trim(),
      platform,
      tone,
      file_ids: uploadedFileIds.length > 0 ? uploadedFileIds : undefined,
      generation_config: {
        temperature: 0.8,
        max_tokens: 4096,
        model: 'gemini-2.5-flash',
      },
    };

    const result = await execute(contentCreatorApi.generateVideoScript, request);

    if (result) {
      setGeneratedScript(result);
      toast.success('Video script generated successfully!');
    } else {
      toast.error(error || 'Failed to generate video script');
    }
  };

  const handleCopy = async () => {
    if (generatedScript) {
      const scriptText = `# ${generatedScript.title}\n\n${generatedScript.script}`;
      const success = await copyToClipboard(scriptText);
      if (success) {
        toast.success('Copied to clipboard!');
      } else {
        toast.error('Failed to copy');
      }
    }
  };

  const handleDownload = () => {
    if (generatedScript) {
      const content = `# ${generatedScript.title}\n\n${generatedScript.script}`;
      const blob = new Blob([content], { type: 'text/plain' });
      const filename = `${generatedScript.title.replace(/\s+/g, '-').toLowerCase()}-script.txt`;
      downloadBlob(blob, filename);
      toast.success('Downloaded successfully!');
    }
  };

  const getPlatformEmoji = (platform: string) => {
    const emojis: Record<string, string> = {
      youtube_shorts: '📹',
      tiktok: '🎵',
      reels: '📱',
    };
    return emojis[platform] || '🎬';
  };

  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header title="Generate Video Script" />
        <main className="flex-1 overflow-y-auto p-8">
          <div className="max-w-7xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Input Form */}
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Video Script Details</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Title */}
                    <div className="space-y-2">
                      <Label htmlFor="title">Video Title *</Label>
                      <Input
                        id="title"
                        placeholder="e.g., Datadog APM in 60 Seconds"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                      />
                    </div>

                    {/* Description */}
                    <div className="space-y-2">
                      <Label htmlFor="description">Video Description *</Label>
                      <Textarea
                        id="description"
                        placeholder="Describe the video content, key points to cover..."
                        rows={5}
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                      />
                      <p className="text-xs text-muted-foreground">
                        What should the video demonstrate or explain?
                      </p>
                    </div>

                    {/* Platform */}
                    <div className="space-y-2">
                      <Label htmlFor="platform">Target Platform</Label>
                      <select
                        id="platform"
                        value={platform}
                        onChange={(e) => setPlatform(e.target.value)}
                        className="w-full h-10 px-3 py-2 text-sm rounded-md border border-input bg-background"
                      >
                        <option value="youtube_shorts">📹 YouTube Shorts (60s)</option>
                        <option value="tiktok">🎵 TikTok (60s)</option>
                        <option value="reels">📱 Instagram Reels (60s)</option>
                      </select>
                    </div>

                    {/* Tone */}
                    <div className="space-y-2">
                      <Label htmlFor="tone">Script Tone</Label>
                      <select
                        id="tone"
                        value={tone}
                        onChange={(e) => setTone(e.target.value)}
                        className="w-full h-10 px-3 py-2 text-sm rounded-md border border-input bg-background"
                      >
                        <option value="engaging">Engaging & Energetic</option>
                        <option value="professional">Professional</option>
                        <option value="casual">Casual & Friendly</option>
                        <option value="educational">Educational</option>
                      </select>
                    </div>

                    {/* Duration Info */}
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                      <div className="flex items-start space-x-2">
                        <Clock className="w-4 h-4 text-blue-600 mt-0.5" />
                        <div className="text-sm text-blue-800">
                          <p className="font-medium mb-1">60-Second Format</p>
                          <p className="text-xs">
                            Scripts are optimized for short-form video (hook, main content, CTA)
                          </p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* File Upload */}
                <Card>
                  <CardHeader>
                    <CardTitle>Reference Materials (Optional)</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <FileUpload onFilesSelected={handleFilesSelected} maxFiles={3} />
                    <p className="text-xs text-muted-foreground mt-2">
                      Upload demo videos, screenshots, or product images for AI to reference
                    </p>
                  </CardContent>
                </Card>

                {/* Generate Button */}
                <Button
                  onClick={handleGenerate}
                  disabled={loading}
                  loading={loading}
                  className="w-full"
                  size="lg"
                >
                  <Sparkles className="w-4 h-4 mr-2" />
                  {loading ? 'Generating...' : 'Generate Video Script'}
                </Button>

                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-sm text-red-800">{error}</p>
                  </div>
                )}
              </div>

              {/* Preview/Output */}
              <div className="space-y-6">
                {generatedScript ? (
                  <>
                    <Card>
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <CardTitle className="flex items-center">
                            <Play className="w-5 h-5 mr-2 text-purple-600" />
                            Generated Script
                          </CardTitle>
                          <div className="flex space-x-2">
                            <Button variant="outline" size="sm" onClick={handleCopy}>
                              <Copy className="w-4 h-4 mr-2" />
                              Copy
                            </Button>
                            <Button variant="outline" size="sm" onClick={handleDownload}>
                              <Download className="w-4 h-4 mr-2" />
                              Download
                            </Button>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          {/* Metadata */}
                          <div className="flex flex-wrap gap-4 text-sm">
                            <span className="flex items-center text-muted-foreground">
                              {getPlatformEmoji(generatedScript.platform)}
                              <span className="ml-1 capitalize">
                                {generatedScript.platform.replace('_', ' ')}
                              </span>
                            </span>
                            <span className="flex items-center text-muted-foreground">
                              <Clock className="w-4 h-4 mr-1" />
                              {generatedScript.estimated_duration}
                            </span>
                          </div>

                          {/* Hashtags */}
                          {generatedScript.hashtags && generatedScript.hashtags.length > 0 && (
                            <div className="flex flex-wrap gap-2">
                              {generatedScript.hashtags.map((tag, index) => (
                                <span
                                  key={index}
                                  className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full"
                                >
                                  #{tag}
                                </span>
                              ))}
                            </div>
                          )}

                          {/* Script Content */}
                          <div className="border border-border rounded-lg p-6 bg-card max-h-[500px] overflow-y-auto">
                            <div className="space-y-4">
                              <h3 className="text-lg font-bold text-foreground">
                                {generatedScript.title}
                              </h3>
                              <div className="prose prose-sm max-w-none">
                                <pre className="whitespace-pre-wrap font-sans text-sm text-foreground">
                                  {generatedScript.script}
                                </pre>
                              </div>
                            </div>
                          </div>

                          {/* Tips */}
                          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                            <p className="text-sm font-medium text-purple-900 mb-2">
                              📝 Production Tips
                            </p>
                            <ul className="text-xs text-purple-800 space-y-1">
                              <li>• Read the script naturally, adjust pacing as needed</li>
                              <li>• Add visual overlays at key points</li>
                              <li>• Include captions for better engagement</li>
                              <li>• Use trending sounds (TikTok/Reels)</li>
                            </ul>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </>
                ) : (
                  <Card>
                    <CardContent className="py-12">
                      <div className="text-center text-muted-foreground">
                        <Play className="w-12 h-12 mx-auto mb-4 text-purple-400" />
                        <p className="text-lg font-medium mb-2">No script generated yet</p>
                        <p className="text-sm">
                          Fill in the details and click "Generate Video Script" to create
                          AI-powered short-form video content
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

