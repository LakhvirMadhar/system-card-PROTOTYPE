import { getCard } from '../state/system-card-store.js';

const AGENT_CARD_TEMPLATE = `
  <span class="home-agent-name"></span>
  <p class="home-agent-summary"></p>
  <p class="home-agent-meta"></p>
`;

export function renderAgentList(onSelect) {
  const card = getCard();
  const list = document.getElementById('agent-list');
  list.innerHTML = '';

  for (const agent of card.agents) {
    const item = document.createElement('article');
    item.className = 'home-agent-card';
    item.innerHTML = AGENT_CARD_TEMPLATE;
    item.querySelector('.home-agent-name').textContent = agent.name;
    item.querySelector('.home-agent-summary').textContent = agent.instruction.split('\n\n')[0];
    item.querySelector('.home-agent-meta').textContent =
      `${agent.tools.length} tool(s) · ${agent.model.provider}/${agent.model.model_name}`;
    item.addEventListener('click', () => onSelect(agent.name));
    list.appendChild(item);
  }
}
