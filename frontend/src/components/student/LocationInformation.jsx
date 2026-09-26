import React from 'react';
import { Select } from '../common/Select';
import { FormSection } from '../forms/FormSection';
import { INDIAN_STATES, STATE_DISTRICTS, CATEGORY_OPTIONS } from '../../utils/constants';

export function LocationInformation({ values, errors, onChange }) {
  const handleChange = (e) => {
    const { name, value } = e.target;
    onChange(name, value);
    
    // Reset district when state changes
    if (name === 'state') {
      onChange('district', '');
    }
  };

  const stateOptions = INDIAN_STATES.map(state => ({ value: state, label: state }));
  
  const selectedState = values.state;
  const availableDistricts = selectedState 
    ? (STATE_DISTRICTS[selectedState] || STATE_DISTRICTS['default'] || [])
    : [];
    
  const districtOptions = availableDistricts.map(district => ({ value: district, label: district }));

  return (
    <FormSection title="Location" description="Used only for recommendation filtering where applicable.">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <Select
          label="State"
          name="state"
          value={values.state || ''}
          onChange={handleChange}
          options={stateOptions}
          placeholder="Select State"
          error={errors.state}
          required
        />

        <Select
          label="District"
          name="district"
          value={values.district || ''}
          onChange={handleChange}
          options={districtOptions}
          placeholder="Select District"
          error={errors.district}
          disabled={!values.state}
          required
        />

        <Select
          label="Category"
          name="category"
          value={values.category || ''}
          onChange={handleChange}
          options={CATEGORY_OPTIONS}
          placeholder="Select Category (Optional)"
          error={errors.category}
        />
      </div>
    </FormSection>
  );
}

export default LocationInformation;
