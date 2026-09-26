/**
 * App.jsx — Root component with routing and layout.
 */

import { BrowserRouter, Routes, Route, useLocation, useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import { CareerProvider, useCareer } from './context/CareerContext';
import { Navbar } from './components/layout/Navbar';
import { Footer } from './components/layout/Footer';

// Pages — real implementations
import LandingPage from './pages/Landing/LandingPage';
import ErrorPage from './pages/Error/ErrorPage';
import NotFoundPage from './pages/NotFound/NotFoundPage';

// Pages — placeholders (replaced in later phases)
import Placeholder from './pages/Placeholder';

import StudentDetailsPage from './pages/Student/StudentDetailsPage';
import AcademicDetailsPage from './pages/Academic/AcademicDetailsPage';
import QuestionnairePage from './pages/Questionnaire/QuestionnairePage';
import ResultsPage from './pages/Results/ResultsPage';

function AppRoutes() {
  const location = useLocation();
  const navigate = useNavigate();
  const { state } = useCareer();

  useEffect(() => {
    // If the user is on a form/results page and the session hasn't started (e.g. hard refresh), redirect to home.
    const isProtected = ['/student', '/academic', '/questionnaire', '/results', '/loading'].some(p => location.pathname.startsWith(p));
    if (isProtected && !state.hasStarted) {
      navigate('/', { replace: true });
    }
  }, [location.pathname, state.hasStarted, navigate]);

  // Pages that should NOT show the Navbar/Footer (landing, loading, error, 404)
  const hideChrome = ['/', '/loading', '/error'].includes(location.pathname);

  return (
    <>
      {!hideChrome && <Navbar />}

      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          {/* Landing */}
          <Route path="/" element={<LandingPage />} />

          {/* Multi-step form */}
          <Route path="/student" element={<StudentDetailsPage />} />
          <Route path="/academic" element={<AcademicDetailsPage />} />
          <Route path="/questionnaire" element={<QuestionnairePage />} />

          {/* Processing */}
          <Route path="/loading" element={<Placeholder title="Analysing..." />} />

          {/* Results */}
          <Route path="/results" element={<ResultsPage />} />
          <Route path="/results/courses" element={<Placeholder title="Recommended Courses" />} />
          <Route path="/results/colleges" element={<Placeholder title="Recommended Colleges" />} />
          <Route path="/results/report" element={<Placeholder title="Your Report" />} />

          {/* Error & 404 */}
          <Route path="/error" element={<ErrorPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </AnimatePresence>

      {!hideChrome && <Footer />}
    </>
  );
}

export default function App() {
  return (
    <CareerProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </CareerProvider>
  );
}
