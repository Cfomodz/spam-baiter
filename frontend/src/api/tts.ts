import type { SoundboardClip, Voice } from "../types";
import { get, post } from "./client";

export const getVoices = () => get<Voice[]>("/api/tts/voices");

export const generateSpeech = (text: string, voiceId: string) =>
  post<SoundboardClip>("/api/tts/generate", { text, voice_id: voiceId });
