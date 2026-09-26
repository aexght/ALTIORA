import { useState, useCallback } from 'react';

/**
 * Lightweight form-validation hook.
 *
 * Usage:
 *   const { errors, validate, clearError } = useFormValidation();
 *   const ok = validate(values, rules);   // returns boolean
 *   if (ok) submit();
 *
 * @returns {{ errors, validate, clearError, setErrors }}
 */
export function useFormValidation() {
  const [errors, setErrors] = useState({});

  /**
   * Run all validation rules against current values.
   *
   * @param {object} values  – { fieldName: value }
   * @param {object} rules   – { fieldName: (value) => errorString | null }
   * @returns {boolean} true if all fields pass
   */
  const validate = useCallback((values, rules) => {
    const newErrors = {};
    let isValid = true;

    for (const [field, rule] of Object.entries(rules)) {
      const error = rule(values[field]);
      if (error) {
        newErrors[field] = error;
        isValid = false;
      }
    }

    setErrors(newErrors);
    return isValid;
  }, []);

  const clearError = useCallback((field) => {
    setErrors((prev) => {
      const next = { ...prev };
      delete next[field];
      return next;
    });
  }, []);

  const clearAll = useCallback(() => setErrors({}), []);

  return { errors, validate, clearError, clearAll, setErrors };
}
