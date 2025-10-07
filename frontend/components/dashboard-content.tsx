"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Video, FileText, Clock, TrendingUp } from "lucide-react"
import { api, type DashboardStats } from "@/services/api"
import { Skeleton } from "@/components/ui/skeleton"
import Link from "next/link"
import { Button } from "@/components/ui/button"

export function DashboardContent() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await api.getDashboardStats()
        setStats(data)
      } catch (error) {
        console.error("[v0] Failed to fetch dashboard stats:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <Skeleton className="h-10 w-64" />
          <Skeleton className="mt-2 h-5 w-96" />
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-balance text-4xl font-bold tracking-tight text-foreground">Welcome to Notely</h1>
        <p className="mt-2 text-pretty text-lg text-muted-foreground leading-relaxed">
          Your AI-powered multi-modal note-taking platform
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-border bg-card transition-colors hover:bg-card/80">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-card-foreground">Total Videos</CardTitle>
            <Video className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-card-foreground">{stats?.total_videos || 0}</div>
            <p className="text-xs text-muted-foreground">Processed and indexed</p>
          </CardContent>
        </Card>

        <Card className="border-border bg-card transition-colors hover:bg-card/80">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-card-foreground">Total Documents</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-card-foreground">{stats?.total_documents || 0}</div>
            <p className="text-xs text-muted-foreground">PDFs and DOCX files</p>
          </CardContent>
        </Card>

        <Card className="border-border bg-card transition-colors hover:bg-card/80">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-card-foreground">Active Jobs</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-card-foreground">{stats?.active_jobs || 0}</div>
            <p className="text-xs text-muted-foreground">Currently processing</p>
          </CardContent>
        </Card>

        <Card className="border-border bg-card transition-colors hover:bg-card/80">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-card-foreground">Notes Generated</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-card-foreground">
              {(stats?.total_videos || 0) + (stats?.total_documents || 0)}
            </div>
            <p className="text-xs text-muted-foreground">AI-powered summaries</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="border-border bg-card">
          <CardHeader>
            <CardTitle className="text-card-foreground">Recent Uploads</CardTitle>
            <CardDescription className="text-muted-foreground">Your latest processed content</CardDescription>
          </CardHeader>
          <CardContent>
            {stats?.recent_uploads && stats.recent_uploads.length > 0 ? (
              <div className="space-y-4">
                {stats.recent_uploads.map((upload) => (
                  <div
                    key={upload.id}
                    className="flex items-center gap-4 rounded-lg border border-border bg-secondary/50 p-4"
                  >
                    <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                      {upload.type === "video" ? (
                        <Video className="h-6 w-6 text-primary" />
                      ) : (
                        <FileText className="h-6 w-6 text-primary" />
                      )}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-card-foreground">{upload.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {new Date(upload.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <p className="text-muted-foreground">No uploads yet</p>
                <p className="mt-2 text-sm text-muted-foreground">Start by uploading a video or document</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="border-border bg-card">
          <CardHeader>
            <CardTitle className="text-card-foreground">Quick Actions</CardTitle>
            <CardDescription className="text-muted-foreground">Get started with Notely</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Link href="/upload-video" className="block">
              <Button className="w-full justify-start" variant="secondary">
                <Video className="mr-2 h-4 w-4" />
                Upload Video
              </Button>
            </Link>
            <Link href="/upload-document" className="block">
              <Button className="w-full justify-start" variant="secondary">
                <FileText className="mr-2 h-4 w-4" />
                Upload Document
              </Button>
            </Link>
            <Link href="/notes" className="block">
              <Button className="w-full justify-start" variant="secondary">
                <TrendingUp className="mr-2 h-4 w-4" />
                View All Notes
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
