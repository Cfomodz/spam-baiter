import type { ContactGroup, PhoneNumber } from "../types";
import { del, get, post, put } from "./client";

export const getGroups = () => get<ContactGroup[]>("/api/contacts/groups");

export const createGroup = (name: string, notes?: string) =>
  post<ContactGroup>("/api/contacts/groups", { name, notes });

export const updateGroup = (id: number, data: { name?: string; notes?: string }) =>
  put<ContactGroup>(`/api/contacts/groups/${id}`, data);

export const deleteGroup = (id: number) =>
  del<{ ok: boolean }>(`/api/contacts/groups/${id}`);

export const addNumber = (number: string, groupId?: number, label?: string) =>
  post<PhoneNumber>("/api/contacts/numbers", {
    number,
    group_id: groupId,
    label,
  });

export const assignNumber = (numberId: number, groupId: number) =>
  put<PhoneNumber>(`/api/contacts/numbers/${numberId}/assign`, {
    group_id: groupId,
  });

export const deleteNumber = (numberId: number) =>
  del<{ ok: boolean }>(`/api/contacts/numbers/${numberId}`);

export const getRecent = () => get<PhoneNumber[]>("/api/contacts/recent");
