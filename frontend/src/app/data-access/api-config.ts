/**
 * API Configuration
 * Holds base URL and endpoint constants for backend communication
 */

export const API_BASE_URL = 'http://127.0.0.1:8000';

export const API_ENDPOINTS = {
  faqs: `${API_BASE_URL}/faqs`,
  generateFaqs: `${API_BASE_URL}/faqs/generate`,
  records: `${API_BASE_URL}/records`,
};
