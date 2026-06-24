let SYSTEM_CARD_DATA = null;

// --- Theme toggle -----------------------------------------------------------

const THEME_STORAGE_KEY = 'system-card-theme';

function currentTheme() {
  const stored = document.documentElement.getAttribute('data-theme');
  if (stored) return stored;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem(THEME_STORAGE_KEY, theme);
  document.getElementById('theme-toggle').textContent = theme === 'dark' ? '☀' : '☾';
}

applyTheme(localStorage.getItem(THEME_STORAGE_KEY) ?? currentTheme());

document.getElementById('theme-toggle').addEventListener('click', () => {
  applyTheme(currentTheme() === 'dark' ? 'light' : 'dark');
});

let activeAgentName = null;

function activeAgent() {
  return SYSTEM_CARD_DATA.agents.find((agent) => agent.name === activeAgentName);
}

function truncatedHash(hash, length = 12) {
  return hash.slice(0, length);
}

function formatParamValue(value) {
  if (value === null || value === undefined) return '—';
  if (Array.isArray(value)) return value.length ? value.join(', ') : '—';
  return String(value);
}

const JSON_SCHEMA_TO_PYTHON_TYPE = {
  number: 'float',
  integer: 'int',
  string: 'str',
  boolean: 'bool',
  null: 'None',
};

function refName(ref) {
  return ref.split('/').pop();
}

// Recursively resolves a JSON Schema fragment (as produced by Pydantic's
// model_json_schema) into a Python type annotation string. Handles every
// shape Pydantic actually emits: $ref/$defs (nested models — shown by class
// name, not expanded), anyOf (unions, including Optional via a null variant),
// enum (-> Literal[...]), array (-> list[...]), and plain primitives.
function pythonTypeAnnotation(schema, defs) {
  if (schema.$ref) {
    return refName(schema.$ref);
  }

  if (schema.anyOf) {
    const variants = schema.anyOf.map((variant) => pythonTypeAnnotation(variant, defs));
    const nonNullVariants = variants.filter((variant) => variant !== 'None');
    if (nonNullVariants.length === variants.length - 1) {
      return `${nonNullVariants.join(' | ')} | None`;
    }
    return variants.join(' | ');
  }

  if (schema.enum) {
    const literalValues = schema.enum
      .map((value) => (typeof value === 'string' ? `"${value}"` : String(value)))
      .join(', ');
    return `Literal[${literalValues}]`;
  }

  if (schema.type === 'array') {
    return `list[${schema.items ? pythonTypeAnnotation(schema.items, defs) : 'object'}]`;
  }

  if (schema.type === 'object') {
    return 'dict';
  }

  return JSON_SCHEMA_TO_PYTHON_TYPE[schema.type] ?? schema.type ?? 'object';
}

function pythonSignature(toolName, parameters) {
  const properties = parameters.properties ?? {};
  const defs = parameters.$defs ?? {};
  const required = new Set(parameters.required ?? []);
  const propertyNames = Object.keys(properties);

  const params = propertyNames.map((name) => {
    const schema = properties[name];
    const annotation = pythonTypeAnnotation(schema, defs);
    if (required.has(name)) return `${name}: ${annotation}`;

    const defaultValue = typeof schema.default === 'string' ? `"${schema.default}"` : String(schema.default);
    return `${name}: ${annotation} = ${defaultValue}`;
  });

  return `def ${toolName}(${params.join(', ')})`;
}

// --- View switching -------------------------------------------------------

const views = ['home', 'tools', 'agents', 'agent-detail'];

function showView(view) {
  for (const v of views) {
    document.getElementById('view-' + v).hidden = v !== view;
  }
  document.getElementById('nav-home').classList.toggle('active', view === 'home');
  document.getElementById('nav-tools').classList.toggle('active', view === 'tools');
  document.getElementById('nav-agents').classList.toggle('active', view === 'agents' || view === 'agent-detail');
}

function showAgentDetail(agentName) {
  activeAgentName = agentName;
  showView('agent-detail');
  renderHeader();
  renderOverview();
  renderModelParams();
  renderInstruction();
  renderAgentVersions();
}

