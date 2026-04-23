import type { LegacyClip, SoundboardClip } from "../types";
import { del, get, post } from "./client";

export const getClips = () => get<SoundboardClip[]>("/api/soundboard/clips");

export const pinClip = (clipId: string) =>
  post<SoundboardClip>(`/api/soundboard/clips/${clipId}/pin`);

export const unpinClip = (clipId: string) =>
  post<SoundboardClip>(`/api/soundboard/clips/${clipId}/unpin`);

export const deleteClip = (clipId: string) =>
  del<{ ok: boolean }>(`/api/soundboard/clips/${clipId}`);

export const getLegacyClips = () =>
  get<LegacyClip[]>("/api/soundboard/legacy");
