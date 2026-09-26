import React from 'react';
import FormSection from '../forms/FormSection';
import Input from '../common/Input';

/**
 * AcademicPerformance component for Phase 4 of CareerPath AI.
 *
 * @param {Object} props
 * @param {Object} props.values - Form values
 * @param {Object} props.errors - Form errors
 * @param {Function} props.onChange - Change handler
 * @param {Function} props.onBlur - Blur handler
 * @param {String} props.computedClass12 - Computed Class 12 percentage
 * @param {Boolean} props.isClass12Complete - Whether all required marks are filled
 */
const AcademicPerformance = ({ values, errors, onChange, onBlur, computedClass12, isClass12Complete }) => {
  const handleChange = (e) => {
    onChange(e.target.name, e.target.value);
  };

  const handleBlur = (e) => {
    if (onBlur) {
      onBlur(e.target.name);
    }
  };

  return (
    <FormSection title="Academic Performance" description="Please enter your previous academic scores.">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input
          id="class10Percentage"
          name="class10Percentage"
          type="number"
          label="Class 10 Percentage"
          placeholder="%"
          min="35"
          max="100"
          step="0.01"
          value={values.class10Percentage || ''}
          onChange={handleChange}
          onBlur={handleBlur}
          error={errors.class10Percentage}
        />
        
        <div className="w-full">
          <label className="block text-sm font-medium text-stone-700 mb-1.5">
            Class 12 Percentage
          </label>
          <div className={`w-full px-4 py-2.5 rounded-lg border flex items-center transition-colors ${isClass12Complete ? 'bg-stone-50 border-stone-200' : 'bg-stone-100/50 border-stone-200 border-dashed'}`}>
            <span className={isClass12Complete ? 'text-stone-900 font-medium' : 'text-stone-400 text-sm'}>
              {isClass12Complete ? `${computedClass12}%` : 'Enter subject marks below to calculate'}
            </span>
          </div>
        </div>
      </div>
    </FormSection>
  );
};

export { AcademicPerformance };
export default AcademicPerformance;
