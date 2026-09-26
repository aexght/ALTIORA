/**
 * main.jsx — Application entry point.
 *
 * Mounts the React app and imports the global stylesheet
 * that configures Tailwind CSS v4 design tokens.
 */

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './index.css';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
