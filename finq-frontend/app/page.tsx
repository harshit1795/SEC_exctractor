'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/hooks/useAuth';
import { useRouter } from 'next/navigation';
import Image from 'next/image';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSignUp, setIsSignUp] = useState(false);
  const [error, setError] = useState('');
  const [configError, setConfigError] = useState(false);
  const { login, signup, signInWithGoogle, user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Check if Firebase config is missing
    const apiKey = process.env.NEXT_PUBLIC_FIREBASE_API_KEY;
    if (!apiKey || apiKey === '') {
      setConfigError(true);
    }
  }, []);

  // Show loading while checking auth state
  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="mb-4 text-lg text-gray-600">Loading...</div>
        </div>
      </div>
    );
  }

  // Redirect if already logged in
  if (user) {
    router.push('/dashboard');
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const result = isSignUp
      ? await signup(email, password)
      : await login(email, password);

    if (result.error) {
      setError(result.error);
    } else {
      router.push('/dashboard');
    }
  };

  const handleGoogleSignIn = async () => {
    setError('');
    const result = await signInWithGoogle();
    if (result.error) {
      setError(result.error);
    } else {
      router.push('/dashboard');
    }
  };

  if (configError) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="w-full max-w-md rounded-lg bg-white p-8 shadow-xl">
          <div className="mb-8 text-center">
            <h1 className="text-3xl font-bold text-red-600">⚠️ Setup Required</h1>
            <p className="mt-4 text-gray-700">
              Firebase configuration is missing. Please set up your environment variables.
            </p>
            <div className="mt-6 rounded-lg bg-gray-100 p-4 text-left">
              <p className="mb-2 font-semibold text-gray-900">Steps to fix:</p>
              <ol className="list-decimal space-y-2 pl-5 text-sm text-gray-700">
                <li>Create <code className="rounded bg-gray-200 px-1">finq-frontend/.env.local</code></li>
                <li>Add your Firebase config from Firebase Console</li>
                <li>Restart the dev server: <code className="rounded bg-gray-200 px-1">npm run dev</code></li>
              </ol>
              <p className="mt-4 text-xs text-gray-600">
                See <code className="rounded bg-gray-200 px-1">QUICK_START.md</code> for details.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="w-full max-w-md rounded-lg bg-white p-8 shadow-xl">
        <div className="mb-8 text-center">
          <Image
            src="/FInQLogo.png"
            alt="FinQ Logo"
            width={200}
            height={200}
            className="mx-auto mb-4"
            onError={(e) => {
              // Hide image if it doesn't exist
              e.currentTarget.style.display = 'none';
            }}
          />
          <h1 className="text-3xl font-bold text-gray-900">Welcome to FinQ</h1>
          <p className="mt-2 text-gray-600">
            Personal Financial Intelligence & Analytics / AI Platform
          </p>
          <p className="mt-1 text-sm text-gray-500">
            Leverage and Connect with Leading Financial Information enhanced for
            use through AI
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600">
              {error}
            </div>
          )}

          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-700"
            >
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-700"
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
            />
          </div>

          <button
            type="submit"
            className="w-full rounded-md bg-blue-600 px-4 py-2 text-white transition-colors hover:bg-blue-700"
          >
            {isSignUp ? 'Sign Up' : 'Sign In'}
          </button>
        </form>

        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="bg-white px-2 text-gray-500">Or continue with</span>
          </div>
        </div>

        <button
          onClick={handleGoogleSignIn}
          className="w-full flex items-center justify-center gap-3 rounded-md border border-gray-300 bg-white px-4 py-2 text-gray-700 transition-colors hover:bg-gray-50"
        >
          <svg className="h-5 w-5" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            />
          </svg>
          <span>Sign in with Google</span>
        </button>

        <div className="mt-4 text-center">
          <button
            onClick={() => setIsSignUp(!isSignUp)}
            className="text-sm text-blue-600 hover:text-blue-700"
          >
            {isSignUp
              ? 'Already have an account? Sign in'
              : "Don't have an account? Sign up"}
          </button>
        </div>
      </div>
    </div>
  );
}
