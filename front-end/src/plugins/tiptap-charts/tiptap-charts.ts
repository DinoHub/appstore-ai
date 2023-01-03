import ChartDisplay from 'src/components/editor/TiptapChart.vue';
import { mergeAttributes, Node } from '@tiptap/core';
import { VueNodeViewRenderer } from '@tiptap/vue-3';

export interface ChartOptions {
  layout: Record<string, any>;
  data: Record<string, any>[];
  HTMLAttributes: Record<string, any>;
}

export const Chart = Node.create<ChartOptions>({
  name: 'chart',
  addOptions() {
    return {
      HTMLAttributes: {},
      layout: {},
      data: [],
    };
  },

  atom: true,
  group: 'block',
  addAttributes() {
    return {
      layout: {
        default: {},
        parseHTML: (el) => el.getAttribute('data-layout'),
        renderHTML: (attr) => {
          return {
            'data-layout': attr.layout,
          };
        },
      },
      data: {
        default: [
          {
            x: [],
            y: [],
            type: 'lines',
          },
        ],
        parseHTML: (el) => el.getAttribute('data-data'),
        renderHTML: (attr) => {
          return {
            'data-data': attr.data,
          };
        },
      },
    };
  },
  parseHTML() {
    return [
      {
        tag: 'chart',
      },
    ];
  },
  renderHTML({ HTMLAttributes }) {
    return ['chart', mergeAttributes(HTMLAttributes)];
  },
  addNodeView() {
    return VueNodeViewRenderer(ChartDisplay);
  },
});
