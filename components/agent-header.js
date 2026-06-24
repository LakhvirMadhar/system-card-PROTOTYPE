import { commitUrl, latestVersionEntry, truncatedHash } from '../services/system-card-service.js';
import { getActiveAgent, getCard } from '../state/system-card-store.js';

const CURRENT_VERSION_TEMPLATE = `
  <dt class="label">Current Version</dt>
  <dd class="value"></dd>
`;

export function renderHeader() {
  const card = getCard();
  const agent = getActiveAgent();
  document.getElementById('agent-title').textContent = agent.name;

  const metaRow = document.getElementById('meta-row');
  metaRow.innerHTML = '';

  const entries = [
    ['Card Hash', card.hash, truncatedHash(card.hash)],
    ['Generated At', card.generated_at, card.generated_at],
    ['Agents', null, String(card.agents.length)],
    ['Tools (this agent)', null, String(agent.tools.length)],
  ];

  for (const [label, title, value] of entries) {
    const item = document.createElement('div');
    item.className = 'meta-item';

    const dt = document.createElement('dt');
    dt.className = 'label';
    dt.textContent = label;

    const dd = document.createElement('dd');
    dd.className = label === 'Card Hash' ? 'value hash' : 'value';
    dd.textContent = value;
    if (title) dd.title = title;

    item.append(dt, dd);
    metaRow.appendChild(item);
  }

  const versionItem = document.createElement('div');
  versionItem.className = 'meta-item';
  versionItem.innerHTML = CURRENT_VERSION_TEMPLATE;
  const versionValue = versionItem.querySelector('dd');

  const latestEntry = latestVersionEntry(card);
  if (latestEntry) {
    versionValue.textContent = `${latestEntry.version} (`;
    const link = document.createElement('a');
    link.textContent = latestEntry.commit.slice(0, 7);
    link.href = commitUrl(card, latestEntry.commit);
    link.target = '_blank';
    link.rel = 'noopener';
    link.style.color = 'var(--accent)';
    versionValue.appendChild(link);
    versionValue.append(')');
  } else {
    versionValue.textContent = 'not yet recorded';
  }

  metaRow.appendChild(versionItem);
}
