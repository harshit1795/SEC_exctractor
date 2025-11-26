'use client';

import { useState, useEffect } from 'react';
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  signInWithPopup,
  GoogleAuthProvider,
  onAuthStateChanged,
  User,
  Auth,
} from 'firebase/auth';
import { auth } from '../firebase';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!auth) {
      console.warn('Firebase auth not initialized');
      setLoading(false);
      return;
    }

    // Set a timeout to prevent infinite loading
    const timeoutId = setTimeout(() => {
      console.warn('Auth state check timeout - setting loading to false');
      setLoading(false);
    }, 10000); // 10 second timeout

    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      clearTimeout(timeoutId);
      setUser(user);
      setLoading(false);
      
      // Auto-initialize user profile on sign-in
      if (user?.uid) {
        try {
          // Import here to avoid circular dependency
          const { api } = await import('../api');
          await api.initializeUserProfile(user.uid, {
            firebase_display_name: user.displayName || undefined,
            firebase_photo_url: user.photoURL || undefined,
            firebase_email: user.email || undefined,
          });
        } catch (error) {
          // Silently fail - profile will be created on first access
          console.debug('Profile initialization:', error);
        }
      }
    });

    return () => {
      clearTimeout(timeoutId);
      unsubscribe();
    };
  }, []);

  const login = async (email: string, password: string) => {
    if (!auth) {
      return { user: null, error: 'Firebase not initialized' };
    }
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      return { user: userCredential.user, error: null };
    } catch (error: any) {
      return { user: null, error: error.message };
    }
  };

  const signup = async (email: string, password: string) => {
    if (!auth) {
      return { user: null, error: 'Firebase not initialized' };
    }
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      return { user: userCredential.user, error: null };
    } catch (error: any) {
      return { user: null, error: error.message };
    }
  };

  const signInWithGoogle = async () => {
    if (!auth) {
      return { user: null, error: 'Firebase not initialized' };
    }
    try {
      const provider = new GoogleAuthProvider();
      const userCredential = await signInWithPopup(auth, provider);
      return { user: userCredential.user, error: null };
    } catch (error: any) {
      return { user: null, error: error.message };
    }
  };

  const logout = async () => {
    if (!auth) {
      return { error: 'Firebase not initialized' };
    }
    try {
      await signOut(auth);
      return { error: null };
    } catch (error: any) {
      return { error: error.message };
    }
  };

  return {
    user,
    loading,
    login,
    signup,
    signInWithGoogle,
    logout,
    isAuthenticated: !!user,
  };
}

