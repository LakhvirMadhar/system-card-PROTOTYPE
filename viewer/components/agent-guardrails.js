import { guardrailVersionHistory } from '../services/system-card-service.js';
import { getActiveAgent, getActiveAgentName, getCard } from '../state/system-card-store.js';
import { renderVersionHistoryList } from './version-history-list.js';

const GUARDRAIL_CARD_TEMPLATE = `
  <header class="tool-detail-head" style="cursor: default;">
    <span class="tool-detail-heading">
      <span class="tool-detail-name"></span>
    </span>
  </header>
  <dl class="detail-list">
    <div class="detail-row">
      <dt>Trigger Keywords</dt>
      <dd class="guardrail-keywords"></dd>
    </div>
    <div class="detail-row">
      <dt>Classifier Instruction</dt>
      <dd class="guardrail-classifier"></dd>
    </div>
    <div class="detail-row">
      <dt>Injected Instruction</dt>
      <dd class="guardrail-injected"></dd>
    </div>
    <div class="detail-row">
      <dt>Version History</dt>
      <dd class="guardrail-versions"></dd>
    </div>
  </dl>
`;

export function renderGuardrails() {
  const card = getCard();
  const agentName = getActiveAgentName();
  const agent = getActiveAgent();
  const list = document.getElementById('guardrail-list');
  const empty = document.getElementById('guardrail-empty');
  list.innerHTML = '';

  empty.hidden = agent.guardrails.length > 0;

  for (const guardrail of agent.guardrails) {
    const article = document.createElement('article');
    article.className = 'tool-detail';
    article.innerHTML = GUARDRAIL_CARD_TEMPLATE;

    article.querySelector('.tool-detail-name').textContent = guardrail.name;

    const keywordsCell = article.querySelector('.guardrail-keywords');
    for (const keyword of guardrail.trigger_keywords) {
      const pill = document.createElement('span');
      pill.className = 'param-pill';
      pill.textContent = keyword;
      keywordsCell.appendChild(pill);
    }

    article.querySelector('.guardrail-classifier').textContent = guardrail.classifier_instruction;
    article.querySelector('.guardrail-injected').textContent = guardrail.injected_instruction;

    renderVersionHistoryList(
      card,
      article.querySelector('.guardrail-versions'),
      guardrailVersionHistory(card, agentName, guardrail.name)
    );

    list.appendChild(article);
  }
}
