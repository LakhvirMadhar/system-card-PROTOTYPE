// The only module allowed to call fetch(). Returns the raw JSON exactly as
// generate_card_viewer_data.py wrote it — no shaping, no defaults. Shaping
// that data into view-ready shapes is system-card-service.js's job.

export async function fetchSystemCard() {
  const response = await fetch('system_card_data.json');
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}
