import api from './client';
import type { Photo, PhotoListResponse } from '../types/photo';

export async function listMyPhotos(
  page = 1,
  perPage = 20,
): Promise<PhotoListResponse> {
  const response = await api.get<PhotoListResponse>('/photos/mine', {
    params: { page, per_page: perPage },
  });
  return response.data;
}

export async function listPhotos(
  page = 1,
  perPage = 20,
): Promise<PhotoListResponse> {
  const response = await api.get<PhotoListResponse>('/photos/', {
    params: { page, per_page: perPage },
  });
  return response.data;
}

export async function getPhoto(id: number): Promise<Photo> {
  const response = await api.get<Photo>(`/photos/${id}`);
  return response.data;
}

export async function uploadPhoto(formData: FormData): Promise<Photo> {
  const response = await api.post<Photo>('/photos/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export async function updatePhoto(
  id: number,
  data: Record<string, unknown>,
): Promise<Photo> {
  const response = await api.put<Photo>(`/photos/${id}`, data);
  return response.data;
}

export async function deletePhoto(id: number): Promise<void> {
  await api.delete(`/photos/${id}`);
}

export function thumbnailUrl(id: number): string {
  return `/api/photos/${id}/thumbnail`;
}

export function fullImageUrl(id: number): string {
  return `/api/photos/${id}/full`;
}
