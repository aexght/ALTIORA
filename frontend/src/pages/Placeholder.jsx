import React from 'react';
import { PageContainer } from '../components/layout/PageContainer';

export const Placeholder = ({ title }) => {
  return (
    <PageContainer title={title}>
      <div className="text-slate-500 text-center py-16">
        This page is coming soon.
      </div>
    </PageContainer>
  );
};

export default Placeholder;
