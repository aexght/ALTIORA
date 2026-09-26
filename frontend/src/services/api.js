/**
 * Axios-based API service layer.
 *
 * All backend communication is isolated here.
 * Components call these functions — they never use axios directly.
 */

import axios from 'axios';

const api = axios.create({
  baseURL: '/api',          // Vite dev proxy rewrites this to http://localhost:5000
  timeout: 120000,          // 120 s — accommodate cold-start model load (117 MB joblib) on first /predict
  headers: { 'Content-Type': 'application/json' },
});

/**
 * GET /questions
 * Fetches the full question bank (master list).
 *
 * @returns {Promise<Array>} Array of question objects
 */
export async function getQuestions() {
  const { data } = await api.get('/questions');
  return data;
}

/**
 * GET /assessment?length=N&exclude=id1,id2,...
 * Fetches a randomized, domain-balanced selection of N questions from the
 * master bank. `exclude` is an optional list of recently used question ids
 * that the backend deprioritizes (with per-domain fallback).
 *
 * @param {number} length  – 10, 20, 30, or 40
 * @param {number[]} excludeIds – recently used question ids (anti-repetition)
 * @returns {Promise<{length: number, questions: Array}>} Selected assessment
 */
export async function getAssessment(length, excludeIds = []) {
  const params = new URLSearchParams({ length: String(length) });
  if (Array.isArray(excludeIds) && excludeIds.length > 0) {
    params.set('exclude', excludeIds.join(','));
  }
  const { data } = await api.get('/assessment', { params });
  return data;
}

/**
 * POST /predict
 * Submits academic details + questionnaire answers and returns
 * the career prediction, top domains, and course recommendations.
 *
 * @param {object} academic  – academic fields matching the API contract
 * @param {object} answers   – { questionId: optionId } e.g. { "1": "A", "2": "C" }
 * @returns {Promise<object>} Prediction result
 */
export async function submitPrediction(academic, answers) {
  const { data } = await api.post('/predict', { academic, answers });
  return data;
}

/**
 * GET /  (health check)
 * Can be used to verify backend connectivity.
 *
 * @returns {Promise<object>} { status, service, version }
 */
export async function healthCheck() {
  const { data } = await api.get('/');
  return data;
}

export default api;
