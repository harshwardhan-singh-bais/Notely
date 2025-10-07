"use client"

import type React from "react"

import { useCallback } from "react"
import { Upload, File, X } from "lucide-react"
import { Button } from "@/components/ui/button"

interface FileUploaderProps {
  accept?: string
  onFileSelect: (file: File | null) => void
  selectedFile: File | null
  disabled?: boolean
}

export function FileUploader({ accept, onFileSelect, selectedFile, disabled }: FileUploaderProps) {
  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault()
      if (disabled) return

      const files = Array.from(e.dataTransfer.files)
      if (files.length > 0) {
        onFileSelect(files[0])
      }
    },
    [onFileSelect, disabled],
  )

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
  }, [])

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files
      if (files && files.length > 0) {
        onFileSelect(files[0])
      }
    },
    [onFileSelect],
  )

  return (
    <div className="space-y-4">
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        className={`relative flex min-h-[200px] cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-border bg-secondary/50 p-8 transition-colors hover:bg-secondary/70 ${
          disabled ? "cursor-not-allowed opacity-50" : ""
        }`}
      >
        <input
          type="file"
          accept={accept}
          onChange={handleFileInput}
          disabled={disabled}
          className="absolute inset-0 cursor-pointer opacity-0"
        />
        <Upload className="mb-4 h-10 w-10 text-muted-foreground" />
        <p className="mb-2 text-center text-sm font-medium text-card-foreground">
          Drop your file here or click to browse
        </p>
        <p className="text-center text-xs text-muted-foreground">
          {accept ? `Supported formats: ${accept}` : "All file types supported"}
        </p>
      </div>

      {selectedFile && (
        <div className="flex items-center gap-3 rounded-lg border border-border bg-card p-4">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
            <File className="h-5 w-5 text-primary" />
          </div>
          <div className="flex-1">
            <p className="font-medium text-card-foreground">{selectedFile.name}</p>
            <p className="text-sm text-muted-foreground">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
          </div>
          <Button variant="ghost" size="icon" onClick={() => onFileSelect(null)} disabled={disabled}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  )
}
