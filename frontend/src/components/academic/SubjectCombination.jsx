import React from 'react';
import FormSection from '../forms/FormSection';
import { Select } from '../common/Select';
import { SUBJECT_COMBINATIONS } from '../../utils/constants';

/**
 * SubjectCombination component for selecting subject combination based on stream
 * 
 * @param {Object} props - Component props
 * @param {Object} props.values - Form values containing stream and subjectCombination
 * @param {Object} props.errors - Validation errors
 * @param {Function} props.onChange - Change handler function
 */
export const SubjectCombination = ({ values, errors, onChange }) => {
  const options = values.stream && SUBJECT_COMBINATIONS[values.stream] 
    ? SUBJECT_COMBINATIONS[values.stream] 
    : [];

  return (
    <FormSection>
      <Select
        id="subject-combination-select"
        label="Subject Combination"
        name="subjectCombination"
        value={values.subjectCombination || ''}
        options={options}
        disabled={!values.stream || options.length === 0}
        error={errors?.subjectCombination}
        onChange={(e) => onChange(e.target.name, e.target.value)}
      />
    </FormSection>
  );
};

export default SubjectCombination;
