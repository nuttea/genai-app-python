'use client';

import { useState, useRef, useEffect } from 'react';
import { datadogRum } from '@datadog/browser-rum';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { imageCreatorApi, inlineDataToDataUrl } from '@/lib/api/imageCreator';
import { useToast } from '@/hooks/useToast';
import {
  Image as ImageIcon,
  Loader2,
  Sparkles,
  Wand2,
  Download,
  Trash2,
  Upload,
} from 'lucide-react';

interface GeneratedImage {
  id: string;
  url: string;
  base64: string;
  mimeType: string;
  prompt: string;
  createdAt: string;
}

export default function ImageCreatorPage() {
  const { showToast } = useToast();
  const [sessionId] = useState(() => {
    const rumSessionId = datadogRum.getInternalContext()?.session_id;
    return rumSessionId ? `img_dd_${rumSessionId}` : `img_${Date.now()}`;
  });

  // Stop RUM session on page unload/refresh (kiosk session pattern)
  useEffect(() => {
    const handleBeforeUnload = () => {
      try {
        // Stop the current session to start fresh on next load
        // This prevents session continuation across page refreshes
        datadogRum.stopSession();
        console.log('📊 Stopped Datadog RUM session on page unload');
      } catch (e) {
        console.warn('Could not stop RUM session:', e);
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      // Also stop session on component unmount
      handleBeforeUnload();
    };
  }, []);

  // State
  const [prompt, setPrompt] = useState('');
  const [imageType, setImageType] = useState<string>('diagram');
  const [aspectRatio, setAspectRatio] = useState<string>('1:1');
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentImage, setCurrentImage] = useState<GeneratedImage | null>(null);
  const [imageHistory, setImageHistory] = useState<GeneratedImage[]>([]);
  const [editPrompt, setEditPrompt] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Image types
  const imageTypes = [
    { value: 'diagram', label: 'Diagram', desc: 'Technical diagrams' },
    { value: 'comic', label: 'Comic', desc: 'Comic-style art' },
    { value: 'slide', label: 'Slide', desc: 'Presentation slides' },
    { value: 'infographic', label: 'Infographic', desc: 'Data visualizations' },
    { value: 'illustration', label: 'Illustration', desc: 'General artwork' },
    { value: 'photo', label: 'Photo', desc: 'Photorealistic' },
  ];

  // Aspect ratios
  const aspectRatios = [
    { value: '1:1', label: 'Square (1:1)' },
    { value: '16:9', label: 'Wide (16:9)' },
    { value: '9:16', label: 'Tall (9:16)' },
    { value: '4:3', label: '4:3' },
    { value: '3:2', label: '3:2' },
  ];

  // Generate image
  const handleGenerate = async () => {
    if (!prompt.trim()) {
      showToast('Please enter a prompt', 'error');
      return;
    }

    setIsGenerating(true);
    try {
      const response = await imageCreatorApi.generateImage(
        {
          prompt: prompt.trim(),
          imageType: imageType as any,
          aspectRatio: aspectRatio as any,
        },
        'user_nextjs',
        sessionId,
        (text) => {
          console.log('Agent streaming:', text);
        }
      );

      if (response.images && response.images.length > 0) {
        const imageData = response.images[0];
        const url = inlineDataToDataUrl(imageData);

        const newImage: GeneratedImage = {
          id: `img_${Date.now()}`,
          url,
          base64: imageData.data,
          mimeType: imageData.mime_type,
          prompt: prompt.trim(),
          createdAt: new Date().toISOString(),
        };

        setCurrentImage(newImage);
        setImageHistory((prev) => [newImage, ...prev].slice(0, 10)); // Keep last 10
        showToast('Image generated successfully!', 'success');
      } else {
        showToast(response.text || 'No image generated', 'error');
      }
    } catch (error) {
      console.error('Generation error:', error);
      showToast(
        error instanceof Error ? error.message : 'Failed to generate image',
        'error'
      );
    } finally {
      setIsGenerating(false);
    }
  };

  // Edit current image
  const handleEdit = async () => {
    if (!currentImage) {
      showToast('No image to edit', 'error');
      return;
    }

    if (!editPrompt.trim()) {
      showToast('Please enter edit instructions', 'error');
      return;
    }

    setIsGenerating(true);
    try {
      const response = await imageCreatorApi.editImage(
        {
          editPrompt: editPrompt.trim(),
          originalImageBase64: currentImage.base64,
          aspectRatio: aspectRatio as any,
        },
        'user_nextjs',
        sessionId, // Same session for multi-turn
        (text) => {
          console.log('Agent streaming:', text);
        }
      );

      if (response.images && response.images.length > 0) {
        const imageData = response.images[0];
        const url = inlineDataToDataUrl(imageData);

        const editedImage: GeneratedImage = {
          id: `img_${Date.now()}`,
          url,
          base64: imageData.data,
          mimeType: imageData.mime_type,
          prompt: `${currentImage.prompt} → ${editPrompt.trim()}`,
          createdAt: new Date().toISOString(),
        };

        setCurrentImage(editedImage);
        setImageHistory((prev) => [editedImage, ...prev].slice(0, 10));
        setEditPrompt('');
        showToast('Image edited successfully!', 'success');
      } else {
        showToast(response.text || 'No image generated', 'error');
      }
    } catch (error) {
      console.error('Edit error:', error);
      showToast(
        error instanceof Error ? error.message : 'Failed to edit image',
        'error'
      );
    } finally {
      setIsGenerating(false);
    }
  };

  // Download image
  const handleDownload = (image: GeneratedImage) => {
    const link = document.createElement('a');
    link.href = image.url;
    link.download = `image_${image.id}.png`;
    link.click();
  };

  // Quick edit buttons
  const quickEdits = [
    { label: 'More Colorful', prompt: 'Make it more colorful with vibrant colors' },
    { label: 'Purple Background', prompt: 'Add a purple background (Datadog purple: #632CA6)' },
    { label: 'Add Title', prompt: 'Add a clear title at the top' },
    { label: 'Simplify', prompt: 'Simplify the design, make it cleaner' },
  ];

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header title="Image Creator" />

        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-7xl mx-auto space-y-6">
            {/* Welcome Card */}
            <div className="bg-gradient-to-r from-purple-500 to-blue-500 rounded-2xl p-8 text-white shadow-lg">
              <div className="flex items-center gap-3 mb-4">
                <Sparkles className="w-8 h-8" />
                <h2 className="text-2xl font-bold">AI Image Creator</h2>
              </div>
              <p className="text-lg leading-relaxed">
                Create stunning images using Gemini 3 Pro Image. Generate diagrams, comics,
                slides, and more. Edit images conversationally with multi-turn refinement.
              </p>
            </div>

            {/* Main Content */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left: Generation Controls */}
              <div className="lg:col-span-1 space-y-6">
                {/* Generation Card */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Wand2 className="w-5 h-5" />
                    Generate Image
                  </h3>

                  {/* Image Type */}
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Image Type
                    </label>
                    <select
                      value={imageType}
                      onChange={(e) => setImageType(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                      disabled={isGenerating}
                    >
                      {imageTypes.map((type) => (
                        <option key={type.value} value={type.value}>
                          {type.label} - {type.desc}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Aspect Ratio */}
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Aspect Ratio
                    </label>
                    <select
                      value={aspectRatio}
                      onChange={(e) => setAspectRatio(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                      disabled={isGenerating}
                    >
                      {aspectRatios.map((ratio) => (
                        <option key={ratio.value} value={ratio.value}>
                          {ratio.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Prompt */}
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Prompt
                    </label>
                    <Textarea
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      placeholder="Describe the image you want to create..."
                      className="min-h-[100px]"
                      disabled={isGenerating}
                    />
                  </div>

                  <Button
                    onClick={handleGenerate}
                    disabled={isGenerating || !prompt.trim()}
                    className="w-full"
                  >
                    {isGenerating ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4 mr-2" />
                        Generate Image
                      </>
                    )}
                  </Button>
                </div>

                {/* Edit Card */}
                {currentImage && (
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                      <Wand2 className="w-5 h-5" />
                      Edit Current Image
                    </h3>

                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Edit Instructions
                      </label>
                      <Textarea
                        value={editPrompt}
                        onChange={(e) => setEditPrompt(e.target.value)}
                        placeholder="Describe how you want to edit the image..."
                        className="min-h-[80px]"
                        disabled={isGenerating}
                      />
                    </div>

                    <Button
                      onClick={handleEdit}
                      disabled={isGenerating || !editPrompt.trim()}
                      className="w-full mb-3"
                      variant="outline"
                    >
                      {isGenerating ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Editing...
                        </>
                      ) : (
                        <>
                          <Wand2 className="w-4 h-4 mr-2" />
                          Edit Image
                        </>
                      )}
                    </Button>

                    {/* Quick Edits */}
                    <div className="space-y-2">
                      <p className="text-xs text-gray-500">Quick edits:</p>
                      {quickEdits.map((edit, idx) => (
                        <Button
                          key={idx}
                          onClick={() => {
                            setEditPrompt(edit.prompt);
                            setTimeout(() => handleEdit(), 100);
                          }}
                          disabled={isGenerating}
                          variant="outline"
                          size="sm"
                          className="w-full justify-start"
                        >
                          {edit.label}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Right: Image Display & History */}
              <div className="lg:col-span-2 space-y-6">
                {/* Current Image */}
                {currentImage ? (
                  <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold">Current Image</h3>
                      <div className="flex gap-2">
                        <Button
                          onClick={() => handleDownload(currentImage)}
                          variant="outline"
                          size="sm"
                        >
                          <Download className="w-4 h-4 mr-1" />
                          Download
                        </Button>
                        <Button
                          onClick={() => setCurrentImage(null)}
                          variant="outline"
                          size="sm"
                        >
                          <Trash2 className="w-4 h-4 mr-1" />
                          Clear
                        </Button>
                      </div>
                    </div>

                    <div className="relative bg-gray-100 rounded-lg overflow-hidden">
                      <img
                        src={currentImage.url}
                        alt={currentImage.prompt}
                        className="w-full h-auto"
                      />
                    </div>

                    <div className="mt-4 text-sm text-gray-600">
                      <p>
                        <strong>Prompt:</strong> {currentImage.prompt}
                      </p>
                      <p>
                        <strong>Type:</strong> {currentImage.mimeType}
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="bg-white rounded-lg shadow p-12 text-center">
                    <ImageIcon className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                    <p className="text-gray-500">
                      No image generated yet. Create your first image using the controls on the
                      left!
                    </p>
                  </div>
                )}

                {/* Image History */}
                {imageHistory.length > 0 && (
                  <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold mb-4">History</h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                      {imageHistory.map((image) => (
                        <div
                          key={image.id}
                          className="relative group cursor-pointer"
                          onClick={() => setCurrentImage(image)}
                        >
                          <img
                            src={image.url}
                            alt={image.prompt}
                            className="w-full h-auto rounded-lg border-2 border-transparent group-hover:border-purple-500 transition"
                          />
                          <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition rounded-lg flex items-center justify-center">
                            <p className="text-white text-xs text-center px-2">
                              {image.prompt.substring(0, 50)}...
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

