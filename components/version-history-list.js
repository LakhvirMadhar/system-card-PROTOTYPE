// Shared by every "Version History" row (tools, model params, instruction,
// guardrails) — renders a list of {version, commit, change} entries already
// produced by system-card-service.js. Pure DOM construction, no data lookup.

import { commitUrl } from '../services/system-card-service.js';

const VERSION_ENTRY_TEMPLATE = '<span></span> <a target="_blank" rel="noopener"></a>';

export function renderVersionHistoryList(card, container, changes) {
  container.innerHTML = '';

  if (changes.length === 0) {
    const none = document.createElement('em');
    none.className = 'no-params';
    none.textContent = 'no recorded versions yet';
    container.appendChild(none);
    return;
  }

  const ul = document.createElement('ul');
  ul.className = 'tool-version-history';
  for (const entry of [...changes].reverse()) {
    const li = document.createElement('li');
    li.innerHTML = VERSION_ENTRY_TEMPLATE;
    li.querySelector('span').textContent = `${entry.version}: ${entry.change}`;
    const link = li.querySelector('a');
    link.textContent = entry.commit.slice(0, 7);
    link.href = commitUrl(card, entry.commit);
    ul.appendChild(li);
  }
  container.appendChild(ul);
}
