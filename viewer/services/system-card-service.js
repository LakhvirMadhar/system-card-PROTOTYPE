// All data transformation lives here: raw card JSON in, view-ready shapes
// out. Components and the store never reach into entry.agent_diffs or
// schema internals directly — they call a function here instead, so that
// shape only has to be understood in one place.

export function commitUrl(card, commit) {
  return `${card.repo_url}/commit/${commit}`;
}

export function truncatedHash(hash, length = 12) {
  return hash.slice(0, length);
}

export function formatParamValue(value) {
  if (value === null || value === undefined) return '—';
  if (Array.isArray(value)) return value.length ? value.join(', ') : '—';
  return String(value);
}

export function latestVersionEntry(card) {
  return card.history[card.history.length - 1] ?? null;
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

export function pythonSignature(toolName, parameters) {
  const properties = parameters.properties ?? {};
  const defs = parameters.$defs ?? {};
  const required = new Set(parameters.required ?? []);
  const propertyNames = Object.keys(properties);

  const params = propertyNames.map((name) => {
    const schema = properties[name];
    const annotation = pythonTypeAnnotation(schema, defs);
    if (required.has(name)) return `${name}: ${annotation}`;

    const defaultValue =
      typeof schema.default === 'string' ? `"${schema.default}"` : String(schema.default);
    return `${name}: ${annotation} = ${defaultValue}`;
  });

  return `def ${toolName}(${params.join(', ')})`;
}

export function visibleSortedTools(card, { sortBy, agentFilter }) {
  let tools = card.tools;
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

export function toolVersionHistory(card, toolName) {
  const changes = [];
  for (const entry of card.history) {
    let change = null;
    for (const agentDiff of entry.agent_diffs) {
      const toolDiff = agentDiff.tool_diffs.find((d) => d.name === toolName);
      if (toolDiff) change = toolDiff.change;
    }
    if (change) {
      changes.push({ version: entry.version, commit: entry.commit, change });
    }
  }
  return changes;
}

export function guardrailVersionHistory(card, agentName, guardrailName) {
  const changes = [];
  for (const entry of card.history) {
    const agentDiff = entry.agent_diffs.find((d) => d.name === agentName);
    if (!agentDiff) continue;
    const guardrailDiff = agentDiff.guardrail_diffs.find((d) => d.name === guardrailName);
    if (guardrailDiff) {
      changes.push({ version: entry.version, commit: entry.commit, change: guardrailDiff.change });
    }
  }
  return changes;
}

export function modelVersionHistory(card, agentName) {
  const changes = [];
  for (const entry of card.history) {
    const agentDiff = entry.agent_diffs.find((d) => d.name === agentName);
    if (agentDiff?.model_changed) {
      changes.push({ version: entry.version, commit: entry.commit, change: 'changed' });
    }
  }
  return changes;
}

export function instructionVersionHistory(card, agentName) {
  const changes = [];
  for (const entry of card.history) {
    const agentDiff = entry.agent_diffs.find((d) => d.name === agentName);
    if (agentDiff?.instruction_changed) {
      changes.push({ version: entry.version, commit: entry.commit, change: 'changed' });
    }
  }
  return changes;
}

export function agentVersionHistory(card, agentName) {
  const relevant = card.history.filter((entry) =>
    entry.agent_diffs.some((d) => d.name === agentName)
  );

  return relevant.map((entry) => {
    const agentDiff = entry.agent_diffs.find((d) => d.name === agentName);
    const lines = [];

    if (agentDiff.change !== 'changed') {
      lines.push(`${agentDiff.change} agent`);
    } else {
      for (const toolDiff of agentDiff.tool_diffs) {
        lines.push(`${toolDiff.change} tool: ${toolDiff.name}`);
      }
      for (const guardrailDiff of agentDiff.guardrail_diffs) {
        lines.push(`${guardrailDiff.change} guardrail: ${guardrailDiff.name}`);
      }
      if (agentDiff.instruction_changed) lines.push('changed: system instruction');
      if (agentDiff.model_changed) lines.push('changed: model config');
    }

    return { version: entry.version, commit: entry.commit, summary: lines.join('\n') };
  });
}
