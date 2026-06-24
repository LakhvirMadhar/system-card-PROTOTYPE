import { fetchSystemCard } from './services/system-card-api.js';
import { setActiveAgentName, setCard } from './state/system-card-store.js';
import { initThemeToggle } from './components/theme-toggle.js';
import { initToolRegistryControls, populateToolAgentFilter, renderToolRegistry } from './components/tool-registry.js';
import { renderAgentList } from './components/agent-list.js';
import { renderHeader } from './components/agent-header.js';
import { renderOverview } from './components/agent-overview.js';
import { renderModelParams } from './components/agent-model-params.js';
import { renderInstruction } from './components/agent-instruction.js';
import { renderGuardrails } from './components/agent-guardrails.js';
import { renderAgentVersions } from './components/agent-versions.js';

const views = ['home', 'tools', 'agents', 'agent-detail'];

function showView(view) {
  for (const v of views) {
    document.getElementById('view-' + v).hidden = v !== view;
  }
  document.getElementById('nav-home').classList.toggle('active', view === 'home');
  document.getElementById('nav-tools').classList.toggle('active', view === 'tools');
  document
    .getElementById('nav-agents')
    .classList.toggle('active', view === 'agents' || view === 'agent-detail');
}

function showAgentDetail(agentName) {
  setActiveAgentName(agentName);
  showView('agent-detail');
  renderHeader();
  renderOverview();
  renderModelParams();
  renderInstruction();
  renderGuardrails();
  renderAgentVersions();
}

function initNav() {
  document.getElementById('nav-home').addEventListener('click', () => showView('home'));
  document.getElementById('nav-tools').addEventListener('click', () => showView('tools'));
  document.getElementById('nav-agents').addEventListener('click', () => showView('agents'));
  document.getElementById('back-to-agents').addEventListener('click', () => showView('agents'));

  document.querySelectorAll('.section-nav button').forEach((btn) => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.section-nav button').forEach((b) => b.classList.remove('active'));
      document.querySelectorAll('#view-agent-detail .panel').forEach((p) => p.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById('panel-' + btn.dataset.panel).classList.add('active');
    });
  });
}

initThemeToggle();
initNav();
initToolRegistryControls();

fetchSystemCard()
  .then((data) => {
    setCard(data);
    populateToolAgentFilter();
    renderToolRegistry();
    renderAgentList(showAgentDetail);
  })
  .catch(() => {
    document.getElementById('data-load-error').hidden = false;
  });
