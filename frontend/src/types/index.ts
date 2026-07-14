export type LineStatus =
  | "idle"
  | "dialing"
  | "active"
  | "held"
  | "merged"
  | "disconnected";

export interface Line {
  line_id: string;
  status: LineStatus;
  number: string;
  contact_name?: string;
  started_at?: number;
  merged_with: string[];
}

export interface ContactGroup {
  id: number;
  name: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  phone_numbers: PhoneNumber[];
}

export interface PhoneNumber {
  id: number;
  number: string;
  label?: string;
  group_id?: number;
  sequence_num?: number;
  created_at: string;
}

export interface Voice {
  voice_id: string;
  name: string;
  preview_url?: string;
}

export interface SoundboardClip {
  id: string;
  label: string;
  voice_id: string;
  voice_name?: string;
  file_path: string;
  pinned: boolean;
  duration?: number;
  created_at?: string;
  source: "generated" | "legacy";
}

export interface LegacyClip {
  id: number;
  persona: string;
  label: string;
  file_path: string;
  category?: string;
  display_order?: number;
}

export interface ModuleClip {
  id: number;
  kind: "script" | "filler";
  label: string;
  file_path: string;
  tier?: number | null;
  expected_duration?: number | null;
  position: number;
}

export interface ModuleSummary {
  id: number;
  name: string;
  description?: string | null;
  script_count: number;
  filler_count: number;
  updated_at: string;
}

export interface BaitModule {
  id: number;
  name: string;
  description?: string | null;
  created_at: string;
  updated_at: string;
  clips: ModuleClip[];
}

export interface RoutingMatrix {
  routes: Record<string, Record<string, boolean>>;
  mic_muted: boolean;
}

export type WSMessage =
  | { type: "line_update"; payload: Line }
  | { type: "line_removed"; payload: { line_id: string } }
  | {
      type: "audio_levels";
      payload: { levels: Record<string, number>; mic: number };
    }
  | { type: "routing_update"; payload: RoutingMatrix }
  | {
      type: "clip_ready";
      payload: {
        clip_id: string;
        label: string;
        voice_name?: string;
        pinned: boolean;
      };
    }
  | {
      type: "playback_state";
      payload: { clip_id: string; state: "playing" | "stopped"; line_ids: string[] };
    }
  | { type: "error"; payload: { message: string } };
