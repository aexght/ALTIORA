/**
 * Prediction service layer.
 *
 * Builds the POST /predict payload from CareerContext state and delegates the
 * HTTP call to the shared api.js service (no duplicated fetch logic here).
 * Also validates the response shape so the questionnaire page can detect
 * malformed responses and show a friendly error.
 */

import { submitPrediction } from './api';

/**
 * Build the exact payload expected by POST /predict.
 *
 * Backend contract (see app.py::predict):
 *   academic: {
 *     class10Percentage, class12Percentage, stream,
 *     electives: string[],
 *     subjectMarks: { 'Physics_Marks': 85, ... }
 *   }
 *   answers: { '1': 'A', '2': 'B', ... }
 *
 * CareerContext already stores academic + questionnaire answers in this exact
 * shape, so we pass them through without renaming any keys.
 *
 * @param {object} academic  – CareerContext `academic` state
 * @param {object} answers   – CareerContext `questionnaire.answers` map
 * @returns {{ academic: object, answers: object }} Payload for POST /predict
 */
export function buildPredictionPayload(academic, answers) {
  return {
    academic: {
      class10Percentage: academic?.class10Percentage,
      class12Percentage: academic?.class12Percentage,
      stream: academic?.stream,
      electives: Array.isArray(academic?.electives) ? academic.electives : [],
      subjectMarks: academic?.subjectMarks || {},
    },
    answers: answers || {},
  };
}

/**
 * A prediction response is considered well-formed when it contains a
 * `prediction` object with a domain and confidence. Matches the real
 * POST /predict response, e.g.
 *   { "prediction": { "domain": "Engineering", "probability": 34.5, "confidence": "Low" } }
 *
 * @param {object} data  – Parsed POST /predict response body
 * @returns {boolean} Whether the response is structurally valid
 */
export function isWellFormedPrediction(data) {
  return Boolean(
    data &&
    typeof data === 'object' &&
    data.prediction &&
    typeof data.prediction === 'object' &&
    typeof data.prediction.domain === 'string' &&
    typeof data.prediction.confidence === 'string'
  );
}

/**
 * Submit academic details + answers to POST /predict and return the full
 * backend response (persisted verbatim under `prediction` in CareerContext).
 *
 * @param {object} academic – CareerContext `academic` state
 * @param {object} answers  – CareerContext `questionnaire.answers` map
 * @returns {Promise<object>} Full prediction response from the backend
 * @throws {Error} On network/timeout/HTTP errors or a malformed response
 */
export async function submitCareerPrediction(academic, answers) {
  const payload = buildPredictionPayload(academic, answers);
  const data = await submitPrediction(payload.academic, payload.answers);

  if (!isWellFormedPrediction(data)) {
    throw new Error(
      'The prediction service returned an unexpected response. Please try again.'
    );
  }

  return data;
}

/**
 * Convert an error thrown by submitCareerPrediction() into a friendly,
 * user-safe message.
 *
 * Handles: network failure, timeout, backend 4xx (validation), backend 5xx,
 * and malformed responses (a plain Error with our sentinel message).
 *
 * @param {Error} err  – The error thrown by the service call
 * @returns {string} A friendly message the user can read and act on
 */
export function getPredictionErrorMessage(err) {
  if (!err) {
    return 'Something went wrong while generating your prediction. Please try again.';
  }

  // Malformed response (thrown locally with a sentinel message).
  if (err.message === 'The prediction service returned an unexpected response. Please try again.') {
    return err.message;
  }

  // Timeout.
  if (err.code === 'ECONNABORTED') {
    return 'The prediction took too long. Please try again.';
  }

  // Axios errors carry a `response` when the server answered.
  if (err.response) {
    const status = err.response.status;
    const detail =
      err.response.data &&
      typeof err.response.data === 'object' &&
      typeof err.response.data.error === 'string'
        ? err.response.data.error
        : '';

    if (status >= 400 && status < 500) {
      return detail
        ? 'Your details could not be submitted: ' + detail
        : 'Some of your details could not be validated. Please review them and try again.';
    }
    if (status >= 500) {
      return 'Something went wrong on our side. Please try again in a moment.';
    }
  }

  // No response received (network failure / backend unreachable).
  if (err.request) {
    return 'Could not reach the prediction server. Please check your connection and try again.';
  }

  return 'Something went wrong while generating your prediction. Please try again.';
}
