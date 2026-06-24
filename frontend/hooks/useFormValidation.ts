import { useState, useCallback } from 'react';

type Rule = {
  required?: boolean;
  email?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  message?: string;
};

type Rules = Record<string, Rule>;
type Errors = Record<string, string>;

function validateField(value: string, rule: Rule): string {
  if (rule.required && !value.trim()) {
    return rule.message || 'This field is required';
  }
  if (value && rule.email) {
    const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRe.test(value)) {
      return rule.message || 'Please enter a valid email address';
    }
  }
  if (value && rule.minLength !== undefined && value.length < rule.minLength) {
    return rule.message || `Must be at least ${rule.minLength} characters`;
  }
  if (value && rule.maxLength !== undefined && value.length > rule.maxLength) {
    return rule.message || `Must be no more than ${rule.maxLength} characters`;
  }
  if (value && rule.pattern && !rule.pattern.test(value)) {
    return rule.message || 'Invalid format';
  }
  return '';
}

export function useFormValidation(rules: Rules) {
  const [errors, setErrors] = useState<Errors>({});

  const validate = useCallback(
    (values: Record<string, string>): boolean => {
      const newErrors: Errors = {};
      for (const [field, rule] of Object.entries(rules)) {
        const err = validateField(values[field] ?? '', rule);
        if (err) newErrors[field] = err;
      }
      setErrors(newErrors);
      return Object.keys(newErrors).length === 0;
    },
    [rules]
  );

  const clearError = useCallback((field: string) => {
    setErrors(prev => {
      if (!prev[field]) return prev;
      const next = { ...prev };
      delete next[field];
      return next;
    });
  }, []);

  return { errors, validate, clearError };
}
