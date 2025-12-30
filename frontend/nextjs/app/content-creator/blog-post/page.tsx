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
import { MarkdownPreview } from '@/components/shared/MarkdownPreview';
import { contentCreatorApi, BlogPostRequest, BlogPostResponse } from '@/lib/api/contentCreator';
import { useApi } from '@/hooks/useApi';
import { useToast } from '@/hooks/useToast';
import { Download, Copy, Sparkles } from 'lucide-react';
import { copyToClipboard, downloadBlob } from '@/lib/utils';

export default function BlogPostPage() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [style, setStyle] = useState('professional');
  const [audience, setAudience] = useState('developers');
  const [files, setFiles] = useState<File[]>([]);
  const [uploadedFiles, setUploadedFiles] = useState<
    Array<{ filename: string; extractedText?: string; gcsUri?: string }>
  >([]);
  const [generatedPost, setGeneratedPost] = useState<BlogPostResponse | null>(null);

  const { loading, error, execute } = useApi<BlogPostResponse, BlogPostRequest>();
  const toast = useToast();

  const handleFilesSelected = async (selectedFiles: File[]) => {
    setFiles(selectedFiles);

    // Upload files
    if (selectedFiles.length > 0) {
      try {
        const uploadPromises = selectedFiles.map((file) => contentCreatorApi.uploadFile(file));
        const results = await Promise.all(uploadPromises);

        // Extract file info from responses
        const fileInfos = results.map((r) => ({
          filename: r.file.filename,
          extractedText: r.file.extracted_text || undefined,
          gcsUri: r.file.gcs_uri || undefined,
        }));

        setUploadedFiles(fileInfos);
        toast.success(`Uploaded ${fileInfos.length} file(s) successfully`);

        // Log extracted text for debugging
        fileInfos.forEach((info) => {
          if (info.extractedText) {
            console.log(
              `Extracted text from ${info.filename}:`,
              info.extractedText.substring(0, 100)
            );
          }
        });
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

    // Combine description with extracted text from uploaded files
    let fullDescription = description.trim();
    if (uploadedFiles.length > 0) {
      const extractedTexts = uploadedFiles
        .filter((f) => f.extractedText)
        .map((f) => `\n\n---\nFrom ${f.filename}:\n${f.extractedText}`)
        .join('\n');

      if (extractedTexts) {
        fullDescription += extractedTexts;
      }
    }

    const request: BlogPostRequest = {
      title: title.trim(),
      description: fullDescription,
      style,
      target_audience: audience,
      // For now, we pass artifact URIs as file_ids (will be handled by backend)
      file_ids: uploadedFiles.filter((f) => f.gcsUri).map((f) => f.gcsUri!) || undefined,
      generation_config: {
        temperature: 0.7,
        max_tokens: 8192,
        model: 'gemini-2.5-flash',
      },
    };

    const result = await execute(contentCreatorApi.generateBlogPost, request);

    if (result) {
      setGeneratedPost(result);
      toast.success('Blog post generated successfully!');
    } else {
      toast.error(error || 'Failed to generate blog post');
    }
  };

  const handleCopyMarkdown = async () => {
    if (generatedPost) {
      const success = await copyToClipboard(generatedPost.content);
      if (success) {
        toast.success('Copied to clipboard!');
      } else {
        toast.error('Failed to copy');
      }
    }
  };

  const handleDownloadMarkdown = () => {
    if (generatedPost) {
      const blob = new Blob([generatedPost.content], { type: 'text/markdown' });
      const filename = `${generatedPost.title.replace(/\s+/g, '-').toLowerCase()}.md`;
      downloadBlob(blob, filename);
      toast.success('Downloaded successfully!');
    }
  };

  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header title="Generate Blog Post" />
        <main className="flex-1 overflow-y-auto p-8">
          <div className="max-w-7xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Input Form */}
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Blog Post Details</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Title */}
                    <div className="space-y-2">
                      <Label htmlFor="title">Title *</Label>
                      <Input
                        id="title"
                        placeholder="e.g., Getting Started with Datadog APM"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                      />
                    </div>

                    {/* Description */}
                    <div className="space-y-2">
                      <Label htmlFor="description">Description *</Label>
                      <Textarea
                        id="description"
                        placeholder="Describe what you want to write about..."
                        rows={6}
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                      />
                      <p className="text-xs text-muted-foreground">
                        Provide context, key points, or specific topics to cover
                      </p>
                    </div>

                    {/* Style */}
                    <div className="space-y-2">
                      <Label htmlFor="style">Writing Style</Label>
                      <select
                        id="style"
                        value={style}
                        onChange={(e) => setStyle(e.target.value)}
                        className="w-full h-10 px-3 py-2 text-sm rounded-md border border-input bg-background"
                      >
                        <option value="professional">Professional</option>
                        <option value="casual">Casual</option>
                        <option value="technical">Technical</option>
                        <option value="conversational">Conversational</option>
                      </select>
                    </div>

                    {/* Target Audience */}
                    <div className="space-y-2">
                      <Label htmlFor="audience">Target Audience</Label>
                      <select
                        id="audience"
                        value={audience}
                        onChange={(e) => setAudience(e.target.value)}
                        className="w-full h-10 px-3 py-2 text-sm rounded-md border border-input bg-background"
                      >
                        <option value="developers">Developers</option>
                        <option value="devops">DevOps Engineers</option>
                        <option value="managers">Engineering Managers</option>
                        <option value="general">General Tech Audience</option>
                      </select>
                    </div>
                  </CardContent>
                </Card>

                {/* File Upload */}
                <Card>
                  <CardHeader>
                    <CardTitle>Reference Materials (Optional)</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <FileUpload onFilesSelected={handleFilesSelected} maxFiles={5} />
                    <p className="text-xs text-muted-foreground mt-2">
                      Upload screenshots, videos, or documents for AI to analyze and incorporate
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
                  {loading ? 'Generating...' : 'Generate Blog Post'}
                </Button>

                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-sm text-red-800">{error}</p>
                  </div>
                )}
              </div>

              {/* Preview/Output */}
              <div className="space-y-6">
                {generatedPost ? (
                  <>
                    <Card>
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <CardTitle>Generated Blog Post</CardTitle>
                          <div className="flex space-x-2">
                            <Button variant="outline" size="sm" onClick={handleCopyMarkdown}>
                              <Copy className="w-4 h-4 mr-2" />
                              Copy
                            </Button>
                            <Button variant="outline" size="sm" onClick={handleDownloadMarkdown}>
                              <Download className="w-4 h-4 mr-2" />
                              Download
                            </Button>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          {/* Metadata */}
                          <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
                            <span>📖 {generatedPost.estimated_read_time} min read</span>
                            {generatedPost.tags && generatedPost.tags.length > 0 && (
                              <span>🏷️ {generatedPost.tags.join(', ')}</span>
                            )}
                          </div>

                          {/* Summary */}
                          {generatedPost.summary && (
                            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                              <p className="text-sm font-medium text-purple-900 mb-1">Summary</p>
                              <p className="text-sm text-purple-800">{generatedPost.summary}</p>
                            </div>
                          )}

                          {/* Content Preview */}
                          <div className="border border-border rounded-lg p-6 bg-card max-h-[600px] overflow-y-auto">
                            <MarkdownPreview content={generatedPost.content} />
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </>
                ) : (
                  <Card>
                    <CardContent className="py-12">
                      <div className="text-center text-muted-foreground">
                        <Sparkles className="w-12 h-12 mx-auto mb-4 text-purple-400" />
                        <p className="text-lg font-medium mb-2">No content generated yet</p>
                        <p className="text-sm">
                          Fill in the details and click "Generate Blog Post" to create AI-powered
                          content
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
