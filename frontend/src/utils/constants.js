/**
 * Application-wide constants.
 * Centralises dropdown options, labels, and configuration values
 * so they stay consistent across all form pages.
 */

import { indianStates, stateDistrictMap } from '../data/districtData';

export const INDIAN_STATES = indianStates;

/** District mapping for states. Sourced from district.json (single source of truth). */
export const STATE_DISTRICTS = stateDistrictMap;

export const GENDER_OPTIONS = [
  { value: 'Male', label: 'Male' },
  { value: 'Female', label: 'Female' },
  { value: 'Other', label: 'Other' },
  { value: 'Prefer not to say', label: 'Prefer not to say' },
];

export const CATEGORY_OPTIONS = [
  { value: 'General', label: 'General' },
  { value: 'OBC', label: 'OBC' },
  { value: 'SC', label: 'SC' },
  { value: 'ST', label: 'ST' },
  { value: 'EWS', label: 'EWS' },
  { value: 'Other', label: 'Other' },
];

export const STREAM_OPTIONS = [
  { value: 'Science', label: 'Science' },
  { value: 'Commerce', label: 'Commerce' },
];

export const SUBJECT_COMBINATIONS = {
  Science: [
    { value: 'PCM', label: 'PCM (Physics, Chemistry, Maths)' },
    { value: 'PCB', label: 'PCB (Physics, Chemistry, Biology)' },
    { value: 'PCMB', label: 'PCMB (Physics, Chemistry, Maths, Biology)' },
    { value: 'PCMC', label: 'PCMC (Physics, Chemistry, Maths, Computer Science)' },
    { value: 'PCMS', label: 'PCMS (Physics, Chemistry, Maths, Statistics)' },
  ],
  Commerce: [
    { value: 'Commerce', label: 'Commerce (General)' },
    { value: 'Commerce_Maths', label: 'Commerce with Maths' },
    { value: 'Commerce_CS', label: 'Commerce with Computer Science' },
    { value: 'Commerce_Statistics', label: 'Commerce with Statistics' },
  ],
  Arts: [
    { value: 'Humanities', label: 'Humanities' },
  ],
};

/**
 * Maps subject combination to the academic mark fields
 * that are relevant (non-zero) for that combination.
 * Other fields default to 0 in the API payload.
 */
export const SUBJECT_FIELDS = {
  PCM: ['Physics_Marks', 'Chemistry_Marks', 'Maths_Marks', 'English_Marks'],
  PCB: ['Physics_Marks', 'Chemistry_Marks', 'Biology_Marks', 'English_Marks'],
  PCMB: ['Physics_Marks', 'Chemistry_Marks', 'Maths_Marks', 'Biology_Marks', 'English_Marks'],
  PCMC: ['Physics_Marks', 'Chemistry_Marks', 'Maths_Marks', 'ComputerScience_Marks', 'English_Marks'],
  PCMS: ['Physics_Marks', 'Chemistry_Marks', 'Maths_Marks', 'Statistics_Marks', 'English_Marks'],
  Commerce: ['Accountancy_Marks', 'BusinessStudies_Marks', 'Economics_Marks', 'English_Marks'],
  Commerce_Maths: ['Accountancy_Marks', 'BusinessStudies_Marks', 'Economics_Marks', 'Maths_Marks', 'English_Marks'],
  Commerce_CS: ['Accountancy_Marks', 'BusinessStudies_Marks', 'Economics_Marks', 'ComputerScience_Marks', 'English_Marks'],
  Commerce_Statistics: ['Accountancy_Marks', 'BusinessStudies_Marks', 'Economics_Marks', 'Statistics_Marks', 'English_Marks'],
  Humanities: ['English_Marks'],
};

/**
 * Dynamic subject selection system.
 * Core subjects are always displayed. Electives are selectable (1–2).
 * Sourced from subject_combination_mapper.py — the backend is the single source of truth.
 */
export const STREAM_SUBJECTS = {
  Science: {
    core: ['Physics', 'Chemistry', 'English'],
    electives: ['Mathematics', 'Biology', 'Computer Science', 'Statistics'],
  },
  Commerce: {
    core: ['Accountancy', 'Business Studies', 'English'],
    electives: ['Mathematics', 'Computer Science', 'Statistics', 'Economics', 'History'],
  },
  Arts: {
    core: ['English'],
    electives: ['History', 'Geography', 'Political Science', 'Economics', 'Psychology', 'Sociology'],
  },
};

/** Maximum number of elective subjects a student can select. */
export const MAX_ELECTIVES = 2;

/**
 * Maps human-readable subject name → backend subjectMarks key.
 * Sourced directly from subject_combination_mapper.py SUBJECT_TO_MARK_KEY.
 */
export const SUBJECT_MARK_KEY = {
  'Physics': 'Physics_Marks',
  'Chemistry': 'Chemistry_Marks',
  'Mathematics': 'Maths_Marks',
  'Biology': 'Biology_Marks',
  'Computer Science': 'ComputerScience_Marks',
  'Statistics': 'Statistics_Marks',
  'Accountancy': 'Accountancy_Marks',
  'Economics': 'Economics_Marks',
  'Business Studies': 'BusinessStudies_Marks',
  'English': 'English_Marks',
  'History': 'History_Marks',
  'Geography': 'Geography_Marks',
  'Political Science': 'PoliticalScience_Marks',
  'Psychology': 'Psychology_Marks',
  'Sociology': 'Sociology_Marks',
};

