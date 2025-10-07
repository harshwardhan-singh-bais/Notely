"use client"

import { useEffect, useState } from "react"
import { api, type JobStatus } from "@/services/api"
import { Progress } from "@/components/ui/progress"
import { CheckCircle2, XCircle, Loader2, Clock } from "lucide-react"
import { Button } from "@/components/ui/button"
import Link from "next/link"

interface JobStatusPanelProps {
  jobId: string
}

export function JobStatusPanel({ jobId }: JobStatusPanelProps) {
  const [status, setStatus] = useState<JobStatus | null>(null)
  const [polling, setPolling] = useState(true)

  useEffect(() => {
    if (!polling) return

    const interval = setInterval(async () => {
      try {
        const data = await api.getJobStatus(jobId)
        setStatus(data)

        if (data.status === "completed" || data.status === "failed") {
          setPolling(false)
        }
      } catch (error) {
        console.error("[v0] Failed to fetch job status:", error)
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [jobId, polling])

  if (!status) {
    return (
      <div className="flex items-center gap-3">
        <Loader2 className="h-5 w-5 animate-spin text-primary" />
        <span className="text-muted-foreground">Loading job status...</span>
      </div>
    )
  }

  const getStatusIcon = () => {
    switch (status.status) {
      case "completed":
        return <CheckCircle2 className="h-5 w-5 text-accent" />
      case "failed":
        return <XCircle className="h-5 w-5 text-destructive" />
      case "processing":
        return <Loader2 className="h-5 w-5 animate-spin text-primary" />
      default:
        return <Clock className="h-5 w-5 text-muted-foreground" />
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        {getStatusIcon()}
        <div className="flex-1">
          <p className="font-medium text-card-foreground capitalize">{status.status}</p>
          {status.message && <p className="text-sm text-muted-foreground">{status.message}</p>}
        </div>
      </div>

      {status.progress !== undefined && (
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Progress</span>
            <span className="font-medium text-card-foreground">{status.progress}%</span>
          </div>
          <Progress value={status.progress} className="h-2" />
        </div>
      )}

      {status.status === "completed" && (
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
