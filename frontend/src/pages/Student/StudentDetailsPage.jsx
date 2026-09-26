import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useCareer } from '../../context/CareerContext';
import { PageContainer } from '../../components/layout/PageContainer';
import { ProgressBar } from '../../components/layout/ProgressBar';
import { Badge } from '../../components/common/Badge';
import { PersonalInformation } from '../../components/student/PersonalInformation';
import { LocationInformation } from '../../components/student/LocationInformation';
import { StudentNavigation } from '../../components/student/StudentNavigation';
import { validateForm, validateName, validateAge, validateEmail, validateRequired } from '../../utils/validators';

export default function StudentDetailsPage() {
  const { state, dispatch } = useCareer();
  const navigate = useNavigate();
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const student = state?.student || {};

  const validationRules = {
    name: validateName,
    age: validateAge,
    email: validateEmail,
    gender: (v) => validateRequired(v, 'Gender'),
    state: (v) => validateRequired(v, 'State'),
    district: (v) => validateRequired(v, 'District'),
  };

  const { isValid, errors: currentErrors } = validateForm(student, validationRules);

  const handleChange = (name, value) => {
    dispatch({
      type: 'SET_STUDENT',
      payload: { [name]: value }
    });
    setTouched(prev => ({ ...prev, [name]: true }));
  };

  const handleBlur = (name, value) => {
    if (typeof value === 'string') {
      dispatch({
        type: 'SET_STUDENT',
        payload: { [name]: value.trim() }
      });
    }
  };

  const handleSubmit = (e) => {
    e?.preventDefault();
    
    // Mark all as touched on submit attempt
    const allTouched = Object.keys(validationRules).reduce((acc, key) => {
      acc[key] = true;
      return acc;
    }, {});
    setTouched(allTouched);
    
    if (isValid) {
      setIsSubmitting(true);
      navigate('/academic');
    } else {
      // Focus first invalid field
      const firstInvalid = Object.keys(currentErrors)[0];
      if (firstInvalid) {
        const el = document.getElementsByName(firstInvalid)[0];
        if (el) el.focus();
      }
    }
  };

  // Only show errors for fields the user has interacted with (or if they tried to submit)
  const displayErrors = Object.keys(currentErrors).reduce((acc, key) => {
    if (touched[key]) acc[key] = currentErrors[key];
    return acc;
  }, {});

  return (
    <PageContainer maxWidth="md">
      <div className="max-w-[700px] mx-auto w-full">
        <div className="mb-8">
          <Badge variant="primary" className="mb-4">Step 1 of 4</Badge>
          <h1 className="text-3xl sm:text-4xl font-bold text-stone-900 mb-3">Tell us about yourself</h1>
          <p className="text-stone-600 mb-8 text-lg">
            We'll use these details to personalise your assessment report and recommendations.
          </p>
          <ProgressBar current={1} total={4} label="25%" />
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="bg-white rounded-xl border border-stone-200 shadow-card p-6 sm:p-10 w-full"
        >
          <form onSubmit={handleSubmit} noValidate>
            <PersonalInformation 
              values={student} 
              errors={displayErrors} 
              onChange={handleChange}
              onBlur={handleBlur}
            />
            
            <div className="h-px bg-stone-100 w-full my-8" />
            
            <LocationInformation 
              values={student} 
              errors={displayErrors} 
              onChange={handleChange} 
            />
            
            <button type="submit" className="hidden" aria-hidden="true" />
            
            <StudentNavigation 
              onContinue={handleSubmit} 
              isValid={isValid} 
              isSubmitting={isSubmitting}
            />
          </form>
        </motion.div>
      </div>
    </PageContainer>
  );
}
