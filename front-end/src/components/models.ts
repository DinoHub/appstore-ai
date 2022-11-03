import { LocationQueryValue } from 'vue-router';

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
  tasks?: string[] | LocationQueryValue[];
  tags?: string[] | LocationQueryValue[];
  frameworks?: string[] | LocationQueryValue[];
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
