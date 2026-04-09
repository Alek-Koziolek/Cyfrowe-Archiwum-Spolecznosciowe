import api from './client';
import type { User } from '../types/user';
import type { Photo } from '../types/photo';

export async function listUsers(): Promise<User[]> {
  const response = await api.get<User[]>('/admin/users');
  return response.data;
}

export async function toggleBlockUser(userId: number): Promise<User> {
  const response = await api.put<User>(`/admin/users/${userId}/block`);
  return response.data;
}

export async function adminDeletePhoto(photoId: number): Promise<void> {
  await api.delete(`/admin/photos/${photoId}`);
}

export async function adminUpdatePhoto(
  photoId: number,
  data: Record<string, unknown>,
): Promise<Photo> {
  const response = await api.put<Photo>(`/admin/photos/${photoId}`, data);
  return response.data;
}

export async function deleteHierarchyNode(nodeId: number): Promise<void> {
  await api.delete(`/admin/hierarchy/${nodeId}`);
}

export async function getStats(): Promise<{
  total_users: number;
  total_photos: number;
  blocked_users: number;
}> {
  const response = await api.get('/admin/stats');
  return response.data;
}
