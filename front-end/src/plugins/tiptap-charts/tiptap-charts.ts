/**
 * Plotly chart extension for tiptap
 * Enables plotly json chart data to
 * be rendered in tiptap editor
 */
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
        // layout JSON is stored as a string attribute in the HTML
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
        // data JSON is stored as a string attribute in the HTML
        // NOTE: this will cause the HTML to be very large if there are many data points
        // but I have not found a better way to store the data conveniently
        renderHTML: (attr) => {
          return {
            'data-data': attr.data,
          };
        },
      },
    };
  },
  // Note that `chart` is a custom tag that is not a valid HTML tag
  // Currently in the backend, I whitelist this tag to ensure the
  // lxml parser does not strip it out, but this is not ideal
  // TODO: Consider using a valid HTML tag to avoid HTML parsers
  // from stripping out the tag
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
    // Render as vue component
    return VueNodeViewRenderer(ChartDisplay);
  },
});
