"use client"

import { useState, useEffect, useRef } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { FileText, Loader2, CheckCircle2 } from "lucide-react"
import { FileUploader } from "@/components/file-uploader"
import { api } from "@/services/api"
import { useToast } from "@/hooks/use-toast"
import { Progress } from "@/components/ui/progress"

interface UploadedDocument {
  id: string
  name: string
  size: number
  status: "pending" | "processed"
  uploadedAt: Date
}

interface ProcessingStatus {
  docId: string | null
  progress: number
  stage: string
  message: string
}


export function DocumentUploadContent() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadedDocuments, setUploadedDocuments] = useState<UploadedDocument[]>([])
  const [processing, setProcessing] = useState<ProcessingStatus>({ docId: null, progress: 0, stage: "", message: "" })
  const progressInterval = useRef<NodeJS.Timeout | null>(null)
  const { toast } = useToast()

  // Cleanup progress tracking on unmount
  useEffect(() => {
    return () => {
      if (progressInterval.current) {
        clearInterval(progressInterval.current)
      }
    }
  }, [])

  // Progress tracking function
  const trackProgress = (docId: string) => {
    progressInterval.current = setInterval(async () => {
      try {
        const progressData = await api.getDocumentProgress(docId)
        setProcessing({
          docId,
          progress: progressData.progress,
          stage: progressData.stage,
          message: progressData.message
        })

        if (progressData.progress >= 100 || progressData.stage === "completed") {
          if (progressInterval.current) {
            clearInterval(progressInterval.current)
          }
          setIsUploading(false)
          setProcessing({ docId: null, progress: 0, stage: "", message: "" })
          
          // Show success notification
          toast({
            title: "Success!",
            description: "Document processed and notes generated successfully",
            variant: "default",
          })
          
          // Refresh documents list
          const docs = await api.getDocuments()
          setUploadedDocuments(
            docs.map((doc) => ({
              id: doc.id,
              name: doc.name,
              size: doc.size,
              status: doc.status,
              uploadedAt: new Date(doc.uploaded_at),
            }))
          )
        } else if (progressData.stage === "error") {
          if (progressInterval.current) {
            clearInterval(progressInterval.current)
          }
          setIsUploading(false)
          setProcessing({ docId: null, progress: 0, stage: "", message: "" })
          
          toast({
            title: "Error",
            description: progressData.message,
            variant: "destructive",
          })
        }
      } catch (error) {
        console.error("Failed to track progress:", error)
      }
    }, 1000) // Poll every second
  }

  // Fetch uploaded documents from backend on mount
  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const docs = await api.getDocuments()
        setUploadedDocuments(
          docs.map((doc) => ({
            id: doc.id,
            name: doc.name,
            size: doc.size,
            status: doc.status,
            uploadedAt: new Date(doc.uploaded_at),
          }))
        )
      } catch (error) {
        console.error("[v0] Failed to fetch documents:", error)
        toast({
          title: "Error",
          description: "Failed to load documents",
          variant: "destructive",
        })
      }
    }
    fetchDocuments()
  }, [toast])

  const handleUpload = async () => {
    if (!selectedFile) {
      toast({
        title: "Error",
        description: "Please select a document to upload",
        variant: "destructive",
      })
      return
    }

    setIsUploading(true)

    try {
      const response = await api.uploadDocument(selectedFile)
      const docId = response.document_id
      
      // Start progress tracking
      trackProgress(docId)
      
      setSelectedFile(null)
    } catch (error) {
      console.error("[v0] Failed to upload document:", error)
      setIsUploading(false)
      toast({
        title: "Error",
        description: "Failed to upload document",
        variant: "destructive",
      })
    }
  }

  const handleGenerateNotes = async (documentId: string) => {
    try {
      await api.generateNotes(documentId, "document")
      toast({
        title: "Success",
        description: "Note generation started",
      })

      setUploadedDocuments((prev) =>
        prev.map((doc) => (doc.id === documentId ? { ...doc, status: "processed" as const } : doc)),
      )
    } catch (error) {
      console.error("[v0] Failed to generate notes:", error)
      toast({
        title: "Error",
        description: "Failed to generate notes",
        variant: "destructive",
      })
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-balance text-4xl font-bold tracking-tight text-foreground">Upload Document</h1>
        <p className="mt-2 text-pretty text-lg text-muted-foreground leading-relaxed">
          Process PDFs and DOCX files with AI-powered summarization
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="border-border bg-card">
          <CardHeader>
            <CardTitle className="text-card-foreground">Document Upload</CardTitle>
            <CardDescription className="text-muted-foreground">Upload PDF or DOCX files for processing</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <FileUploader
              accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              onFileSelect={setSelectedFile}
              selectedFile={selectedFile}
              disabled={isUploading}
            />

            {/* Show upload progress */}
            {isUploading && (
              <div className="space-y-2">
                {processing.docId ? (
                  <>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground capitalize">{processing.stage || 'Processing...'}</span>
                      <span className="font-medium text-card-foreground">{processing.progress}%</span>
                    </div>
                    <Progress value={processing.progress} className="h-2" />
                    {processing.message && (
                      <p className="text-xs text-muted-foreground">{processing.message}</p>
                    )}
                  </>
                ) : (
                  <>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Uploading...</span>
                      <span className="font-medium text-card-foreground">Preparing...</span>
                    </div>
                    <Progress value={5} className="h-2" />
                  </>
                )}
              </div>
            )}

            <Button onClick={handleUpload} disabled={isUploading || !selectedFile} className="w-full">
              {isUploading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <FileText className="mr-2 h-4 w-4" />
                  Upload Document
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        <Card className="border-border bg-card">
          <CardHeader>
            <CardTitle className="text-card-foreground">Processing Features</CardTitle>
            <CardDescription className="text-muted-foreground">What happens after upload</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                  <FileText className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h4 className="font-medium text-card-foreground">Text Extraction</h4>
                  <p className="text-sm text-muted-foreground">Extract and parse content from PDFs and DOCX files</p>
                </div>
              </div>

              <div className="flex gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-accent/10">
                  <CheckCircle2 className="h-5 w-5 text-accent" />
                </div>
                <div>
                  <h4 className="font-medium text-card-foreground">RAG Processing</h4>
                  <p className="text-sm text-muted-foreground">Create embeddings and store in ChromaDB for retrieval</p>
                </div>
              </div>

              <div className="flex gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                  <FileText className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h4 className="font-medium text-card-foreground">AI Summarization</h4>
                  <p className="text-sm text-muted-foreground">Generate comprehensive notes using multi-LLM backend</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {uploadedDocuments.length > 0 && (
        <Card className="border-border bg-card">
          <CardHeader>
            <CardTitle className="text-card-foreground">Uploaded Documents</CardTitle>
            <CardDescription className="text-muted-foreground">Manage your uploaded documents</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {uploadedDocuments.map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center gap-4 rounded-lg border border-border bg-secondary/50 p-4"
                >
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                    <FileText className="h-6 w-6 text-primary" />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-card-foreground">{doc.name}</p>
                    <div className="flex items-center gap-3 text-sm text-muted-foreground">
                      <span>{(doc.size / 1024 / 1024).toFixed(2)} MB</span>
                      <span>•</span>
                      <span className="capitalize">{doc.status}</span>
                      <span>•</span>
                      <span>{doc.uploadedAt.toLocaleDateString()}</span>
                    </div>
                  </div>
            {/* Show processing status */}
            {processing.docId === doc.id && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground capitalize">{processing.stage}</span>
                  <span className="font-medium text-card-foreground">{processing.progress}%</span>
                </div>
                <Progress value={processing.progress} className="h-2" />
                {processing.message && (
                  <p className="text-xs text-muted-foreground">{processing.message}</p>
                )}
              </div>
            )}
            {processing.docId !== doc.id && doc.status === "processed" && (
              <div className="flex items-center gap-2 text-sm text-accent">
                <CheckCircle2 className="h-4 w-4" />
                <span>Processed</span>
              </div>
            )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
