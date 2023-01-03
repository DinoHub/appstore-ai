import { boot } from 'quasar/wrappers';
import VuePlyr from 'vue-plyr';
import 'vue-plyr/dist/vue-plyr.css';

export default boot(({ app }) => {
  app.use(VuePlyr, {
    plyr: {},
  });
});
