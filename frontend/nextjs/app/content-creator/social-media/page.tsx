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
import { contentCreatorApi, SocialMediaRequest, SocialMediaResponse } from '@/lib/api/contentCreator';
import { useApi } from '@/hooks/useApi';
import { useToast } from '@/hooks/useToast';
import { Download, Copy, Sparkles, Share2, Check } from 'lucide-react';
import { copyToClipboard, downloadBlob } from '@/lib/utils';

export default function SocialMediaPage() {
  const [topic, setTopic] = useState('');
  const [keyMessage, setKeyMessage] = useState('');
  const [platforms, setPlatforms] = useState<string[]>(['linkedin']);
  const [style, setStyle] = useState('professional');
  const [files, setFiles] = useState<File[]>([]);
  const [uploadedFileIds, setUploadedFileIds] = useState<string[]>([]);
  const [generatedPosts, setGeneratedPosts] = useState<SocialMediaResponse | null>(null);

  const { loading, error, execute } = useApi<SocialMediaResponse, SocialMediaRequest>();
  const toast = useToast();

  const availablePlatforms = [
    { id: 'linkedin', name: 'LinkedIn', emoji: '💼', limit: 3000 },
    { id: 'twitter', name: 'Twitter/X', emoji: '🐦', limit: 280 },
    { id: 'instagram', name: 'Instagram', emoji: '📷', limit: 2200 },
  ];

  const handleFilesSelected = async (selectedFiles: File[]) => {
    setFiles(selectedFiles);

    if (selectedFiles.length > 0) {
      try {
        const uploadPromises = selectedFiles.map((file) => contentCreatorApi.uploadFile(file));
        const results = await Promise.all(uploadPromises);
        const fileIds = results.map((r) => r.file_id).filter((id): id is string => id !== undefined);
        setUploadedFileIds(fileIds);
        toast.success(`Uploaded ${fileIds.length} file(s) successfully`);
      } catch (err) {
        toast.error('Failed to upload files');
        console.error('Upload error:', err);
      }
    }
  };

  const togglePlatform = (platformId: string) => {
    if (platforms.includes(platformId)) {
      setPlatforms(platforms.filter((p) => p !== platformId));
    } else {
      setPlatforms([...platforms, platformId]);
    }
  };

  const handleGenerate = async () => {
    if (!topic.trim()) {
      toast.error('Please enter a topic');
      return;
    }

    if (platforms.length === 0) {
      toast.error('Please select at least one platform');
      return;
    }

    const request: SocialMediaRequest = {
      content: topic.trim(),
      topic: topic.trim(),
      key_message: keyMessage.trim() || undefined,
      platforms,
      style,
      file_ids: uploadedFileIds.length > 0 ? uploadedFileIds : undefined,
      generation_config: {
        temperature: 0.7,
        max_tokens: 4096,
        model: 'gemini-2.5-flash',
      },
    };

    const result = await execute(contentCreatorApi.generateSocialMedia, request);

    if (result) {
      setGeneratedPosts(result);
      toast.success('Social media posts generated successfully!');
    } else {
      toast.error(error || 'Failed to generate social media posts');
    }
  };

  const handleCopyPost = async (content: string, platform: string) => {
    const success = await copyToClipboard(content);
    if (success) {
      toast.success(`Copied ${platform} post!`);
    } else {
      toast.error('Failed to copy');
    }
  };

  const handleDownloadAll = () => {
    if (generatedPosts) {
      const content = generatedPosts.posts
        .map((post) => {
          const lines = [
            `=== ${post.platform.toUpperCase()} ===`,
            '',
            post.content,
            '',
            `Hashtags: ${post.hashtags.join(' ')}`,
            `Character count: ${post.character_count}`,
            '',
            '---',
            '',
          ];
          return lines.join('\n');
        })
        .join('\n');

      const blob = new Blob([content], { type: 'text/plain' });
      const filename = `social-media-posts-${Date.now()}.txt`;
      downloadBlob(blob, filename);
      toast.success('Downloaded all posts!');
    }
  };

  const getPlatformEmoji = (platform: string) => {
    const found = availablePlatforms.find((p) => p.id === platform);
    return found ? found.emoji : '📱';
  };

  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header title="Generate Social Media Posts" />
        <main className="flex-1 overflow-y-auto p-8">
          <div className="max-w-7xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Input Form */}
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Post Details</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Topic */}
                    <div className="space-y-2">
                      <Label htmlFor="topic">Topic *</Label>
                      <Input
                        id="topic"
                        placeholder="e.g., Introducing Datadog Cloud Cost Management"
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                      />
                    </div>

                    {/* Key Message */}
                    <div className="space-y-2">
                      <Label htmlFor="keyMessage">Key Message (Optional)</Label>
                      <Textarea
                        id="keyMessage"
                        placeholder="What's the main takeaway? (optional)"
                        rows={3}
                        value={keyMessage}
                        onChange={(e) => setKeyMessage(e.target.value)}
                      />
                    </div>

                    {/* Platform Selection */}
                    <div className="space-y-2">
                      <Label>Target Platforms *</Label>
                      <div className="grid grid-cols-1 gap-2">
                        {availablePlatforms.map((platform) => (
                          <button
                            key={platform.id}
                            type="button"
                            onClick={() => togglePlatform(platform.id)}
                            className={`flex items-center justify-between p-3 border rounded-lg transition-colors ${
                              platforms.includes(platform.id)
                                ? 'border-purple-500 bg-purple-50'
                                : 'border-border hover:border-purple-300'
                            }`}
                          >
                            <div className="flex items-center">
                              <span className="text-2xl mr-3">{platform.emoji}</span>
                              <div className="text-left">
                                <p className="font-medium text-sm">{platform.name}</p>
                                <p className="text-xs text-muted-foreground">
                                  Max {platform.limit} characters
                                </p>
                              </div>
                            </div>
                            {platforms.includes(platform.id) && (
                              <Check className="w-5 h-5 text-purple-600" />
                            )}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Style */}
                    <div className="space-y-2">
                      <Label htmlFor="style">Post Style</Label>
                      <select
                        id="style"
                        value={style}
                        onChange={(e) => setStyle(e.target.value)}
                        className="w-full h-10 px-3 py-2 text-sm rounded-md border border-input bg-background"
                      >
                        <option value="professional">Professional</option>
                        <option value="casual">Casual & Friendly</option>
                        <option value="promotional">Promotional</option>
                        <option value="educational">Educational</option>
                      </select>
                    </div>
                  </CardContent>
                </Card>

                {/* File Upload */}
                <Card>
                  <CardHeader>
                    <CardTitle>Media Attachments (Optional)</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <FileUpload
                      onFilesSelected={handleFilesSelected}
                      maxFiles={3}
                      accept={['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp']}
                    />
                    <p className="text-xs text-muted-foreground mt-2">
                      Upload images to include in posts (AI will analyze and reference them)
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
                  {loading ? 'Generating...' : 'Generate Social Media Posts'}
                </Button>

                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-sm text-red-800">{error}</p>
                  </div>
                )}
              </div>

              {/* Preview/Output */}
              <div className="space-y-6">
                {generatedPosts ? (
                  <>
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-semibold">Generated Posts</h3>
                      <Button variant="outline" size="sm" onClick={handleDownloadAll}>
                        <Download className="w-4 h-4 mr-2" />
                        Download All
                      </Button>
                    </div>

                    {generatedPosts.posts.map((post, index) => (
                      <Card key={index}>
                        <CardHeader>
                          <div className="flex items-center justify-between">
                            <CardTitle className="flex items-center text-base">
                              <span className="text-2xl mr-2">{getPlatformEmoji(post.platform)}</span>
                              {post.platform.charAt(0).toUpperCase() + post.platform.slice(1)}
                            </CardTitle>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleCopyPost(post.content, post.platform)}
                            >
                              <Copy className="w-4 h-4 mr-2" />
                              Copy
                            </Button>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-4">
                            {/* Post Content */}
                            <div className="border border-border rounded-lg p-4 bg-card">
                              <p className="text-sm text-foreground whitespace-pre-wrap">
                                {post.content}
                              </p>
                            </div>

                            {/* Hashtags */}
                            <div className="flex flex-wrap gap-2">
                              {post.hashtags.map((tag, tagIndex) => (
                                <span
                                  key={tagIndex}
                                  className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full"
                                >
                                  #{tag}
                                </span>
                              ))}
                            </div>

                            {/* Metadata */}
                            <div className="flex justify-between text-xs text-muted-foreground">
                              <span>
                                {post.character_count} / {
                                  availablePlatforms.find((p) => p.id === post.platform)?.limit
                                } characters
                              </span>
                              <span className="text-green-600 font-medium">
                                {Math.round(
                                  (post.character_count /
                                    (availablePlatforms.find((p) => p.id === post.platform)
                                      ?.limit || 1)) *
                                    100
                                )}
                                % used
                              </span>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}

                    {/* Engagement Tips */}
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <p className="text-sm font-medium text-green-900 mb-2">
                        📈 Engagement Tips
                      </p>
                      <ul className="text-xs text-green-800 space-y-1">
                        <li>• Post during peak hours for your audience</li>
                        <li>• Respond to comments within the first hour</li>
                        <li>• Use relevant trending hashtags</li>
                        <li>• Include a clear call-to-action</li>
                        <li>• Tag relevant accounts or brands</li>
                      </ul>
                    </div>
                  </>
                ) : (
                  <Card>
                    <CardContent className="py-12">
                      <div className="text-center text-muted-foreground">
                        <Share2 className="w-12 h-12 mx-auto mb-4 text-purple-400" />
                        <p className="text-lg font-medium mb-2">No posts generated yet</p>
                        <p className="text-sm">
                          Fill in the details and select platforms to create AI-powered social
                          media content
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

