"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Upload, LinkIcon, Loader2 } from "lucide-react"
import { FileUploader } from "@/components/file-uploader"
import { JobStatusPanel } from "@/components/job-status-panel"
import { api } from "@/services/api"
import { useToast } from "@/hooks/use-toast"

export function VideoUploadContent() {
  const [youtubeUrl, setYoutubeUrl] = useState("")
  const [videoFile, setVideoFile] = useState<File | null>(null)
  const [screenshotInterval, setScreenshotInterval] = useState(5)
  const [smartMode, setSmartMode] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [currentJobId, setCurrentJobId] = useState<string | null>(null)
  const { toast } = useToast()

  const handleYoutubeSubmit = async () => {
    if (!youtubeUrl.trim()) {
      toast({
        title: "Error",
        description: "Please enter a YouTube URL",
        variant: "destructive",
      })
      return
    }

    setIsSubmitting(true)
    try {
      const result = await api.submitVideoJob({
        url: youtubeUrl,
        screenshot_interval: screenshotInterval,
        smart_mode: smartMode,
      })
      setCurrentJobId(result.job_id)
      toast({
        title: "Success",
        description: "Video job submitted successfully",
      })
      setYoutubeUrl("")
    } catch (error) {
      console.error("[v0] Failed to submit video job:", error)
      toast({
        title: "Error",
        description: "Failed to submit video job",
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleFileSubmit = async () => {
    if (!videoFile) {
      toast({
        title: "Error",
        description: "Please select a video file",
        variant: "destructive",
      })
      return
    }

    setIsSubmitting(true)
    try {
      const result = await api.submitVideoJob({
        file: videoFile,
        screenshot_interval: screenshotInterval,
        smart_mode: smartMode,
      })
      setCurrentJobId(result.job_id)
      toast({
        title: "Success",
        description: "Video file uploaded successfully",
      })
      setVideoFile(null)
    } catch (error) {
      console.error("[v0] Failed to upload video file:", error)
      toast({
        title: "Error",
        description: "Failed to upload video file",
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-balance text-4xl font-bold tracking-tight text-foreground">Upload Video</h1>
        <p className="mt-2 text-pretty text-lg text-muted-foreground leading-relaxed">
          Process videos with AI-powered transcription and screenshot extraction
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="border-border bg-card">
          <CardHeader>
            <CardTitle className="text-card-foreground">Video Source</CardTitle>
            <CardDescription className="text-muted-foreground">Upload from YouTube or local file</CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="youtube" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="youtube">YouTube URL</TabsTrigger>
                <TabsTrigger value="file">Local File</TabsTrigger>
              </TabsList>
              <TabsContent value="youtube" className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="youtube-url" className="text-card-foreground">
                    YouTube URL
                  </Label>
                  <div className="flex gap-2">
                    <div className="relative flex-1">
                      <LinkIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        id="youtube-url"
                        placeholder="https://youtube.com/watch?v=..."
                        value={youtubeUrl}
                        onChange={(e) => setYoutubeUrl(e.target.value)}
                        className="pl-9"
                        disabled={isSubmitting}
                      />
                    </div>
                  </div>
                </div>
                <Button onClick={handleYoutubeSubmit} disabled={isSubmitting} className="w-full">
                  {isSubmitting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Submitting...
                    </>
                  ) : (
                    <>
                      <Upload className="mr-2 h-4 w-4" />
                      Submit YouTube Video
                    </>
                  )}
                </Button>
              </TabsContent>
              <TabsContent value="file" className="space-y-4">
                <FileUploader
                  accept="video/*"
                  onFileSelect={setVideoFile}
                  selectedFile={videoFile}
                  disabled={isSubmitting}
                />
                <Button onClick={handleFileSubmit} disabled={isSubmitting || !videoFile} className="w-full">
                  {isSubmitting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Uploading...
                    </>
                  ) : (
                    <>
                      <Upload className="mr-2 h-4 w-4" />
                      Upload Video File
                    </>
                  )}
                </Button>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        <Card className="border-border bg-card">
          <CardHeader>
            <CardTitle className="text-card-foreground">Processing Options</CardTitle>
            <CardDescription className="text-muted-foreground">Configure video processing settings</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="screenshot-interval" className="text-card-foreground">
                Screenshot Interval (seconds)
              </Label>
              <Input
                id="screenshot-interval"
                type="number"
                min="1"
                max="60"
                value={screenshotInterval}
                onChange={(e) => setScreenshotInterval(Number(e.target.value))}
                disabled={isSubmitting}
              />
              <p className="text-sm text-muted-foreground">Extract frames every N seconds</p>
            </div>

            <div className="flex items-center justify-between space-x-2">
              <div className="space-y-0.5">
                <Label htmlFor="smart-mode" className="text-card-foreground">
                  Smart Screenshot Mode
                </Label>
                <p className="text-sm text-muted-foreground">Only extract frames with diagrams, charts, or figures</p>
              </div>
              <Switch id="smart-mode" checked={smartMode} onCheckedChange={setSmartMode} disabled={isSubmitting} />
            </div>

            <div className="rounded-lg border border-border bg-secondary/50 p-4">
              <h4 className="mb-2 font-medium text-card-foreground">Processing Pipeline</h4>
              <ul className="space-y-1 text-sm text-muted-foreground">
                <li>• Video transcription with WhisperX</li>
                <li>• AI-powered screenshot extraction</li>
                <li>• Multi-modal embeddings (CLIP)</li>
                <li>• ChromaDB vector storage</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>

      {currentJobId && (
        <Card className="border-border bg-card">
          <CardHeader>
            <CardTitle className="text-card-foreground">Job Status</CardTitle>
            <CardDescription className="text-muted-foreground">Track your video processing progress</CardDescription>
          </CardHeader>
          <CardContent>
            <JobStatusPanel jobId={currentJobId} />
          </CardContent>
        </Card>
      )}
    </div>
  )
}
