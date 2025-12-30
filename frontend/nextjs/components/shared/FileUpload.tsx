'use client';

import { useState, useRef } from 'react';
import { Upload, X, File, Image, Video as VideoIcon } from 'lucide-react';
import { cn, formatFileSize, isValidFileType, isValidFileSize } from '@/lib/utils';
import { FILE_UPLOAD } from '@/lib/constants/config';

interface FileUploadProps {
  onFilesSelected: (files: File[]) => void;
  accept?: string[];
  maxFiles?: number;
  maxSizeMB?: number;
  className?: string;
}

export function FileUpload({
  onFilesSelected,
  accept = [
    ...FILE_UPLOAD.acceptedImageTypes,
    ...FILE_UPLOAD.acceptedVideoTypes,
    ...FILE_UPLOAD.acceptedDocTypes,
  ],
  maxFiles = 10,
  maxSizeMB = FILE_UPLOAD.maxSizeMB,
  className,
}: FileUploadProps) {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFiles = (files: File[]): { valid: File[]; errors: string[] } => {
    const valid: File[] = [];
    const errors: string[] = [];

    files.forEach((file) => {
      // Check file type
      if (!isValidFileType(file, accept)) {
        errors.push(`${file.name}: Invalid file type`);
        return;
      }

      // Check file size
      if (!isValidFileSize(file, maxSizeMB)) {
        errors.push(`${file.name}: File too large (max ${maxSizeMB}MB)`);
        return;
      }

      valid.push(file);
    });

    return { valid, errors };
  };

  const handleFilesAdded = (files: File[]) => {
    const { valid, errors: validationErrors } = validateFiles(files);

    if (validationErrors.length > 0) {
      setErrors(validationErrors);
    } else {
      setErrors([]);
    }

    const newFiles = [...selectedFiles, ...valid].slice(0, maxFiles);
    setSelectedFiles(newFiles);
    onFilesSelected(newFiles);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFilesAdded(Array.from(e.target.files));
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFilesAdded(Array.from(e.dataTransfer.files));
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const removeFile = (index: number) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index);
    setSelectedFiles(newFiles);
    onFilesSelected(newFiles);
  };

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) {
      return <Image className="w-5 h-5" />;
    } else if (file.type.startsWith('video/')) {
      return <VideoIcon className="w-5 h-5" />;
    } else {
      return <File className="w-5 h-5" />;
    }
  };

  return (
    <div className={cn('space-y-4', className)}>
      {/* Drop Zone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => fileInputRef.current?.click()}
        className={cn(
          'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
          isDragging
            ? 'border-purple-500 bg-purple-50'
            : 'border-border hover:border-purple-400 hover:bg-gray-50'
        )}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={accept.join(',')}
          onChange={handleFileInputChange}
          className="hidden"
        />

        <div className="flex flex-col items-center space-y-4">
          <div className="p-4 bg-purple-100 rounded-full">
            <Upload className="w-8 h-8 text-purple-600" />
          </div>

          <div>
            <p className="text-lg font-medium text-foreground mb-1">
              Drop files here or click to browse
            </p>
            <p className="text-sm text-muted-foreground">
              Upload up to {maxFiles} files (max {maxSizeMB}MB each)
            </p>
          </div>

          <div className="text-xs text-muted-foreground">
            <p>Supported formats:</p>
            <p>Images: PNG, JPG, JPEG, GIF, WebP</p>
            <p>Videos: MP4, MOV, AVI, WebM</p>
            <p>Documents: PDF, TXT, Markdown</p>
          </div>
        </div>
      </div>

      {/* Error Messages */}
      {errors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm font-medium text-red-800 mb-2">Upload Errors:</p>
          <ul className="list-disc list-inside space-y-1">
            {errors.map((error, index) => (
              <li key={index} className="text-sm text-red-700">
                {error}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Selected Files */}
      {selectedFiles.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium text-foreground">
            Selected Files ({selectedFiles.length}/{maxFiles})
          </p>
          <div className="space-y-2">
            {selectedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-card border border-border rounded-lg"
              >
                <div className="flex items-center space-x-3 flex-1 min-w-0">
                  <div className="text-purple-600">{getFileIcon(file)}</div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground truncate">{file.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {formatFileSize(file.size)} • {file.type || 'Unknown type'}
                    </p>
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(index);
                  }}
                  className="p-1 text-muted-foreground hover:text-red-600 transition-colors"
                  aria-label="Remove file"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
