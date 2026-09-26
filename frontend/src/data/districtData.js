import districtRaw from './districts.json';

/**
 * District data module - single source of truth for Indian states and districts.
 * Consumes district.json directly to avoid duplicate maintenance.
 */

export const stateDistrictMap = districtRaw.reduce((acc, entry) => {
  acc[entry.state] = entry.districts;
  return acc;
}, {});

export const indianStates = districtRaw.map(entry => entry.state).sort();

export const getDistrictsForState = (state) => {
  return stateDistrictMap[state] || [];
};

export const getAllStates = () => indianStates;

export const getAllDistricts = () => {
  const all = [];
  for (const districts of Object.values(stateDistrictMap)) {
    all.push(...districts);
  }
  return all;
};

export default {
  stateDistrictMap,
  indianStates,
  getDistrictsForState,
  getAllStates,
  getAllDistricts,
};