document.getElementById('nav-home').addEventListener('click', () => showView('home'));
document.getElementById('nav-tools').addEventListener('click', () => showView('tools'));
document.getElementById('nav-agents').addEventListener('click', () => showView('agents'));
document.getElementById('back-to-agents').addEventListener('click', () => showView('agents'));

// --- Tools view (flat registry, independent of any one agent) ------------

const expandedToolNames = new Set();

function populateToolAgentFilter() {
  const select = document.getElementById('tool-agent-filter');
  for (const agent of SYSTEM_CARD_DATA.agents) {
    const option = document.createElement('option');
    option.value = agent.name;
    option.textContent = agent.name;
    select.appendChild(option);
  }
}

function visibleSortedTools() {
  const sortBy = document.getElementById('tool-sort').value;
  const agentFilter = document.getElementById('tool-agent-filter').value;

  let tools = SYSTEM_CARD_DATA.tools;
  if (agentFilter) {
    tools = tools.filter((tool) => tool.used_by.includes(agentFilter));
  }

  tools = [...tools];
  if (sortBy === 'used-by-count') {
    tools.sort((a, b) => b.used_by.length - a.used_by.length || a.name.localeCompare(b.name));
  } else {
    tools.sort((a, b) => a.name.localeCompare(b.name));
  }

  return tools;
}

