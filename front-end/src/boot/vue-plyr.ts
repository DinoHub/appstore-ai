import { boot } from 'quasar/wrappers';
import VuePlyr from 'vue-plyr';
import 'vue-plyr/dist/vue-plyr.css';
import plyr from '../assets/plyr_sprites.svg';

export default boot(({ app }) => {
  app.use(VuePlyr, {
    plyr: { iconUrl: plyr },
  });
});
