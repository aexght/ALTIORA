import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useCareer } from '../../context/CareerContext';
import { PageContainer } from '../../components/layout/PageContainer';
import { ProgressBar } from '../../components/layout/ProgressBar';
import { Badge } from '../../components/common/Badge';
import { StudentNavigation } from '../../components/student/StudentNavigation';
import { validateRequired } from '../../utils/validators';
import PreferencesForm from '../../components/preferences/PreferencesForm';
import PreferencesSummaryCard from '../../components/preferences/PreferencesSummaryCard';

export default function PreferencesPage() {
  const { state, dispatch } = useCareer();
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const preferences = state?.preferences || {};

  // State is the only required field; everything else is optional.
  const stateError = validateRequired(preferences.state, 'Preferred State');
  const isValid = stateError === null;

  const handleChange = (name, value) => {
    let updates = { [name]: value };

    // Changing State must clear the dependent District.
    if (name === 'state' && value !== preferences.state) {
      updates.district = '';
    }

    dispatch({ type: 'SET_PREFERENCES', payload: updates });
  };

  const handleSubmit = (e) => {
    e?.preventDefault();

    if (isValid) {
      setIsSubmitting(true);
      const normalized = {
        state: preferences.state,
        district: preferences.district,
        ownership: preferences.ownership,
        maxFee: Number(preferences.maxFee),
        hostel: preferences.hostel,
        collegeType: preferences.collegeType,
        placementImportance: Number(preferences.placementImportance),
        travelPreference: preferences.travelPreference,
      };
      dispatch({ type: 'SET_PREFERENCES', payload: normalized });
      navigate('/questionnaire');
    } else {
      const el = document.getElementsByName('state')[0];
      if (el) el.focus();
    }
  };

  const displayErrors = stateError && preferences.state ? {} : (stateError ? { state: stateError } : {});

  return (
    <PageContainer maxWidth="md">
      <div className="max-w-[700px] mx-auto w-full">
        <div className="mb-8">
          <Badge variant="primary" className="mb-4">Step 3 of 5</Badge>
          <h1 className="text-3xl sm:text-4xl font-bold text-stone-900 mb-3">College Preferences</h1>
          <p className="text-stone-600 mb-8 text-lg">
            Help us personalise your college recommendations.
          </p>
          <ProgressBar current={3} total={5} label="60%" />
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="bg-white rounded-xl border border-stone-200 shadow-card p-6 sm:p-10 w-full"
        >
          <form onSubmit={handleSubmit} noValidate>
            <PreferencesForm values={preferences} errors={displayErrors} onChange={handleChange} />

            <button type="submit" className="hidden" aria-hidden="true" />

            <StudentNavigation
              onBack={() => navigate('/academic')}
              onContinue={handleSubmit}
              isValid={isValid}
              isSubmitting={isSubmitting}
            />
          </form>
        </motion.div>

        <PreferencesSummaryCard preferences={preferences} />
      </div>
    </PageContainer>
  );
}