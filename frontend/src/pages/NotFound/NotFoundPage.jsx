import React from 'react';
import { FileQuestion } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../components/common/Button';
import { motion } from 'framer-motion';

export const NotFoundPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center altiora-bg p-4">
      <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-md w-full text-center"
      >
        <FileQuestion className="w-12 h-12 text-stone-300 mx-auto" />
        <h1 className="text-6xl font-display font-bold text-stone-200 mt-4 tracking-tighter">404</h1>
        <h2 className="text-xl font-medium text-stone-900 mt-2">Page not found</h2>
        <p className="text-stone-500 mt-2 text-center">
          The page you're looking for doesn't exist or has been moved.
        </p>
        
        <div className="mt-8 flex justify-center">
          <Button variant="primary" onClick={() => navigate('/')}>
            Return Home
          </Button>
        </div>
      </motion.div>
    </div>
  );
};

export default NotFoundPage;
