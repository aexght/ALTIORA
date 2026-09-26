/**
 * CareerContext — Global application state.
 *
 * Stores data collected across all pages and persists it
 * to localStorage so users don't lose progress on refresh.
 *
 * State shape:
 *   studentDetails   – name, age, gender, state, district, category, email
 *   academic         – percentages, stream, subject combination, marks, exams, interests
 *   preferences      – state, district, ownership, maxFee, hostel, collegeType, placementImportance, travelPreference
 *   questionnaire    – { answers: { "1": "A", ... }, currentIndex: 0 }
 *   prediction       – full backend POST /predict response, persisted verbatim
 *   results          – reserved (legacy placeholder)
 *   hasStarted       – boolean to track if the session was explicitly started (detects hard refresh)
 */

import { createContext, useContext, useReducer } from 'react';

const CareerContext = createContext(null);

const INITIAL_STATE = {
  student: {
    name: '',
    age: '',
    gender: '',
    email: '',
    state: '',
    district: '',
    category: '',
  },
  academic: {
    class10Percentage: '',
    class12Percentage: '',
    stream: '',
    electives: [],
    subjectMarks: {},
  },
  preferences: {
    state: '',
    district: '',
    ownership: 'Both',
    maxFee: 120000,
    hostel: "Doesn't Matter",
    collegeType: 'Any',
    placementImportance: 3,
    travelPreference: 'Within State',
  },
  questionnaire: {
    answers: {},
    currentIndex: 0,
  },
  prediction: null,
  results: null,
  hasStarted: false,
};

function reducer(state, action) {
  switch (action.type) {
    case 'START_ASSESSMENT':
      return { ...state, hasStarted: true };

    case 'SET_STUDENT':
      return { ...state, student: { ...state.student, ...action.payload } };

    case 'SET_ACADEMIC':
      return { ...state, academic: { ...state.academic, ...action.payload } };

    case 'SET_PREFERENCES':
      return { ...state, preferences: { ...state.preferences, ...action.payload } };

    case 'SET_ANSWER':
      return {
        ...state,
        questionnaire: {
          ...state.questionnaire,
          answers: { ...state.questionnaire.answers, [action.payload.questionId]: action.payload.optionId },
        },
      };

    case 'SET_QUESTION_INDEX':
      return {
        ...state,
        questionnaire: { ...state.questionnaire, currentIndex: action.payload },
      };

    case 'SET_PREDICTION':
      return { ...state, prediction: action.payload };

    case 'SET_RESULTS':
      return { ...state, results: action.payload };

    case 'RESET':
      return INITIAL_STATE;

    default:
      return state;
  }
}

export function CareerProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, INITIAL_STATE);

  return (
    <CareerContext.Provider value={{ state, dispatch }}>
      {children}
    </CareerContext.Provider>
  );
}

/**
 * Hook to access career context.
 * @returns {{ state: object, dispatch: function }}
 */
export function useCareer() {
  const context = useContext(CareerContext);
  if (!context) {
    throw new Error('useCareer must be used within a CareerProvider');
  }
  return context;
}

export default CareerContext;
