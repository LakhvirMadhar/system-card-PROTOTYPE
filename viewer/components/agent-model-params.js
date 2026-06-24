import { formatParamValue, modelVersionHistory, truncatedHash } from '../services/system-card-service.js';
import { getActiveAgentName, getCard, getActiveAgent } from '../state/system-card-store.js';
import { renderVersionHistoryList } from './version-history-list.js';

// Longer than truncatedHash's default 12 — digests need more characters
// shown to stay distinguishable from each other than the card hash does.
const MODEL_DIGEST_DISPLAY_LENGTH = 16;

const DETAIL_ROW_TEMPLATE = '<dt></dt><dd></dd>';

export function renderModelParams() {
  const card = getCard();
  const agent = getActiveAgent();
  const list = document.getElementById('model-params');
  list.innerHTML = '';

  const fields = [
    ['Provider', formatParamValue(agent.model.provider)],
    ['Model', formatParamValue(agent.model.model_name)],
    ['Model Digest', truncatedHash(agent.model.model_digest ?? '', MODEL_DIGEST_DISPLAY_LENGTH)],
    ['Temperature', formatParamValue(agent.model.temperature)],
    ['Top P', formatParamValue(agent.model.top_p)],
    ['Top K', formatParamValue(agent.model.top_k)],
    ['Seed', formatParamValue(agent.model.seed)],
    ['Presence Penalty', formatParamValue(agent.model.presence_penalty)],
    ['Frequency Penalty', formatParamValue(agent.model.frequency_penalty)],
    ['Stop Sequences', formatParamValue(agent.model.stop_sequences)],
    ['Max Output Tokens', formatParamValue(agent.model.max_output_tokens)],
  ];

  for (const [label, value] of fields) {
    const row = document.createElement('div');
    row.className = 'detail-row';
    row.innerHTML = DETAIL_ROW_TEMPLATE;
    row.querySelector('dt').textContent = label;
    row.querySelector('dd').textContent = value;
    list.appendChild(row);
  }

  renderVersionHistoryList(
    card,
    document.getElementById('model-version-history'),
    modelVersionHistory(card, getActiveAgentName())
  );
}
