import { Notify } from 'quasar';
import { boot } from 'quasar/wrappers';

// "async" is optional;
// more info on params: https://v2.quasar.dev/quasar-cli/boot-files
export default boot(async (/* { app, router, ... } */) => {
  // something to do
  Notify.setDefaults({
    position: 'top-right',
    timeout: 2500,
    actions: [{ icon: 'close', color: 'white' }],
  });
});
