import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:glass_kit/glass_kit.dart';
import 'package:frontend/core/theme/theme.dart';
import 'package:frontend/features/auth/presentation/auth_controller.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  
  bool _isSignUp = false;
  bool _obscurePassword = true;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  void _submitForm() {
    if (_formKey.currentState!.validate()) {
      final authController = ref.read(authControllerProvider.notifier);
      if (_isSignUp) {
        authController.register(_emailController.text.trim(), _passwordController.text.trim());
      } else {
        authController.login(_emailController.text.trim(), _passwordController.text.trim());
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authControllerProvider);
    
    // Show error toast if any
    if (authState.errorMessage != null) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(authState.errorMessage!),
            backgroundColor: AppColors.error,
          ),
        );
      });
    }

    return Scaffold(
      body: Stack(
        children: [
          // Background neon gradients
          Container(color: AppColors.background),
          Positioned(
            top: -100,
            left: -100,
            child: Container(
              width: 300,
              height: 300,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: AppColors.primary.withOpacity(0.15),
                    blurRadius: 100,
                    spreadRadius: 50,
                  ),
                ],
              ),
            ),
          ),
          Positioned(
            bottom: -50,
            right: -50,
            child: Container(
              width: 350,
              height: 350,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: AppColors.secondary.withOpacity(0.12),
                    blurRadius: 120,
                    spreadRadius: 60,
                  ),
                ],
              ),
            ),
          ),
          
          // Content
          Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 24.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Funny Music Peon Mascot Logo
                  Hero(
                    tag: 'music_peon_logo',
                    child: Image.asset(
                      'assets/images/music_peon_logo.png',
                      height: 140,
                      width: 140,
                      errorBuilder: (context, error, stackTrace) => Container(
                        height: 120,
                        width: 120,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: AppColors.cardBackground,
                          border: Border.all(color: AppColors.border),
                        ),
                        child: const Icon(Icons.music_note, size: 60, color: AppColors.secondary),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  
                  // App Title
                  Text(
                    "PrivateFM AI",
                    style: Theme.of(context).textTheme.displayLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1.2,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    "Your Personal AI Radio Station",
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                  const SizedBox(height: 32),
                  
                  // Glassmorphism login card
                  GlassContainer.clearGlass(
                    height: 400,
                    width: double.infinity,
                    borderRadius: BorderRadius.circular(28),
                    borderWidth: 1.0,
                    borderColor: AppColors.border,
                    gradient: LinearGradient(
                      colors: [
                        AppColors.cardBackground.withOpacity(0.6),
                        AppColors.cardBackground.withOpacity(0.1),
                      ],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(24.0),
                      child: Form(
                        key: _formKey,
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            Text(
                              _isSignUp ? "Create Account" : "Welcome Back",
                              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                                color: Colors.white,
                              ),
                              textAlign: TextAlign.center,
                            ),
                            const SizedBox(height: 24),
                            
                            // Email input field
                            TextFormField(
                              controller: _emailController,
                              keyboardType: TextInputType.emailAddress,
                              decoration: const InputDecoration(
                                labelText: "Email",
                                prefixIcon: Icon(Icons.mail_outline, color: AppColors.textSecondary),
                              ),
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return "Please enter your email";
                                }
                                if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value)) {
                                  return "Please enter a valid email address";
                                }
                                return null;
                              },
                            ),
                            const SizedBox(height: 16),
                            
                            // Password input field
                            TextFormField(
                              controller: _passwordController,
                              obscureText: _obscurePassword,
                              decoration: InputDecoration(
                                labelText: "Password",
                                prefixIcon: const Icon(Icons.lock_outline, color: AppColors.textSecondary),
                                suffixIcon: IconButton(
                                  icon: Icon(
                                    _obscurePassword ? Icons.visibility_off_outlined : Icons.visibility_outlined,
                                    color: AppColors.textSecondary,
                                  ),
                                  onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                                ),
                              ),
                              validator: (value) {
                                if (value == null || value.isEmpty) {
                                  return "Please enter your password";
                                }
                                if (value.length < 6) {
                                  return "Password must be at least 6 characters long";
                                }
                                return null;
                              },
                            ),
                            const SizedBox(height: 24),
                            
                            // Actions
                            authState.status == AuthStatus.loading
                                ? const Center(child: CircularProgressIndicator(color: AppColors.secondary))
                                : ElevatedButton(
                                    onPressed: _submitForm,
                                    child: Text(_isSignUp ? "Sign Up" : "Log In"),
                                  ),
                          ],
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  
                  // Toggle button between signup/login
                  TextButton(
                    onPressed: () {
                      setState(() {
                        _isSignUp = !_isSignUp;
                        _formKey.currentState?.reset();
                        _emailController.clear();
                        _passwordController.clear();
                      });
                    },
                    child: Text(
                      _isSignUp
                          ? "Already have an account? Log In"
                          : "Don't have an account? Sign Up",
                      style: const TextStyle(
                        color: AppColors.secondary,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
