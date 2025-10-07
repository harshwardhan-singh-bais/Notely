"use client"

import { useEffect, useState } from "react"
import { api } from "@/services/api"
import { Progress } from "@/components/ui/progress"
import { CheckCircle2, XCircle, Loader2, Clock } from "lucide-react"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { useToast } from "@/hooks/use-toast"

interface VideoProgress {
  progress: number
  stage: string
  message: string
}

interface JobStatusPanelProps {
  jobId: string
}

export function JobStatusPanel({ jobId }: JobStatusPanelProps) {
  const [progress, setProgress] = useState<VideoProgress | null>(null)
  const [polling, setPolling] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { toast } = useToast()

  useEffect(() => {
    if (!polling) return

    const interval = setInterval(async () => {
      try {
        const data = await api.getVideoProgress(jobId)
        setProgress(data)

        if (data.progress >= 100 || data.stage === "completed") {
          setPolling(false)
          toast({
            title: "Success!",
            description: "Video processed and notes generated successfully",
            variant: "default",
          })
        } else if (data.stage === "error") {
          setPolling(false)
          setError(data.message)
          toast({
            title: "Error",
            description: data.message,
            variant: "destructive",
          })
        }
      } catch (error) {
        console.error("[v0] Failed to fetch progress:", error)
        setError("Failed to track progress")
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [jobId, polling, toast])

  if (!progress && !error) {
    return (
      <div className="flex items-center gap-3">
        <Loader2 className="h-5 w-5 animate-spin text-primary" />
        <span className="text-muted-foreground">Loading progress...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center gap-3">
        <XCircle className="h-5 w-5 text-destructive" />
        <span className="text-destructive">{error}</span>
      </div>
    )
  }

  const getStatusIcon = () => {
    if (progress!.progress >= 100 || progress!.stage === "completed") {
      return <CheckCircle2 className="h-5 w-5 text-accent" />
    } else if (progress!.stage === "error") {
      return <XCircle className="h-5 w-5 text-destructive" />
    } else {
      return <Loader2 className="h-5 w-5 animate-spin text-primary" />
    }
  }

  const getStatusText = () => {
    if (progress!.progress >= 100 || progress!.stage === "completed") {
      return "Completed"
    } else if (progress!.stage === "error") {
      return "Failed"
    } else {
      return progress!.stage.charAt(0).toUpperCase() + progress!.stage.slice(1)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        {getStatusIcon()}
        <div className="flex-1">
          <p className="font-medium text-card-foreground capitalize">{getStatusText()}</p>
          {progress!.message && <p className="text-sm text-muted-foreground">{progress!.message}</p>}
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">{progress!.stage}</span>
          <span className="font-medium text-card-foreground">{progress!.progress}%</span>
        </div>
        <Progress value={progress!.progress} className="h-2" />
      </div>

      {(progress!.progress >= 100 || progress!.stage === "completed") && (
        <div className="flex gap-2">
          <Link href="/notes" className="flex-1">
            <Button className="w-full">View Notes</Button>
          </Link>
          <Button variant="outline" onClick={() => setPolling(true)}>
            Refresh
          </Button>
        </div>
      )}
    </div>
  )
}
