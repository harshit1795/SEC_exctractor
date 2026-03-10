import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';

import 'auth_service.dart';

class FirebaseAuthService implements AuthService {
  FirebaseAuthService({FirebaseAuth? firebaseAuth})
      : _firebaseAuth = firebaseAuth ??
            (Firebase.apps.isNotEmpty ? FirebaseAuth.instance : null);

  final FirebaseAuth? _firebaseAuth;

  @override
  Future<String?> getIdToken() async {
    final auth = _firebaseAuth;
    if (auth == null) {
      return null;
    }
    final user = auth.currentUser;
    if (user == null) {
      return null;
    }
    return user.getIdToken();
  }

  @override
  Stream<bool> authStateChanges() {
    final auth = _firebaseAuth;
    if (auth == null) {
      return Stream<bool>.value(false);
    }
    return auth.authStateChanges().map((user) => user != null);
  }
}
