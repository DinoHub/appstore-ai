import { LocationQueryValue } from 'vue-router';

export interface Breadcrumb {
  label: string;
  to: string;
}

export interface SortOption {
  label: string;
  value: string;
  desc: boolean;
}
export interface Pagination {
  sortBy: SortOption;
  descending: boolean;
  page: number;
  rowsPerPage: number;
  rowsNumber?: number;
}

export interface SearchFilter {
  title?: string;
  genericSearchText?: string;
  creator?: string;
  creatorUserIdPartial?: string;
  tasks?: string[] | LocationQueryValue[];
  tags?: string[] | LocationQueryValue[];
  frameworks?: string[] | LocationQueryValue[];
}

export interface UsersSearchFilter {
  name?: string;
  userId?: string;
  privilege?: number;
  dateCreatedRange?: string[];
  dateModifiedRange?: string[];
}

export interface ExportsSearchFilter {
  userId?: string;
  timeInitiatedRange?: string[];
  timeCompletedRange?: string[];
}

export interface FormOptionValue {
  label: string;
  value: string;
}

export interface Chart {
  id?: string;
  data: {
    [key: string]: any;
  }[];
  layout: {
    [key: string]: any;
  };
}

export interface EnvField {
  key: string;
  value: string;
}
