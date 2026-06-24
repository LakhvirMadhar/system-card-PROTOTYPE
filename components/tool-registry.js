import {
  pythonSignature,
  toolVersionHistory,
  visibleSortedTools,
} from '../services/system-card-service.js';
import {
  getCard,
  getToolAgentFilter,
  getToolSort,
  isToolExpanded,
  setToolAgentFilter,
  setToolSort,
  toggleToolExpanded,
} from '../state/system-card-store.js';
import { renderVersionHistoryList } from './version-history-list.js';

const CHEVRON_EXPANDED = '▾';
const CHEVRON_COLLAPSED = '▸';

const TOOL_DETAIL_TEMPLATE = `
  <button class="tool-detail-head" type="button">
    <span class="tool-detail-chevron"></span>
    <span class="tool-detail-heading">
      <span class="tool-detail-name"></span>
      <span class="tool-detail-signature"></span>
    </span>
  </button>
  <dl class="detail-list" hidden>
    <div class="detail-row">
      <dt>Description</dt>
      <dd class="tool-detail-description"></dd>
    </div>
    <div class="detail-row">
      <dt>Used By</dt>
      <dd class="tool-detail-used-by"></dd>
    </div>
    <div class="detail-row">
      <dt>Version History</dt>
      <dd class="tool-detail-versions"></dd>
    </div>
  </dl>
`;

export function populateToolAgentFilter() {
  const card = getCard();
  const select = document.getElementById('tool-agent-filter');
  for (const agent of card.agents) {
    const option = document.createElement('option');
    option.value = agent.name;
    option.textContent = agent.name;
    select.appendChild(option);
  }
}

export function renderToolRegistry() {
  const card = getCard();
  const list = document.getElementById('tool-registry-list');
  list.innerHTML = '';

  const tools = visibleSortedTools(card, {
    sortBy: getToolSort(),
    agentFilter: getToolAgentFilter(),
  });

  for (const tool of tools) {
    const isExpanded = isToolExpanded(tool.name);

    const article = document.createElement('article');
    article.className = 'tool-detail';
    article.innerHTML = TOOL_DETAIL_TEMPLATE;

    article.querySelector('.tool-detail-name').textContent = tool.name;
    article.querySelector('.tool-detail-signature').textContent = pythonSignature(
      tool.name,
      tool.parameters
    );
    article.querySelector('.tool-detail-description').textContent = tool.description;

    const usedByCell = article.querySelector('.tool-detail-used-by');
    if (tool.used_by.length === 0) {
      const none = document.createElement('em');
      none.className = 'no-params';
      none.textContent = 'no agent currently uses this tool';
      usedByCell.appendChild(none);
    } else {
      usedByCell.textContent = tool.used_by.join(', ');
    }

    renderVersionHistoryList(
      card,
      article.querySelector('.tool-detail-versions'),
      toolVersionHistory(card, tool.name)
    );

    const chevron = article.querySelector('.tool-detail-chevron');
    const body = article.querySelector('.detail-list');
    chevron.textContent = isExpanded ? CHEVRON_EXPANDED : CHEVRON_COLLAPSED;
    body.hidden = !isExpanded;

    article.querySelector('.tool-detail-head').addEventListener('click', () => {
      toggleToolExpanded(tool.name);
      renderToolRegistry();
    });

    list.appendChild(article);
  }
}

export function initToolRegistryControls() {
  document.getElementById('tool-sort').addEventListener('change', (event) => {
    setToolSort(event.target.value);
    renderToolRegistry();
  });
  document.getElementById('tool-agent-filter').addEventListener('change', (event) => {
    setToolAgentFilter(event.target.value);
    renderToolRegistry();
  });
}
