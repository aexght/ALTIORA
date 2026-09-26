import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../common/Button';
import { cn } from '../../utils/cn';

export function StudentNavigation({ onBack, onContinue, isValid, isSubmitting, className }) {
  const navigate = useNavigate();

  const handleBack = () => {
    if (onBack) {
      onBack();
    } else {
      navigate('/');
    }
  };

  return (
    <div className={cn("flex items-center justify-between mt-8 pt-6 border-t border-stone-100", className)}>
      <Button 
        variant="ghost" 
        onClick={handleBack}
        disabled={isSubmitting}
      >
        ← Back
      </Button>
      
      <Button 
        variant="primary" 
        onClick={onContinue}
        disabled={!isValid || isSubmitting}
        loading={isSubmitting}
      >
        Continue →
      </Button>
    </div>
  );
}

export default StudentNavigation;
