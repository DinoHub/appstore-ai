import { api } from 'src/boot/axios';
import { defineStore } from 'pinia';
import { Notify } from 'quasar';

export interface AccessControl {
    newUsernamesList: string[];
    validUsernames: string[];
    invalidUsernames: string[];
  }

export const useAccessControlStore = defineStore('access-control', {
  state: () => ({
    enableModelAccessOptions: [
      {
        label: 'No',
        value: false,
      },
      {
        label: 'Yes',
        value: true
      }
    ],
    previousUsernamesList: [] as string[]
  }),

  actions: {
    /**
     * Validate list of usernames with keycloak
     * @param usernamesList list of usernames to validate
     * @param connector Experiment connector to use
     * @param returnPlots Whether to return plots or not
     * @param returnArtifacts Whether to return artifacts or not
     * @returns Experiment data
     */
    async validateUsernamesWithKeycloak(
        usernamesList: string[]
    ): Promise<AccessControl> {
        try {
            const res = await api.post(`access-control/`, usernamesList)
            const data: AccessControl = res.data
            if (data.invalidUsernames.length){
                const invalidUsernamesString: string = data.invalidUsernames.join(', ')
                Notify.create({
                    message: `Usernames: ${invalidUsernamesString} not found`,
                    type: 'negative',
                    timeout: 5000
                });
                }
            if (data.validUsernames.length){
                const validUsernamesString: string = data.validUsernames.join(', ')
                Notify.create({
                    message: `Usernames: ${validUsernamesString} found`,
                    type: 'positive',
                    timeout: 5000
                });
            }
            return data
        } catch (error) {
            return Promise.reject('Unable to validate')
        }
    }
  },
});
