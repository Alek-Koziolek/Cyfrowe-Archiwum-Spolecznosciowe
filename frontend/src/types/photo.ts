import type { HierarchyNode } from './hierarchy';
import type { User } from './user';

export interface Photo {
  id: number;
  title: string;
  description: string | null;
  owner: User;
  hierarchy_node: HierarchyNode | null;
  mime_type: string;
  file_size: number;
  width: number | null;
  height: number | null;
  date_taken: string | null;
  date_precision: 'year' | 'month' | 'day' | null;
  location_text: string | null;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface PhotoListResponse {
  items: Photo[];
  total: number;
  page: number;
  per_page: number;
}
