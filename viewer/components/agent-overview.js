import { getActiveAgent } from '../state/system-card-store.js';

const TOOL_SUMMARY_TEMPLATE = `
  <span class="tool-name"></span>
  <p class="tool-desc"></p>
`;

export function renderOverview() {
  const agent = getActiveAgent();
  const list = document.getElementById('tool-list');
  list.innerHTML = '';

  for (const tool of agent.tools) {
    const summary = tool.description.split('\n\n')[0];

    const article = document.createElement('article');
    article.className = 'tool';
    article.innerHTML = TOOL_SUMMARY_TEMPLATE;
    article.querySelector('.tool-name').textContent = tool.name;
    article.querySelector('.tool-desc').textContent = summary;
    list.appendChild(article);
  }
}
