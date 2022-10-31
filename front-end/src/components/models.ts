export interface Pagination {
  sortBy: string;
  descending: boolean;
  page: number;
  rowsPerPage: number;
  rowsNumber?: number;
}

export interface SearchFilter {
  title?: string;
  creator?: string;
  tags?: string[];
  frameworks?: string[];
}