export const SUBJECT_LABELS = {
  Physics_Marks: 'Physics',
  Chemistry_Marks: 'Chemistry',
  Maths_Marks: 'Mathematics',
  Biology_Marks: 'Biology',
  ComputerScience_Marks: 'Computer Science',
  English_Marks: 'English',
  Accountancy_Marks: 'Accountancy',
  Economics_Marks: 'Economics',
  BusinessStudies_Marks: 'Business Studies',
  Statistics_Marks: 'Statistics',
};

export const ENTRANCE_EXAMS = [
  'JEE Main', 'JEE Advanced', 'NEET', 'CUET', 'BITSAT', 'VITEEE',
  'SRMJEEE', 'MET (Manipal)', 'KIITEE', 'WBJEE', 'MHT-CET',
  'AP EAMCET', 'KCET', 'COMEDK', 'IPU CET', 'CLAT', 'LSAT',
  'NID', 'NIFT', 'UCEED', 'CAT (Foundation)', 'Other', 'None',
];

export const COLLEGE_TYPE_OPTIONS = [
  { value: 'Government', label: 'Government' },
  { value: 'Private', label: 'Private' },
  { value: 'Both', label: 'Both' },
];

export const BUDGET_OPTIONS = [
  { value: '', label: 'No preference' },
  { value: '50000', label: 'Under ₹50,000 / year' },
  { value: '100000', label: 'Under ₹1,00,000 / year' },
  { value: '200000', label: 'Under ₹2,00,000 / year' },
  { value: '500000', label: 'Under ₹5,00,000 / year' },
  { value: '1000000', label: 'Under ₹10,00,000 / year' },
  { value: '999999999', label: 'No limit' },
];

/** 10 career domains the ML model can predict. */
export const CAREER_DOMAINS = [
  'Agriculture Environment & Food',
  'Business & Management',
  'Commerce & Finance',
  'Design Media & Creative',
  'Engineering',
  'Law & Legal Studies',
  'Life Sciences & Biotechnology',
  'Medical & Health Sciences',
  'Physical & Mathematical Sciences',
  'Technology & Computing',
];

/** Confidence labels returned by the backend. */
export const CONFIDENCE_LEVELS = ['Very High', 'High', 'Moderate', 'Low', 'Very Low'];

/**
 * Values that the backend or dataset may use to indicate
 * unverified / unknown information.  Any field whose value
 * matches one of these strings must be hidden in the UI.
 */
export const UNVERIFIED_VALUES = [
  'Not Verified',
  'Unknown',
  'N/A',
  'Not Available',
  'NA',
  'not verified',
  'unknown',
  'n/a',
  'not available',
];

/** Number of questionnaire questions. */
export const TOTAL_QUESTIONS = 40;

/** Application metadata. */
export const APP_NAME = 'ALTIORA';
export const APP_DESCRIPTION = 'AI-Powered Career Guidance for Students After 12th Grade';

/**
 * Steps shown in the Navbar progress indicator.
 * Each entry maps a route prefix to a label.
 */
export const STEPS = [
  { path: '/student', label: 'Student' },
  { path: '/academic', label: 'Academic' },
  { path: '/questionnaire', label: 'Assessment' },
  { path: '/results', label: 'Results' },
];

/** College Preferences — hostel requirement options. */
export const HOSTEL_OPTIONS = [
  { value: 'Required', label: 'Required' },
  { value: 'Not Required', label: 'Not Required' },
  { value: "Doesn't Matter", label: "Doesn't Matter" },
];

/** College Preferences — institution type options (Section 6). */
export const INSTITUTION_TYPE_OPTIONS = [
  { value: 'Autonomous', label: 'Autonomous' },
  { value: 'University', label: 'University' },
  { value: 'Affiliated', label: 'Affiliated' },
  { value: 'Any', label: 'Any' },
];

/** College Preferences — travel distance preference options (Section 8). */
export const TRAVEL_PREFERENCE_OPTIONS = [
  { value: 'Nearby', label: 'Nearby' },
  { value: 'Within District', label: 'Within District' },
  { value: 'Within State', label: 'Within State' },
  { value: 'Anywhere', label: 'Anywhere' },
];

/** College Preferences — placement importance level labels (Section 7). */
export const PLACEMENT_IMPORTANCE_LABELS = {
  1: 'Not Important',
  2: 'Less Important',
  3: 'Moderately Important',
  4: 'Important',
  5: 'Very Important',
};

/** College Preferences — maximum annual fee slider bounds (Section 4). */
export const MAX_FEE_MIN = 0;
export const MAX_FEE_MAX = 500000;
export const MAX_FEE_STEP = 5000;
export const MAX_FEE_DEFAULT = 120000;

/** College Preferences — placement importance slider bounds (Section 7). */
export const PLACEMENT_MIN = 1;
export const PLACEMENT_MAX = 5;
export const PLACEMENT_STEP = 1;
export const PLACEMENT_DEFAULT = 3;
