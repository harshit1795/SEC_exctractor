abstract class AuthService {
  Future<String?> getIdToken();
  Stream<bool> authStateChanges();
}
