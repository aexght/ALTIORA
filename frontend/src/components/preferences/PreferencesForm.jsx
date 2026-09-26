import React from 'react';
import { Select } from '../common/Select';
import { RadioGroup } from '../common/RadioGroup';
import { Slider } from '../common/Slider';
import { FormSection } from '../forms/FormSection';
import {
  INDIAN_STATES,
  STATE_DISTRICTS,
  COLLEGE_TYPE_OPTIONS,
  HOSTEL_OPTIONS,
  INSTITUTION_TYPE_OPTIONS,
  TRAVEL_PREFERENCE_OPTIONS,
  PLACEMENT_IMPORTANCE_LABELS,
  MAX_FEE_MIN,
  MAX_FEE_MAX,
  MAX_FEE_STEP,
  PLACEMENT_MIN,
  PLACEMENT_MAX,
  PLACEMENT_STEP,
} from '../../utils/constants';
import { formatCurrency } from '../../utils/formatters';

export function PreferencesForm({ values, errors = {}, onChange }) {
  const selectedState = values.state || '';

  const districts = selectedState
    ? STATE_DISTRICTS[selectedState] || STATE_DISTRICTS['default'] || []
    : [];

  const stateOptions = INDIAN_STATES.map((state) => ({
    value: state,
    label: state,
  }));

  const districtOptions = districts.map((district) => ({
    value: district,
    label: district,
  }));

  const handleSelectChange = (e) => {
    const { name, value } = e.target;
    onChange(name, value);
    if (name === 'state') {
      onChange('district', '');
    }
  };

  const handleRadioChange = (e) => {
    const { name, value } = e.target;
    onChange(name, value);
  };

  const placementLabel = (value) =>
    PLACEMENT_IMPORTANCE_LABELS[value] || String(value);

  return (
    <>
      <FormSection
        title="Location"
        description="Where would you prefer to study? District is optional."
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <Select
            label="Preferred State"
            name="state"
            value={values.state || ''}
            onChange={handleSelectChange}
            options={stateOptions}
            placeholder="Select State"
            error={errors.state}
            required
          />

          <Select
            label="Preferred District"
            name="district"
            value={values.district || ''}
            onChange={handleSelectChange}
            options={districtOptions}
            placeholder="Select District (Optional)"
            disabled={!selectedState}
          />
        </div>
      </FormSection>

      <div className="h-px bg-stone-100 w-full my-8" />

      <FormSection
        title="College Preferences"
        description="These help us personalise your college recommendations."
      >
        <div className="space-y-8">
          <RadioGroup
            label="College Ownership"
            name="ownership"
            value={values.ownership}
            onChange={handleRadioChange}
            options={COLLEGE_TYPE_OPTIONS}
          />

          <Slider
            label="Maximum Annual Fee"
            name="maxFee"
            value={Number(values.maxFee)}
            min={MAX_FEE_MIN}
            max={MAX_FEE_MAX}
            step={MAX_FEE_STEP}
            onChange={(v, n) => onChange(n, v)}
            formatValue={formatCurrency}
            minLabel={formatCurrency(MAX_FEE_MIN)}
            maxLabel={formatCurrency(MAX_FEE_MAX)}
            description="Your maximum budget per year."
          />

          <RadioGroup
            label="Hostel Preference"
            name="hostel"
            value={values.hostel}
            onChange={handleRadioChange}
            options={HOSTEL_OPTIONS}
          />

          <RadioGroup
            label="College Type"
            name="collegeType"
            value={values.collegeType}
            onChange={handleRadioChange}
            options={INSTITUTION_TYPE_OPTIONS}
          />

          <Slider
            label="Placement Importance"
            name="placementImportance"
            value={Number(values.placementImportance)}
            min={PLACEMENT_MIN}
            max={PLACEMENT_MAX}
            step={PLACEMENT_STEP}
            onChange={(v, n) => onChange(n, v)}
            formatValue={placementLabel}
            minLabel={placementLabel(PLACEMENT_MIN)}
            maxLabel={placementLabel(PLACEMENT_MAX)}
            description="How important are campus placements to you?"
          />

          <RadioGroup
            label="Travel Preference"
            name="travelPreference"
            value={values.travelPreference}
            onChange={handleRadioChange}
            options={TRAVEL_PREFERENCE_OPTIONS}
          />
        </div>
      </FormSection>
    </>
  );
}

export default PreferencesForm;