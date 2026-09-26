/**
 * Display formatting utilities.
 */

import { UNVERIFIED_VALUES } from './constants';

/**
 * Returns true if a value is considered "unverified" or unknown
 * and should be hidden from the UI.
 */
export function isUnverified(value) {
  if (value === null || value === undefined || value === '') return true;
  if (typeof value === 'string') {
    return UNVERIFIED_VALUES.includes(value.trim());
  }
  return false;
}

/** Format a number as a percentage string safely bounded to 100%, e.g. 28.45 -> "28.45%" */
export function formatPercent(value, decimals = 1) {
  if (value === null || value === undefined || isNaN(Number(value))) return '';
  const num = Math.max(0, Math.min(100, Number(value)));
  return `${num.toFixed(decimals)}%`;
}

/** Format a number as Indian Rupee currency. */
export function formatCurrency(value) {
  if (value === null || value === undefined) return '';
  const num = Number(value);
  if (isNaN(num)) return '';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(num);
}

/**
 * Capitalise the first letter of each word.
 * "technology & computing" → "Technology & Computing"
 */
export function titleCase(str) {
  if (!str) return '';
  return str.replace(/\b\w/g, (char) => char.toUpperCase());
}

/**
 * Truncate a string to maxLen characters, adding "…" if truncated.
 */
export function truncate(str, maxLen = 120) {
  if (!str || str.length <= maxLen) return str || '';
  return str.slice(0, maxLen).trimEnd() + '…';
}

/**
 * Return a confidence level's corresponding semantic colour class.
 */
export function confidenceColor(level) {
  switch (level) {
    case 'Very High':
    case 'High':
      return 'success';
    case 'Moderate':
      return 'warning';
    case 'Low':
    case 'Very Low':
      return 'danger';
    default:
      return 'primary';
  }
}
