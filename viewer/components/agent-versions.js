import { agentVersionHistory, commitUrl } from '../services/system-card-service.js';
import { getActiveAgentName, getCard } from '../state/system-card-store.js';

const TIMELINE_ENTRY_TEMPLATE = `
  <span class="tl-dot"></span>
  <span class="tl-hash"></span>
  <a class="tl-commit" target="_blank" rel="noopener"></a>
  <p class="tl-diff"></p>
`;

export function renderAgentVersions() {
  const card = getCard();
  const timeline = document.getElementById('agent-version-timeline');
  const empty = document.getElementById('agent-version-empty');
  timeline.innerHTML = '';

  const entries = agentVersionHistory(card, getActiveAgentName());
  empty.hidden = entries.length > 0;

  for (const entry of [...entries].reverse()) {
    const li = document.createElement('li');
    li.className = 'tl-entry';
    li.innerHTML = TIMELINE_ENTRY_TEMPLATE;
    li.querySelector('.tl-hash').textContent = entry.version;

    const commitLink = li.querySelector('.tl-commit');
    commitLink.textContent = entry.commit.slice(0, 7);
    commitLink.href = commitUrl(card, entry.commit);

    li.querySelector('.tl-diff').textContent = entry.summary;
    timeline.appendChild(li);
  }
}
