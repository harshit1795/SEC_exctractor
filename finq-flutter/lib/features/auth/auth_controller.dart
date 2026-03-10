import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/foundation.dart';
import 'package:google_sign_in/google_sign_in.dart';

class AuthResult {
  AuthResult({this.user, this.error});

  final User? user;
  final String? error;
}

class AuthController {
  AuthController({FirebaseAuth? firebaseAuth})
      : _firebaseAuth = firebaseAuth ??
            (Firebase.apps.isNotEmpty ? FirebaseAuth.instance : null);

  final FirebaseAuth? _firebaseAuth;

  Future<AuthResult> signInWithEmail(String email, String password) async {
    final auth = _firebaseAuth;
    if (auth == null) {
      return AuthResult(error: 'Firebase not initialized');
    }
    final normalizedEmail = _normalizeEmail(email);
    if (normalizedEmail == null) {
      return AuthResult(error: 'Please enter a valid email address.');
    }
    if (password.isEmpty) {
      return AuthResult(error: 'Please enter your password.');
    }
    try {
      await _ensureWebPersistence(auth);
      final credential = await auth.signInWithEmailAndPassword(
        email: normalizedEmail,
        password: password,
      );
      return AuthResult(user: credential.user);
    } on FirebaseAuthException catch (error) {
      return AuthResult(error: _mapAuthError(error));
    } catch (error) {
      return AuthResult(error: error.toString());
    }
  }

  Future<AuthResult> signUpWithEmail(String email, String password) async {
    final auth = _firebaseAuth;
    if (auth == null) {
      return AuthResult(error: 'Firebase not initialized');
    }
    final normalizedEmail = _normalizeEmail(email);
    if (normalizedEmail == null) {
      return AuthResult(error: 'Please enter a valid email address.');
    }
    if (password.isEmpty) {
      return AuthResult(error: 'Please enter a password.');
    }
    try {
      await _ensureWebPersistence(auth);
      final credential = await auth.createUserWithEmailAndPassword(
        email: normalizedEmail,
        password: password,
      );
      return AuthResult(user: credential.user);
    } on FirebaseAuthException catch (error) {
      return AuthResult(error: _mapAuthError(error));
    } catch (error) {
      return AuthResult(error: error.toString());
    }
  }

  Future<void> signOut() async {
    final auth = _firebaseAuth;
    if (auth == null) {
      return;
    }
    await auth.signOut();
  }

  Future<AuthResult> signInWithGoogle() async {
    final auth = _firebaseAuth;
    if (auth == null) {
      return AuthResult(error: 'Firebase not initialized');
    }
    try {
      await _ensureWebPersistence(auth);
      if (kIsWeb) {
        final provider = GoogleAuthProvider();
        final credential = await auth.signInWithPopup(provider);
        return AuthResult(user: credential.user);
      }

      final googleUser = await GoogleSignIn().signIn();
      if (googleUser == null) {
        return AuthResult(error: 'Google sign-in cancelled');
      }
      final googleAuth = await googleUser.authentication;
      final credential = GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken,
        idToken: googleAuth.idToken,
      );
      final userCredential = await auth.signInWithCredential(credential);
      return AuthResult(user: userCredential.user);
    } on FirebaseAuthException catch (error) {
      return AuthResult(error: error.message ?? error.code);
    } catch (error) {
      return AuthResult(error: error.toString());
    }
  }

  Future<void> _ensureWebPersistence(FirebaseAuth auth) async {
    if (!kIsWeb) {
      return;
    }
    try {
      await auth.setPersistence(Persistence.LOCAL);
    } catch (_) {
      // Ignore persistence errors; auth can still work in-memory.
    }
  }

  String? _normalizeEmail(String email) {
    final normalized = email.trim().toLowerCase();
    if (normalized.isEmpty || !normalized.contains('@')) {
      return null;
    }
    return normalized;
  }

  String _mapAuthError(FirebaseAuthException error) {
    switch (error.code) {
      case 'user-not-found':
      case 'invalid-credential':
        return 'No account found for that email.';
      case 'wrong-password':
        return 'Incorrect password.';
      case 'invalid-email':
        return 'That email address is invalid.';
      case 'email-already-in-use':
        return 'That email is already registered.';
      case 'operation-not-allowed':
        return 'Email/password sign-in is disabled in Firebase.';
      case 'weak-password':
        return 'Password is too weak (min 6 characters).';
      default:
        return error.message ?? error.code;
    }
  }
}
