import type { Line } from "../types";
import { get, post } from "./client";

export const getLines = () => get<Line[]>("/api/lines");

export const dial = (number: string) =>
  post<Line>("/api/lines/dial", { number });

export const hangup = (lineId: string) =>
  post<{ ok: boolean }>(`/api/lines/${lineId}/hangup`);

export const hold = (lineId: string) =>
  post<{ ok: boolean }>(`/api/lines/${lineId}/hold`);

export const unhold = (lineId: string) =>
  post<{ ok: boolean }>(`/api/lines/${lineId}/unhold`);

export const mergeLines = (lineIds: string[]) =>
  post<Line>("/api/lines/merge", { line_ids: lineIds });
