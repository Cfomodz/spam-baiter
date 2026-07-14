import { create } from "zustand";
import type {
  ContactGroup,
  GenerationProgress,
  LegacyClip,
  Line,
  RoutingMatrix,
  SoundboardClip,
  Voice,
} from "../types";

interface AppState {
  lines: Record<string, Line>;
  setLine: (line: Line) => void;
  removeLine: (lineId: string) => void;
  setLines: (lines: Line[]) => void;

  contacts: ContactGroup[];
  setContacts: (contacts: ContactGroup[]) => void;

  clips: SoundboardClip[];
  setClips: (clips: SoundboardClip[]) => void;
  addClip: (clip: SoundboardClip) => void;
  updateClip: (clipId: string, updates: Partial<SoundboardClip>) => void;
  removeClip: (clipId: string) => void;

  legacyClips: LegacyClip[];
  setLegacyClips: (clips: LegacyClip[]) => void;

  voices: Voice[];
  setVoices: (voices: Voice[]) => void;

  routing: RoutingMatrix;
  setRouting: (routing: RoutingMatrix) => void;

  playingClipId: string | null;
  setPlayingClipId: (id: string | null) => void;

  generationProgress: Record<number, GenerationProgress>;
  setGenerationProgress: (progress: GenerationProgress) => void;
}

export const useStore = create<AppState>((set) => ({
  lines: {},
  setLine: (line) =>
    set((s) => ({ lines: { ...s.lines, [line.line_id]: line } })),
  removeLine: (lineId) =>
    set((s) => {
      const { [lineId]: _, ...rest } = s.lines;
      return { lines: rest };
    }),
  setLines: (lines) =>
    set(() => {
      const map: Record<string, Line> = {};
      for (const l of lines) map[l.line_id] = l;
      return { lines: map };
    }),

  contacts: [],
  setContacts: (contacts) => set({ contacts }),

  clips: [],
  setClips: (clips) => set({ clips }),
  addClip: (clip) => set((s) => ({ clips: [clip, ...s.clips] })),
  updateClip: (clipId, updates) =>
    set((s) => ({
      clips: s.clips.map((c) => (c.id === clipId ? { ...c, ...updates } : c)),
    })),
  removeClip: (clipId) =>
    set((s) => ({ clips: s.clips.filter((c) => c.id !== clipId) })),

  legacyClips: [],
  setLegacyClips: (clips) => set({ legacyClips: clips }),

  voices: [],
  setVoices: (voices) => set({ voices }),

  routing: { routes: {}, mic_muted: true },
  setRouting: (routing) => set({ routing }),

  playingClipId: null,
  setPlayingClipId: (id) => set({ playingClipId: id }),

  generationProgress: {},
  setGenerationProgress: (progress) =>
    set((s) => ({
      generationProgress: {
        ...s.generationProgress,
        [progress.module_id]: progress,
      },
    })),
}));