function renderToolRegistry() {
  const list = document.getElementById('tool-registry-list');
  list.innerHTML = '';

  for (const tool of visibleSortedTools()) {
    const isExpanded = expandedToolNames.has(tool.name);

    const article = document.createElement('article');
    article.className = 'tool-detail';
    article.innerHTML = `
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

    article.querySelector('.tool-detail-name').textContent = tool.name;
    article.querySelector('.tool-detail-signature').textContent =
      pythonSignature(tool.name, tool.parameters);
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

    const versionsCell = article.querySelector('.tool-detail-versions');
    const versions = toolVersionHistory(tool.name);
    if (versions.length === 0) {
      const none = document.createElement('em');
      none.className = 'no-params';
      none.textContent = 'no recorded versions yet';
      versionsCell.appendChild(none);
    } else {
      const ul = document.createElement('ul');
      ul.className = 'tool-version-history';
      for (const line of [...versions].reverse()) {
        const li = document.createElement('li');
        li.textContent = line;
        ul.appendChild(li);
      }
      versionsCell.appendChild(ul);
    }

    const chevron = article.querySelector('.tool-detail-chevron');
    const body = article.querySelector('.detail-list');
    chevron.textContent = isExpanded ? '▾' : '▸';
    body.hidden = !isExpanded;

    article.querySelector('.tool-detail-head').addEventListener('click', () => {
      if (expandedToolNames.has(tool.name)) {
        expandedToolNames.delete(tool.name);
      } else {
        expandedToolNames.add(tool.name);
      }
      renderToolRegistry();
    });

    list.appendChild(article);
  }
}

document.getElementById('tool-sort').addEventListener('change', renderToolRegistry);
document.getElementById('tool-agent-filter').addEventListener('change', renderToolRegistry);

// --- Agents view (picker) --------------------------------------------------

function renderAgentList() {
  const list = document.getElementById('agent-list');
  list.innerHTML = '';

  for (const agent of SYSTEM_CARD_DATA.agents) {
    const card = document.createElement('article');
    card.className = 'home-agent-card';
    card.innerHTML = `
      <span class="home-agent-name"></span>
      <p class="home-agent-summary"></p>
      <p class="home-agent-meta"></p>
    `;
    card.querySelector('.home-agent-name').textContent = agent.name;
    card.querySelector('.home-agent-summary').textContent = agent.instruction.split('\n\n')[0];
    card.querySelector('.home-agent-meta').textContent =
      `${agent.tools.length} tool(s) · ${agent.model.provider}/${agent.model.model_name}`;
    card.addEventListener('click', () => showAgentDetail(agent.name));
    list.appendChild(card);
  }
}

// --- Agent detail view ------------------------------------------------------

function renderHeader() {
  const agent = activeAgent();
  document.getElementById('agent-title').textContent = agent.name;

  const metaRow = document.getElementById('meta-row');
  metaRow.innerHTML = '';

  const entries = [
    ['Card Hash', SYSTEM_CARD_DATA.hash, truncatedHash(SYSTEM_CARD_DATA.hash)],
    ['Generated At', SYSTEM_CARD_DATA.generated_at, SYSTEM_CARD_DATA.generated_at],
    ['Agents', null, String(SYSTEM_CARD_DATA.agents.length)],
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
}

function renderOverview() {
  const agent = activeAgent();
  const list = document.getElementById('tool-list');
  list.innerHTML = '';

  for (const tool of agent.tools) {
    const summary = tool.description.split('\n\n')[0];

    const article = document.createElement('article');
    article.className = 'tool';
    article.innerHTML = `
      <span class="tool-name"></span>
      <p class="tool-desc"></p>
    `;
    article.querySelector('.tool-name').textContent = tool.name;
    article.querySelector('.tool-desc').textContent = summary;
    list.appendChild(article);
  }
}

function renderModelParams() {
  const agent = activeAgent();
  const list = document.getElementById('model-params');
  list.innerHTML = '';

  const fields = [
    ['Provider', formatParamValue(agent.model.provider)],
    ['Model', formatParamValue(agent.model.model_name)],
    ['Model Digest', truncatedHash(agent.model.model_digest ?? '', 16)],
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
    row.innerHTML = '<dt></dt><dd></dd>';
    row.querySelector('dt').textContent = label;
    row.querySelector('dd').textContent = value;
    list.appendChild(row);
  }
}

function renderInstruction() {
  const agent = activeAgent();
  document.getElementById('instruction-block').textContent = agent.instruction;
}

function renderAgentVersions() {
  const agentName = activeAgentName;
  const timeline = document.getElementById('agent-version-timeline');
  const empty = document.getElementById('agent-version-empty');
  timeline.innerHTML = '';

  const relevant = SYSTEM_CARD_DATA.history.filter((entry) =>
    entry.agent_diffs.some((d) => d.name === agentName)
  );

  empty.hidden = relevant.length > 0;

  for (const entry of [...relevant].reverse()) {
    const agentDiff = entry.agent_diffs.find((d) => d.name === agentName);
    const lines = [];
    if (agentDiff.change !== 'changed') {
      lines.push(`${agentDiff.change} agent`);
    } else {
      for (const toolDiff of agentDiff.tool_diffs) {
        lines.push(`${toolDiff.change} tool: ${toolDiff.name}`);
      }
      if (agentDiff.instruction_changed) lines.push('changed: system instruction');
      if (agentDiff.model_changed) lines.push('changed: model config');
    }

    const li = document.createElement('li');
    li.className = 'tl-entry';
    li.innerHTML = `
      <span class="tl-dot"></span>
      <span class="tl-hash"></span>
      <p class="tl-diff"></p>
    `;
    li.querySelector('.tl-hash').textContent = entry.version;
    li.querySelector('.tl-diff').textContent = lines.join('\n');
    timeline.appendChild(li);
  }
}

function toolVersionHistory(toolName) {
  const changes = [];
  for (const entry of SYSTEM_CARD_DATA.history) {
    let change = null;
    for (const agentDiff of entry.agent_diffs) {
      const toolDiff = agentDiff.tool_diffs.find((d) => d.name === toolName);
      if (toolDiff) change = toolDiff.change;
    }
    if (change) changes.push(`${entry.version}: ${change}`);
  }
  return changes;
}

document.querySelectorAll('.section-nav button').forEach((btn) => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.section-nav button').forEach((b) => b.classList.remove('active'));
    document.querySelectorAll('#view-agent-detail .panel').forEach((p) => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('panel-' + btn.dataset.panel).classList.add('active');
  });
});

fetch('system_card_data.json')
  .then((response) => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  })
  .then((data) => {
    SYSTEM_CARD_DATA = data;
    populateToolAgentFilter();
    renderToolRegistry();
    renderAgentList();
  })
  .catch(() => {
    document.getElementById('data-load-error').hidden = false;
  });
