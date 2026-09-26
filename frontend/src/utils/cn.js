/**
 * Merges class name strings, filtering out falsy values.
 * Lightweight alternative to clsx/classnames.
 *
 * @param {...(string|boolean|null|undefined)} classes
 * @returns {string}
 */
export function cn(...classes) {
  return classes.filter(Boolean).join(' ');
}

export default cn;
