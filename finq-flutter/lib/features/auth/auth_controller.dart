import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';

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
    try {
      final credential = await auth.signInWithEmailAndPassword(
        email: email,
        password: password,
      );
      return AuthResult(user: credential.user);
    } on FirebaseAuthException catch (error) {
      return AuthResult(error: error.message ?? error.code);
    } catch (error) {
      return AuthResult(error: error.toString());
    }
  }

  Future<AuthResult> signUpWithEmail(String email, String password) async {
    final auth = _firebaseAuth;
    if (auth == null) {
      return AuthResult(error: 'Firebase not initialized');
    }
    try {
      final credential = await auth.createUserWithEmailAndPassword(
        email: email,
        password: password,
      );
      return AuthResult(user: credential.user);
    } on FirebaseAuthException catch (error) {
      return AuthResult(error: error.message ?? error.code);
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
}
