// Holds app state and exposes plain lookups only — no transformation. Any
// "what does this mean" computation belongs in system-card-service.js, not
// here; this module just remembers what the user picked and what was last
// fetched.

let card = null;
let activeAgentName = null;
const expandedToolNames = new Set();
let toolSort = 'name';
let toolAgentFilter = '';

export function setCard(data) {
  card = data;
}

export function getCard() {
  return card;
}

export function setActiveAgentName(name) {
  activeAgentName = name;
}

export function getActiveAgentName() {
  return activeAgentName;
}

export function getActiveAgent() {
  return card.agents.find((agent) => agent.name === activeAgentName);
}

export function isToolExpanded(toolName) {
  return expandedToolNames.has(toolName);
}

export function toggleToolExpanded(toolName) {
  if (expandedToolNames.has(toolName)) {
    expandedToolNames.delete(toolName);
  } else {
    expandedToolNames.add(toolName);
  }
}

export function getToolSort() {
  return toolSort;
}

export function setToolSort(value) {
  toolSort = value;
}

export function getToolAgentFilter() {
  return toolAgentFilter;
}

export function setToolAgentFilter(value) {
  toolAgentFilter = value;
}
