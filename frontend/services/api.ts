
export interface UserSettings {
  user_id: string;
  gemini_api_key: string;
  whisper_api_key: string;
  notion_api_key: string;
  screenshot_interval: number;
  embedding_type: string;
  llm_preference: string;
}
export interface DocumentMeta {
  id: string;
  name: string;
  type: string;
  size: number;
  uploaded_at: string;
  status: "pending" | "processed";
}
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export interface VideoJobSubmit {
  url?: string
  file?: File
  screenshot_interval?: number
  smart_mode?: boolean
}

export interface DocumentUpload {
  file: File
}

export interface JobStatus {
  job_id: string
  status: "pending" | "processing" | "completed" | "failed"
  progress?: number
  message?: string
}

export interface Note {
  id: string
  title: string
  source_type: "video" | "document"
  source_name: string
  created_at: string
  model_used: string
  thumbnails: string[]
  markdown_url?: string
  pdf_url?: string
}

export interface DashboardStats {
  total_videos: number
  total_documents: number
  active_jobs: number
  recent_uploads: Array<{
    id: string
    name: string
    type: "video" | "document"
    thumbnail?: string
    created_at: string
  }>
}

class ApiService {
  // Settings endpoints
  async getUserSettings(userId: string): Promise<UserSettings> {
    return this.request(`/settings/${userId}`)
  }

  async saveUserSettings(userId: string, settings: UserSettings): Promise<UserSettings> {
    return this.request(`/settings/${userId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(settings),
    })
  }
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        ...options?.headers,
      },
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`)
    }

    return response.json()
  }

  // Video endpoints
  async submitVideoJob(data: VideoJobSubmit): Promise<{ job_id: string }> {
    const formData = new FormData()
    if (data.url) formData.append("url", data.url)
    if (data.file) formData.append("file", data.file)
    if (data.screenshot_interval) formData.append("screenshot_interval", data.screenshot_interval.toString())
    if (data.smart_mode !== undefined) formData.append("smart_mode", data.smart_mode.toString())

    return this.request("/video/submit_job/", {
      method: "POST",
      body: formData,
    })
  }

  async getJobStatus(jobId: string): Promise<JobStatus> {
    return this.request(`/video/job_status/${jobId}`)
  }

  // Document endpoints
  async uploadDocument(file: File): Promise<{ document_id: string }> {
    const formData = new FormData()
    formData.append("file", file)

    return this.request("/document/upload/", {
      method: "POST",
      body: formData,
    })
  }

  async getDocuments(): Promise<DocumentMeta[]> {
    return this.request("/document/list/")
  }

  // Progress tracking endpoints
  async getDocumentProgress(docId: string): Promise<{ progress: number; stage: string; message: string }> {
    return this.request(`/document/progress/${docId}`)
  }

  async getVideoProgress(jobId: string): Promise<{ progress: number; stage: string; message: string }> {
    return this.request(`/video/progress/${jobId}`)
  }

  // Notes endpoints
  async getNotes(): Promise<Note[]> {
    return this.request("/notes/")
  }

  async generateNotes(sourceId: string, sourceType: "video" | "document"): Promise<{ note_id: string }> {
    return this.request("/notes/generate/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source_id: sourceId, source_type: sourceType }),
    })
  }

  async downloadNotePdf(noteId: string): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/notes/download/pdf/${noteId}`)
    return response.blob()
  }

  async downloadNoteMarkdown(noteId: string): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/notes/download/md/${noteId}`)
    return response.blob()
  }

  async pushToNotion(noteId: string): Promise<{ success: boolean }> {
    return this.request(`/notion/push_notes/${noteId}`, {
      method: "POST",
    })
  }

  // Dashboard endpoints
  async getDashboardStats(): Promise<DashboardStats> {
    return this.request("/dashboard/stats")
  }
}

export const api = new ApiService()
