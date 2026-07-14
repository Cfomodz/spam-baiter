import type { BaitModule, ModuleClip, ModuleSummary } from "../types";
import { del, get, post, put } from "./client";

export const getModules = () => get<ModuleSummary[]>("/api/modules");

export const getModule = (id: number) => get<BaitModule>(`/api/modules/${id}`);

export const createModule = (name: string, description?: string) =>
  post<BaitModule>("/api/modules", { name, description });

export const updateModule = (
  id: number,
  body: { name?: string; description?: string },
) => put<BaitModule>(`/api/modules/${id}`, body);

export const deleteModule = (id: number) =>
  del<{ ok: boolean }>(`/api/modules/${id}`);

export const updateClip = (
  moduleId: number,
  clipId: number,
  body: { label?: string; tier?: number; expected_duration?: number },
) => put<ModuleClip>(`/api/modules/${moduleId}/clips/${clipId}`, body);

export const deleteModuleClip = (moduleId: number, clipId: number) =>
  del<{ ok: boolean }>(`/api/modules/${moduleId}/clips/${clipId}`);

export const reorderClips = (
  moduleId: number,
  kind: "script" | "filler",
  clipIds: number[],
) => post<BaitModule>(`/api/modules/${moduleId}/reorder`, {
    kind,
    clip_ids: clipIds,
  });

export async function uploadClip(
  moduleId: number,
  file: File,
  opts: { kind: "script" | "filler"; tier?: number; expectedDuration?: number },
): Promise<ModuleClip> {
  const form = new FormData();
  form.append("file", file);
  form.append("kind", opts.kind);
  if (opts.tier != null) form.append("tier", String(opts.tier));
  if (opts.expectedDuration != null) {
    form.append("expected_duration", String(opts.expectedDuration));
  }
  const res = await fetch(`/api/modules/${moduleId}/clips`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status}: ${text}`);
  }
  return res.json();
}
