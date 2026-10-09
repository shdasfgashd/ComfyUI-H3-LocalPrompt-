import { app } from '../../../scripts/app.js';
app.registerExtension({
  name: 'gensz.h3.local.preview',
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== 'H3PromptReview') return;
    const previous = nodeType.prototype.onExecuted;
    nodeType.prototype.onExecuted = function(message) {
      previous?.apply(this, arguments);
      if (!this.h3Preview) {
        this.h3Preview = document.createElement('textarea');
        this.h3Preview.readOnly = true;
        this.h3Preview.style.cssText = 'width:100%;height:100%;background:#18202a;color:#eee;font-size:12px;resize:none;';
        this.addDOMWidget('h3_preview', 'text', this.h3Preview, { serialize: false });
      }
      this.h3Preview.value = (message.text || []).join('\n\n--- ANALYSIS ---\n\n');
      this.setSize([Math.max(this.size[0], 520), Math.max(this.size[1], 500)]);
    };
  }
});
