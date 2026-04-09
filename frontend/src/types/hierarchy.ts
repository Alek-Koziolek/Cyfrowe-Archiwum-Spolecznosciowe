export interface HierarchyNode {
  id: number;
  name: string;
  slug: string;
  level: string;
  parent_id: number | null;
  parent?: HierarchyNode | null;
  created_at: string;
}

export interface HierarchyNodeWithChildren extends HierarchyNode {
  children: HierarchyNode[];
}
