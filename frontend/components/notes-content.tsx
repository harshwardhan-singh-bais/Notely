"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { api, type Note } from "@/services/api";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";

const NotesViewer = dynamic(() => import("./notes-viewer"), { ssr: false });

export function NotesContent() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<Note | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    api.getNotes().then(setNotes).catch(() => {
      toast({ title: "Error", description: "Failed to load notes", variant: "destructive" });
    }).finally(() => setLoading(false));
  }, [toast]);

  const filtered = notes.filter(n => n.title.toLowerCase().includes(search.toLowerCase()) || n.source_name.toLowerCase().includes(search.toLowerCase()));

  if (loading) return (
    <div className="space-y-6">
      <Skeleton className="h-10 w-64" />
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {[...Array(6)].map((_, i) => <Skeleton key={i} className="h-96" />)}
      </div>
    </div>
  );

  if (selected) return (
    <div className="space-y-6">
      <button className="mb-2 text-blue-600 underline" onClick={() => setSelected(null)}>
        ← Back to all notes
      </button>
      <NotesViewer jobOrDocId={selected.id} type={selected.source_type as "video" | "document"} />
    </div>
  );

  return (
    <div className="space-y-6">
      <h1 className="text-4xl font-bold">Notes</h1>
      <Input placeholder="Search notes..." value={search} onChange={e => setSearch(e.target.value)} className="max-w-md" />
      {filtered.length === 0 ? (
        <Card><CardContent className="py-16 text-center">No notes found.</CardContent></Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filtered.map(note => (
            <Card key={note.id} className="cursor-pointer" onClick={() => setSelected(note)}>
              <CardHeader>
                <CardTitle>{note.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-muted-foreground">{note.source_name}</div>
                <div className="text-xs mt-2">{note.source_type} | {new Date(note.created_at).toLocaleDateString()}</div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
