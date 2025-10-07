"use client"

import { useState, useEffect } from "react"
import { api } from "@/services/api"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

import { Key, Brain, Settings2, Save } from "lucide-react"

import { useToast } from "@/hooks/use-toast"

export function SettingsContent() {
  // TODO: Replace with real user ID from auth context/session
  const userId = "demo-user";
  const [geminiKey, setGeminiKey] = useState("")
  const [whisperKey, setWhisperKey] = useState("")
  const [notionKey, setNotionKey] = useState("")
  const [screenshotInterval, setScreenshotInterval] = useState("5")
  const [embeddingType, setEmbeddingType] = useState("clip")
  const [llmPreference, setLlmPreference] = useState("gemini")
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)

  // Load settings from backend on mount
  useEffect(() => {
    setLoading(true)
    api.getUserSettings(userId)
      .then((settings) => {
        setGeminiKey(settings.gemini_api_key || "")
        setWhisperKey(settings.whisper_api_key || "")
        setNotionKey(settings.notion_api_key || "")
        setScreenshotInterval(settings.screenshot_interval?.toString() || "5")
        setEmbeddingType(settings.embedding_type || "clip")
        setLlmPreference(settings.llm_preference || "gemini")
      })
      .catch(() => {
        // Optionally show a toast or ignore if no settings exist yet
      })
      .finally(() => setLoading(false))
  }, [])

  const handleSaveApiKeys = async () => {
    setLoading(true)
    try {
      await api.saveUserSettings(userId, {
        user_id: userId,
        gemini_api_key: geminiKey,
        whisper_api_key: whisperKey,
        notion_api_key: notionKey,
        screenshot_interval: Number(screenshotInterval),
        embedding_type: embeddingType,
        llm_preference: llmPreference,
      })
      toast({
        title: "Success",
        description: "API keys saved to backend successfully",
      })
    } catch (e) {
      toast({
        title: "Error",
        description: "Failed to save API keys",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleSaveProcessing = async () => {
    setLoading(true)
    try {
      await api.saveUserSettings(userId, {
        user_id: userId,
        gemini_api_key: geminiKey,
        whisper_api_key: whisperKey,
        notion_api_key: notionKey,
        screenshot_interval: Number(screenshotInterval),
        embedding_type: embeddingType,
        llm_preference: llmPreference,
      })
      toast({
        title: "Success",
        description: "Processing settings saved to backend successfully",
      })
    } catch (e) {
      toast({
        title: "Error",
        description: "Failed to save processing settings",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-balance text-4xl font-bold tracking-tight text-foreground">Settings</h1>
        <p className="mt-2 text-pretty text-lg text-muted-foreground leading-relaxed">
          Configure your Notely preferences and API keys
        </p>
      </div>

      <Tabs defaultValue="api-keys" className="w-full">
        <TabsList className="grid w-full grid-cols-2 lg:w-[400px]">
          <TabsTrigger value="api-keys">API Keys</TabsTrigger>
          <TabsTrigger value="processing">Processing</TabsTrigger>
        </TabsList>

        <TabsContent value="api-keys" className="space-y-6">
          <Card className="border-border bg-card">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Key className="h-5 w-5 text-primary" />
                <CardTitle className="text-card-foreground">API Keys</CardTitle>
              </div>
              <CardDescription className="text-muted-foreground">
                Configure your API keys for AI services
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="gemini-key" className="text-card-foreground">
                  Gemini API Key
                </Label>
                <Input
                  id="gemini-key"
                  type="password"
                  placeholder="Enter your Gemini API key"
                  value={geminiKey}
                  onChange={(e) => setGeminiKey(e.target.value)}
                />
                <p className="text-sm text-muted-foreground">Used for AI-powered note generation and vision tasks</p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="whisper-key" className="text-card-foreground">
                  OpenAI Whisper API Key
                </Label>
                <Input
                  id="whisper-key"
                  type="password"
                  placeholder="Enter your OpenAI API key"
                  value={whisperKey}
                  onChange={(e) => setWhisperKey(e.target.value)}
                />
                <p className="text-sm text-muted-foreground">Used for video transcription with WhisperX</p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="notion-key" className="text-card-foreground">
                  Notion API Key
                </Label>
                <Input
                  id="notion-key"
                  type="password"
                  placeholder="Enter your Notion integration token"
                  value={notionKey}
                  onChange={(e) => setNotionKey(e.target.value)}
                />
                <p className="text-sm text-muted-foreground">Used to push generated notes to your Notion workspace</p>
              </div>

              <Button onClick={handleSaveApiKeys} className="w-full">
                <Save className="mr-2 h-4 w-4" />
                Save API Keys
              </Button>
            </CardContent>
          </Card>

          <Card className="border-border bg-card">
            <CardHeader>
              <CardTitle className="text-card-foreground">Security Notice</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Your API keys are stored locally in your browser and are never sent to our servers. For production use,
                consider using environment variables or a secure key management system.
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="processing" className="space-y-6">
          <Card className="border-border bg-card">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Settings2 className="h-5 w-5 text-primary" />
                <CardTitle className="text-card-foreground">Processing Settings</CardTitle>
              </div>
              <CardDescription className="text-muted-foreground">
                Configure default processing parameters
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="screenshot-interval" className="text-card-foreground">
                  Default Screenshot Interval (seconds)
                </Label>
                <Input
                  id="screenshot-interval"
                  type="number"
                  min="1"
                  max="60"
                  value={screenshotInterval}
                  onChange={(e) => setScreenshotInterval(e.target.value)}
                />
                <p className="text-sm text-muted-foreground">How often to extract frames from videos</p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="embedding-type" className="text-card-foreground">
                  Embedding Type
                </Label>
                <Select value={embeddingType} onValueChange={setEmbeddingType}>
                  <SelectTrigger id="embedding-type">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="clip">CLIP (Multi-modal)</SelectItem>
                    <SelectItem value="gemini">Gemini Vision</SelectItem>
                    <SelectItem value="openai">OpenAI Embeddings</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-sm text-muted-foreground">Choose the embedding model for vector storage</p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="llm-preference" className="text-card-foreground">
                  LLM Preference
                </Label>
                <Select value={llmPreference} onValueChange={setLlmPreference}>
                  <SelectTrigger id="llm-preference">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="gemini">Gemini Pro</SelectItem>
                    <SelectItem value="llama">LLaMA</SelectItem>
                    <SelectItem value="mistral">Mistral</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-sm text-muted-foreground">
                  Select your preferred language model for note generation
                </p>
              </div>

              <Button onClick={handleSaveProcessing} className="w-full">
                <Save className="mr-2 h-4 w-4" />
                Save Processing Settings
              </Button>
            </CardContent>
          </Card>

          <Card className="border-border bg-card">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Brain className="h-5 w-5 text-accent" />
                <CardTitle className="text-card-foreground">Processing Pipeline</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-medium text-primary">
                    1
                  </div>
                  <div>
                    <p className="font-medium text-card-foreground">Ingestion</p>
                    <p className="text-sm text-muted-foreground">Video/document upload and validation</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-medium text-primary">
                    2
                  </div>
                  <div>
                    <p className="font-medium text-card-foreground">Extraction</p>
                    <p className="text-sm text-muted-foreground">Transcription and screenshot detection</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-medium text-primary">
                    3
                  </div>
                  <div>
                    <p className="font-medium text-card-foreground">Embedding</p>
                    <p className="text-sm text-muted-foreground">Multi-modal vector generation</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent/10 text-sm font-medium text-accent">
                    4
                  </div>
                  <div>
                    <p className="font-medium text-card-foreground">Generation</p>
                    <p className="text-sm text-muted-foreground">AI-powered note composition</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
