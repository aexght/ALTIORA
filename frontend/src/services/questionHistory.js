/**
 * Recent-question history for anti-repetition.
 *
 * The assessment selection engine prefers questions that were NOT used in the
 * user's recent previous assessments. We track that history here, stored under
 * its OWN localStorage key — deliberately separate from CareerContext's
 * persisted state, which resets on every page refresh.
 *
 * Contract:
 *   - FIFO history, capped at RECENT_HISTORY_CAP ids
 *   - after a successful prediction the submitted question ids are appended
 *   - the next assessment passes them as an exclusion preference to /assessment
 *   - refreshing the page preserves history but clears active assessment state
 */

const HISTORY_KEY = 'altiora_recent_question_ids';
const RECENT_HISTORY_CAP = 60;

function isInteger(value) {
  return Number.isInteger(value);
}

/**
 * Read the current recent-question history.
 *
 * @returns {number[]} Recently used question ids (oldest first, capped)
 */
export function getRecentQuestionIds() {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter((n) => typeof n === 'number' && isInteger(n));
  } catch {
    return [];
  }
}

/**
 * Append question ids to the recent-question history (FIFO, capped).
 * Already-tracked ids move to the back so only the most recent matter.
 *
 * @param {Array<string|number>} questionIds – ids used in a completed assessment
 */
export function recordRecentQuestionIds(questionIds) {
  try {
    const incoming = (questionIds || [])
      .map((n) => Number(n))
      .filter((n) => isInteger(n));
    if (incoming.length === 0) return;

    const current = getRecentQuestionIds();
    const existing = new Set(incoming);
    const rest = current.filter((n) => !existing.has(n));
    const merged = rest.concat(incoming).slice(-RECENT_HISTORY_CAP);

    localStorage.setItem(HISTORY_KEY, JSON.stringify(merged));
  } catch {
    // Storage unavailable — anti-repetition degrades to pure randomness.
  }
}

export default { getRecentQuestionIds, recordRecentQuestionIds };
