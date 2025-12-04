import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = 'http://YOUR_SERVER_IP:8000/api';

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await AsyncStorage.removeItem('accessToken');
      await AsyncStorage.removeItem('refreshToken');
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (data) => api.post('/users/register/', data),
  login: (data) => api.post('/users/login/', data),
  getProfile: () => api.get('/users/profile/'),
  updateProfile: (data) => api.put('/users/profile/update/', data),
  updateLocation: (data) => api.post('/users/location/update/', data),
  saveFCMToken: (token) => api.post('/users/fcm-token/', { fcm_token: token }),
};

export const swipeAPI = {
  getSuggestions: () => api.get('/swipes/suggestions/'),
  swipe: (data) => api.post('/swipes/swipe/', data),
  getMatches: () => api.get('/swipes/matches/'),
};

export const chatAPI = {
  getRooms: () => api.get('/users/chat/rooms/'),
  getMessages: (roomId) => api.get(`/users/chat/messages/${roomId}/`),
  sendMessage: (data) => api.post('/users/chat/send/', data),
};

export const photoAPI = {
  getPresignedUrl: (extension) => api.get(`/photos/presigned-url/?file_extension=${extension}`),
  uploadPhoto: (data) => api.post('/photos/upload/', data),
  getPhotos: () => api.get('/photos/list/'),
  deletePhoto: (photoId) => api.delete(`/photos/${photoId}/delete/`),
  submitVerification: (data) => api.post('/photos/verification/submit/', data),
  getVerificationStatus: () => api.get('/photos/verification/status/'),
};

export const paymentAPI = {
  initiateRegistration: (data) => api.post('/payments/registration/initiate/', data),
  initiateSubscription: (data) => api.post('/payments/subscription/initiate/', data),
  checkStatus: (reference) => api.get(`/payments/status/${reference}/`),
};

export const adAPI = {
  getAds: () => api.get('/users/ads/'),
  trackClick: (adId) => api.post(`/users/ads/${adId}/click/`),
};

export default api;