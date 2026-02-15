import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:flutter_svg/flutter_svg.dart';
import 'auth_providers.dart';

class LoginPage extends ConsumerStatefulWidget {
  const LoginPage({super.key});

  @override
  ConsumerState<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends ConsumerState<LoginPage> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLogin = true;
  bool _isBusy = false;
  String? _errorMessage;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleSubmit() async {
    setState(() {
      _errorMessage = null;
      _isBusy = true;
    });

    final controller = ref.read(authControllerProvider);
    final email = _emailController.text;
    final password = _passwordController.text;

    final result = _isLogin
        ? await controller.signInWithEmail(email, password)
        : await controller.signUpWithEmail(email, password);

    if (!mounted) {
      return;
    }

    setState(() {
      _isBusy = false;
      _errorMessage = result.error;
    });
  }

  @override
  Widget build(BuildContext context) {
    final firebaseReady = Firebase.apps.isNotEmpty;
    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 380),
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  SvgPicture.asset(
                    'assets/FinQLogoNew.svg',
                    height: 120,
                    fit: BoxFit.contain,
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'Enhancing Financial Analysis leveraging AI',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
                      color: Colors.black54,
                      fontStyle: FontStyle.italic,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 24),
                  Text(
                    _isLogin ? 'Sign in to continue' : 'Create your account',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.grey.shade600),
                  ),
                  const SizedBox(height: 24),
                  if (!firebaseReady)
                    const _FirebaseConfigNotice(),
                  TextField(
                    controller: _emailController,
                    decoration: const InputDecoration(labelText: 'Email'),
                    keyboardType: TextInputType.emailAddress,
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _passwordController,
                    decoration: const InputDecoration(labelText: 'Password'),
                    obscureText: true,
                  ),
                  const SizedBox(height: 16),
                  if (_errorMessage != null)
                    Text(
                      _errorMessage ?? '',
                      style: TextStyle(color: Colors.red.shade700),
                    ),
                  const SizedBox(height: 12),
                  ElevatedButton(
                    onPressed: _isBusy || !firebaseReady ? null : _handleSubmit,
                    child: Text(_isLogin ? 'Sign In' : 'Sign Up'),
                  ),
                  const SizedBox(height: 8),
                  OutlinedButton.icon(
                    onPressed: _isBusy || !firebaseReady
                        ? null
                        : () async {
                            setState(() {
                              _errorMessage = null;
                              _isBusy = true;
                              });
                            final result = await ref
                                .read(authControllerProvider)
                                .signInWithGoogle();
                            if (!mounted) {
                              return;
                            }
                            setState(() {
                              _isBusy = false;
                              _errorMessage = result.error;
                            });
                          },
                    icon: const Icon(Icons.login),
                    label: const Text('Continue with Google'),
                  ),
                  TextButton(
                    onPressed: _isBusy
                        ? null
                        : () => setState(() => _isLogin = !_isLogin),
                    child: Text(
                      _isLogin
                          ? 'Need an account? Sign up'
                          : 'Have an account? Sign in',
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _FirebaseConfigNotice extends StatelessWidget {
  const _FirebaseConfigNotice();

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.amber.shade100,
        borderRadius: BorderRadius.circular(8),
      ),
      child: const Text(
        'Firebase is not initialized. For web, pass FIREBASE_* values via '
        '--dart-define. For mobile, run flutterfire configure.',
      ),
    );
  }
}
