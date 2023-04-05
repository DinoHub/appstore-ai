import { installQuasar } from '@quasar/quasar-app-extension-testing-unit-vitest';
import { mount } from '@vue/test-utils';
import { describe, expect, it, vi } from 'vitest';

import GradioFrame from 'src/components/content/GradioFrame.vue';

installQuasar({});

describe('', () => {
  it('Settings menu should be always visible', async () => {
    expect(GradioFrame).toBeTruthy();
    const wrapper = mount(GradioFrame, {
      props: {
        url: 'example.com',
      },
    });
    // check that it can find the settings menu
    // id=gradio-settings-menu
    expect(wrapper.find('#gradio-settings-menu')).toBeTruthy();
  });
});
