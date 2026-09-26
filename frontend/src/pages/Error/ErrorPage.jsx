import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from '../../components/common/Button';
import { motion } from 'framer-motion';

export const ErrorPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  const errorMessage = location.state?.message || 'We encountered an unexpected error. Please try again.';

  return (
    <div className="min-h-screen flex items-center justify-center altiora-bg p-4">
      <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-md w-full text-center"
      >
        <div className="w-16 h-16 rounded-full bg-red-50 border border-red-100 flex items-center justify-center mx-auto">
          <AlertTriangle className="w-8 h-8 text-red-600" />
        </div>
        <h1 className="text-2xl font-display font-bold text-stone-900 mt-6">Something went wrong</h1>
        <p className="text-stone-500 mt-2 text-center">{errorMessage}</p>
        
        <div className="gap-3 mt-8 flex justify-center">
          <Button variant="primary" onClick={() => navigate(-1)}>
            Try Again
          </Button>
          <Button variant="outline" onClick={() => navigate('/')}>
            Back to Home
          </Button>
        </div>
      </motion.div>
    </div>
  );
};

export default ErrorPage;
