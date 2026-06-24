import { instructionVersionHistory } from '../services/system-card-service.js';
import { getActiveAgent, getActiveAgentName, getCard } from '../state/system-card-store.js';
import { renderVersionHistoryList } from './version-history-list.js';

export function renderInstruction() {
  const card = getCard();
  const agent = getActiveAgent();
  document.getElementById('instruction-block').textContent = agent.instruction;

  renderVersionHistoryList(
    card,
    document.getElementById('instruction-version-history'),
    instructionVersionHistory(card, getActiveAgentName())
  );
}
