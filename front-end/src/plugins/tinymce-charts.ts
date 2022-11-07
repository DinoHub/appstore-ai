import contentCss from 'tinymce/skins/content/default/content.css';
import contentUiCss from 'tinymce/skins/ui/oxide/content.css';
import tinymce from 'tinymce';

tinymce.PluginManager.add('plotly', (editor, url) => {
  const openDialog = () => {
    return editor.windowManager.open({
      title: 'Create Plotly Chart',
      body: {
        type: 'tabpanel',
        tabs: [
          {
            title: 'Define Chart Data',
            name: 'dataTab',
            items: [
              {
                type: 'input',
                name: 'title',
                label: 'Title',
              },
              {
                type: 'selectbox',
                name: 'chartType',
                label: 'Chart Type',
                items: [
                  { value: 'line+marker', text: 'Line' },
                  { value: 'marker', text: 'Scatter' },
                ],
              },
              {
                type: 'input',
                name: 'xLabel',
                label: 'X Axis Label',
              },
              {
                type: 'input',
                name: 'yLabel',
                label: 'Y Axis Label',
              },
              {
                type: 'textarea',
                name: 'data',
                label: 'Data',
              },
              {
                type: 'iframe',
                name: 'codePreview',
                label: 'Code Preview',
              },
            ],
          },
          {
            title: 'Preview',
            name: 'previewTab',
            items: [
              {
                type: 'iframe',
                name: 'preview',
                label: 'Graph Preview',
                sandboxed: true,
                transparent: true,
              },
            ],
          },
        ],
      },
      buttons: [
        {
          type: 'cancel',
          text: 'Close',
        },
        {
          type: 'submit',
          text: 'Save',
          primary: true,
        },
      ],
      initialData: {
        preview: 'No preview available',
      },
      onChange: (api, details) => {
        const data = api.getData();
        try {
          const plotData = JSON.parse(data.data ?? '[]');
          plotData.map((trace) => {
            trace.mode = data.chartType;
          });
          const plotDataString = JSON.stringify(plotData);
          const layout = `{
              title: '${data.title}',
              xaxis: {
                title: '${data.xLabel}'
              },
              yaxis: {
                title: '${data.yLabel}'
              }
            }`;
          const plotJSON = `{ 'data' : ${plotDataString}, 'layout' : ${layout} }`;
          console.log(details);
          console.log(data);
          const graph = `
            <script src="https://cdn.plot.ly/plotly-2.16.1.min.js"></script>
            <div id="preview"></div>
            <script>
            chart = document.getElementById('preview');
            Plotly.newPlot( chart, ${plotDataString},  ${layout});
          </script>
          `;
          api.setData({
            preview: graph,
            codePreview: `${plotJSON}`,
          });
        } catch (error) {
          console.log(error);
        }
      },
      onSubmit: (api) => {
        const data = api.getData();
        editor.insertContent(
          '```chart ' + data.codePreview.replace(/\n/g, ' ') + '```',
        );
        api.close();
      },
    });
  };

  editor.ui.registry.addButton('plotly', {
    text: 'Plotly Graph',
    onAction: () => {
      openDialog();
    },
  });
  return {
    getMetadata: () => {
      return {
        name: 'Plotly Editor',
        url: '',
      };
    },
  };
});
