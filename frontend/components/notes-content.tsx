"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Download, FileText, Video, Search, Share2 } from "lucide-react"
import { api, type Note } from "@/services/api"
import { useToast } from "@/hooks/use-toast"
import { Skeleton } from "@/components/ui/skeleton"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export function NotesContent() {
  const [notes, setNotes] = useState<Note[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [filterType, setFilterType] = useState<"all" | "video" | "document">("all")
  const { toast } = useToast()

  useEffect(() => {
    const fetchNotes = async () => {
      try {
        const data = await api.getNotes()
        setNotes(data)
      } catch (error) {
        console.error("[v0] Failed to fetch notes:", error)
        toast({
          title: "Error",
          description: "Failed to load notes",
          variant: "destructive",
        })
      } finally {
        setLoading(false)
      }
    }

    fetchNotes()
  }, [toast])

  const handleDownloadPdf = async (noteId: string, title: string) => {
    try {
      const blob = await api.downloadNotePdf(noteId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `${title}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      toast({
        title: "Success",
        description: "PDF downloaded successfully",
      })
    } catch (error) {
      console.error("[v0] Failed to download PDF:", error)
      toast({
        title: "Error",
        description: "Failed to download PDF",
        variant: "destructive",
      })
    }
  }

  const handleDownloadMarkdown = async (noteId: string, title: string) => {
    try {
      const blob = await api.downloadNoteMarkdown(noteId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `${title}.md`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      toast({
        title: "Success",
        description: "Markdown downloaded successfully",
      })
    } catch (error) {
      console.error("[v0] Failed to download Markdown:", error)
      toast({
        title: "Error",
        description: "Failed to download Markdown",
        variant: "destructive",
      })
    }
  }

  const handlePushToNotion = async (noteId: string) => {
    try {
      await api.pushToNotion(noteId)
      toast({
        title: "Success",
        description: "Note pushed to Notion successfully",
      })
    } catch (error) {
      console.error("[v0] Failed to push to Notion:", error)
      toast({
        title: "Error",
        description: "Failed to push to Notion",
        variant: "destructive",
      })
    }
  }

  const filteredNotes = notes.filter((note) => {
    const matchesSearch =
      note.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      note.source_name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesFilter = filterType === "all" || note.source_type === filterType
    return matchesSearch && matchesFilter
  })

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-96" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-balance text-4xl font-bold tracking-tight text-foreground">Notes</h1>
        <p className="mt-2 text-pretty text-lg text-muted-foreground leading-relaxed">
          Browse and manage your AI-generated notes
        </p>
      </div>

      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative flex-1 sm:max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search notes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={filterType} onValueChange={(value: any) => setFilterType(value)}>
          <SelectTrigger className="w-full sm:w-[180px]">
            <SelectValue placeholder="Filter by type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="video">Videos</SelectItem>
            <SelectItem value="document">Documents</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {filteredNotes.length === 0 ? (
        <Card className="border-border bg-card">
          <CardContent className="flex flex-col items-center justify-center py-16">
            <FileText className="mb-4 h-12 w-12 text-muted-foreground" />
            <p className="text-lg font-medium text-card-foreground">No notes found</p>
            <p className="mt-2 text-sm text-muted-foreground">
              {searchQuery || filterType !== "all"
                ? "Try adjusting your search or filters"
                : "Upload a video or document to get started"}
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredNotes.map((note) => (
            <Card key={note.id} className="group border-border bg-card transition-all hover:shadow-lg">
              <CardHeader>
                <div className="mb-3 flex items-start justify-between">
                  <Badge variant={note.source_type === "video" ? "default" : "secondary"} className="gap-1">
                    {note.source_type === "video" ? <Video className="h-3 w-3" /> : <FileText className="h-3 w-3" />}
                    {note.source_type}
                  </Badge>
                  <span className="text-xs text-muted-foreground">
                    {new Date(note.created_at).toLocaleDateString()}
                  </span>
                </div>
                <CardTitle className="text-balance text-xl text-card-foreground">{note.title}</CardTitle>
                <CardDescription className="text-muted-foreground">{note.source_name}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {note.thumbnails && note.thumbnails.length > 0 && (
                  <div className="grid grid-cols-3 gap-2">
                    {note.thumbnails.slice(0, 3).map((thumb, idx) => (
                      <div
                        key={idx}
                        className="aspect-video overflow-hidden rounded-md border border-border bg-secondary"
                      >
                        <img
                          src={thumb || `/placeholder.svg?height=100&width=150&query=diagram`}
                          alt={`Screenshot ${idx + 1}`}
                          className="h-full w-full object-cover"
                        />
                      </div>
                    ))}
                  </div>
                )}

                <div className="space-y-1 text-sm">
                  <p className="text-muted-foreground">
                    <span className="font-medium text-card-foreground">Model:</span> {note.model_used}
                  </p>
                </div>

                <div className="flex flex-wrap gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleDownloadPdf(note.id, note.title)}
                    className="flex-1"
                  >
                    <Download className="mr-1 h-3 w-3" />
                    PDF
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleDownloadMarkdown(note.id, note.title)}
                    className="flex-1"
                  >
                    <Download className="mr-1 h-3 w-3" />
                    MD
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => handlePushToNotion(note.id)} className="w-full">
                    <Share2 className="mr-1 h-3 w-3" />
                    Push to Notion
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
