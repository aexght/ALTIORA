import React from 'react';
import FormSection from '../forms/FormSection';
import Select from '../common/Select';
import { STREAM_OPTIONS } from '../../utils/constants';

/**
 * StreamSelection component for Phase 4 of CareerPath AI.
 *
 * @param {Object} props
 * @param {Object} props.values - Form values
 * @param {Object} props.errors - Form errors
 * @param {Function} props.onChange - Change handler
 */
const StreamSelection = ({ values, errors, onChange }) => {
  const handleChange = (e) => {
    onChange(e.target.name, e.target.value);
  };

  return (
    <FormSection title="Stream Selection" description="Select your preferred academic stream.">
      <Select
        id="stream"
        name="stream"
        label="Academic Stream"
        value={values.stream || ''}
        onChange={handleChange}
        options={STREAM_OPTIONS}
        error={errors.stream}
      />
    </FormSection>
  );
};

export { StreamSelection };
export default StreamSelection;
