/**
 * Client-side validation helpers.
 * Each validator returns an error string or null if valid.
 */

export function validateRequired(value, fieldName = 'This field') {
  if (value === null || value === undefined || String(value).trim() === '') {
    return `${fieldName} is required`;
  }
  return null;
}

export function validateEmail(value) {
  if (!value) return 'Email is required';
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!pattern.test(value)) return 'Enter a valid email address';
  return null;
}

export function validateAge(value) {
  if (!value) return 'Age is required';
  const age = Number(value);
  if (isNaN(age) || !Number.isInteger(age)) return 'Age must be a whole number';
  if (age < 16 || age > 30) return 'Age must be between 16 and 30';
  return null;
}

export function validateName(value) {
  if (!value || String(value).trim() === '') return 'Name is required';
  if (String(value).trim().length < 3) return 'Name must be at least 3 characters';
  if (String(value).trim().length > 60) return 'Name cannot exceed 60 characters';
  return null;
}

export function validatePercentage(value, fieldName = 'Percentage') {
  if (value === '' || value === null || value === undefined) {
    return `${fieldName} is required`;
  }
  const num = Number(value);
  if (isNaN(num)) return `${fieldName} must be a number`;
  if (num < 0 || num > 100) return `${fieldName} must be between 0 and 100`;
  return null;
}

export function validateClass10Percentage(value) {
  if (value === '' || value === null || value === undefined) {
    return 'Class 10 Percentage is required';
  }
  const num = Number(value);
  if (isNaN(num)) return 'Class 10 Percentage must be a number';
  if (num < 35) return 'Class 10 percentage must be at least 35%';
  if (num > 100) return 'Class 10 percentage must be between 35 and 100%';
  return null;
}

export function validateMarks(value, fieldName = 'Marks') {
  if (value === '' || value === null || value === undefined) {
    return `${fieldName} is required`;
  }
  const num = Number(value);
  if (isNaN(num)) return `${fieldName} must be a number`;
  if (num < 0 || num > 100) return `${fieldName} must be between 0 and 100`;
  return null;
}

/**
 * Validate an entire form using a rules object.
 *
 * @param {object} values   – form values { fieldName: value }
 * @param {object} rules    – { fieldName: (value) => errorString | null }
 * @returns {{ isValid: boolean, errors: object }}
 */
export function validateForm(values, rules) {
  const errors = {};
  let isValid = true;

  for (const [field, validate] of Object.entries(rules)) {
    const error = validate(values[field]);
    if (error) {
      errors[field] = error;
      isValid = false;
    }
  }

  return { isValid, errors };
}
