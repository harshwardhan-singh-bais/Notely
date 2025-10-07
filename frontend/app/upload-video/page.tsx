import { SidebarProvider } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/app-sidebar"
import { AppHeader } from "@/components/app-header"
import { VideoUploadContent } from "@/components/video-upload-content"

export default function UploadVideoPage() {
  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full">
        <AppSidebar />
        <div className="flex flex-1 flex-col">
          <AppHeader />
          <main className="flex-1 p-6">
            <VideoUploadContent />
          </main>
        </div>
      </div>
    </SidebarProvider>
  )
}
