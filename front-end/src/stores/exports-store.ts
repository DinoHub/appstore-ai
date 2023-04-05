import { api } from 'src/boot/axios';
import { AxiosError } from 'axios';
import { defineStore } from 'pinia';
import { Notify } from 'quasar';

export interface Exports {
  userId: string;
  timeInitiated: string;
  models: Array<object>;
  exportLocation: string;
  timeCompleted: string;
}

export interface ExportsPaginated {
  results: Exports[];
  total_rows: number;
}

export const useExportsStore = defineStore('exports', {
  state: () => ({
    timeInitiatedRange: null as null,
    timeCompletedRange: null as null,
    idSearch: '' as string,
  }),
  actions: {
    /**
     * Retrives exports in a paginated format
     * @param pageNumber Page number to retrieve
     * @param userNumber Number of exports per page
     * @param sortBy What field to sort by
     * @param descending If the sort should be descending instead of ascending
     * @returns Promise that resolves to the list of exports and the total number of users
     */
    async getExportsPaginated(
      pageNumber: number,
      userNumber: number,
      sortBy: string,
      descending: boolean
    ): Promise<ExportsPaginated> {
      try {
        let desc;
        let sort;
        if (typeof sortBy != 'string') {
          desc = '';
          sort = '';
        } else {
          desc = `?desc=${descending}`;
          sort = `&sort=${sortBy}`;
        }
        let tempInitiatedRange = { from: '', to: '' };
        let tempCompletedRange = { from: '', to: '' };
        if (
          typeof this.timeInitiatedRange == 'object' &&
          this.timeInitiatedRange != null
        ) {
          tempInitiatedRange = Object.create(this.timeInitiatedRange);
          tempInitiatedRange.from = tempInitiatedRange.from.replaceAll(
            '/',
            '-'
          );
          tempInitiatedRange.to = tempInitiatedRange.to.replaceAll('/', '-');
          tempInitiatedRange.to = `${tempInitiatedRange.to} 24:00:00`;
        }
        if (
          typeof this.timeInitiatedRange == 'string' &&
          this.timeInitiatedRange != null
        ) {
          tempInitiatedRange = { from: '', to: '' };
          tempInitiatedRange.from = this.timeInitiatedRange.replaceAll(
            '/',
            '-'
          );
          tempInitiatedRange.to = this.timeInitiatedRange.replaceAll('/', '-');
          tempInitiatedRange.to = `${tempInitiatedRange.to} 24:00:00`;
        }
        if (
          typeof this.timeCompletedRange == 'object' &&
          this.timeCompletedRange != null
        ) {
          tempCompletedRange = Object.create(this.timeCompletedRange);
          tempCompletedRange.from = tempCompletedRange.from.replaceAll(
            '/',
            '-'
          );
          tempCompletedRange.to = tempCompletedRange.to.replaceAll('/', '-');
          tempCompletedRange.to = `${tempCompletedRange.to} 24:00:00`;
        }
        if (
          typeof this.timeCompletedRange == 'string' &&
          this.timeCompletedRange != null
        ) {
          tempCompletedRange = { from: '', to: '' };
          tempCompletedRange.from = this.timeCompletedRange.replaceAll(
            '/',
            '-'
          );
          tempCompletedRange.to = this.timeCompletedRange.replaceAll('/', '-');
          tempCompletedRange.to = `${tempCompletedRange.to} 24:00:00`;
        }

        const res = await api.post(`exports/${desc}${sort}`, {
          page_num: pageNumber,
          exports_num: userNumber,
          userId: this.idSearch,
          time_initiated_range: tempInitiatedRange,
          time_completed_range: tempCompletedRange,
        });
        const { results, total_rows }: ExportsPaginated = res.data;
        return { results, total_rows };
      } catch (error) {
        const errRes = error as AxiosError;
        Notify.create({
          message:
            'Error occurred while retrieving exports. Ensure values have been input correctly.',
          color: 'negative',
          icon: 'error',
        });
        console.error(errRes.response?.data);
        return Promise.reject('Unable to query for export logs');
      }
    },
    async removeExports(exportsList: Array<Exports>): Promise<void> {
      try {
        const removeExports = exportsList.map((a) =>
          (({ userId, timeInitiated, timeCompleted }) => ({
            userId,
            timeInitiated,
            timeCompleted,
          }))(a)
        );
        console.log(removeExports);
        await api.delete('exports/', {
          data: { logs_package: removeExports },
        });
        Notify.create({
          type: 'positive',
          message: `${removeExports.length} export(s) have been removed from database`,
        });
      } catch (err) {
        console.log(err);
        Notify.create({
          message:
            'Error occurred while removing export(s). Ensure values have been input correctly.',
          type: 'negative',
        });
      }
    },
  },
});
