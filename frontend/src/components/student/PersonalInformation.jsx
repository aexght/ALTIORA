import React from 'react';
import { Input } from '../common/Input';
import { Select } from '../common/Select';
import { FormSection } from '../forms/FormSection';
import { GENDER_OPTIONS } from '../../utils/constants';

export function PersonalInformation({ values, errors, onChange, onBlur }) {
  const handleChange = (e) => {
    const { name, value } = e.target;
    onChange(name, value);
  };

  const handleBlur = (e) => {
    const { name, value } = e.target;
    if (onBlur) {
      onBlur(name, value);
    }
  };

  return (
    <FormSection title="Personal Information">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <Input
          label="Full Name"
          name="name"
          value={values.name || ''}
          onChange={handleChange}
          onBlur={handleBlur}
          placeholder="Enter your full name"
          error={errors.name}
          required
          className="sm:col-span-2"
        />

        <Input
          label="Age"
          name="age"
          type="number"
          value={values.age || ''}
          onChange={handleChange}
          placeholder="e.g. 18"
          error={errors.age}
          required
        />

        <Select
          label="Gender"
          name="gender"
          value={values.gender || ''}
          onChange={handleChange}
          options={GENDER_OPTIONS}
          placeholder="Select gender"
          error={errors.gender}
          required
        />

        <Input
          label="Email"
          name="email"
          type="email"
          value={values.email || ''}
          onChange={handleChange}
          onBlur={handleBlur}
          placeholder="example@email.com"
          error={errors.email}
          required
          className="sm:col-span-2"
        />
      </div>
    </FormSection>
  );
}

export default PersonalInformation;
