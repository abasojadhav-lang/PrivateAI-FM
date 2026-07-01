import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/features/auth/data/auth_repository.dart';

enum AuthStatus { initial, loading, authenticated, unauthenticated, error }

class AuthState {
  final AuthStatus status;
  final String? errorMessage;
  final Map<String, dynamic>? user;

  AuthState({
    required this.status,
    this.errorMessage,
    this.user,
  });

  factory AuthState.initial() => AuthState(status: AuthStatus.initial);

  AuthState copyWith({
    AuthStatus? status,
    String? errorMessage,
    Map<String, dynamic>? user,
  }) {
    return AuthState(
      status: status ?? this.status,
      errorMessage: errorMessage ?? this.errorMessage,
      user: user ?? this.user,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  final AuthRepository _repository;

  AuthNotifier(this._repository) : super(AuthState.initial()) {
    checkAuthentication();
  }

  Future<void> checkAuthentication() async {
    final hasToken = await _repository.isAuthenticated();
    if (hasToken) {
      final user = await _repository.getCurrentUser();
      if (user != null) {
        state = AuthState(status: AuthStatus.authenticated, user: user);
        return;
      }
    }
    state = AuthState(status: AuthStatus.unauthenticated);
  }

  Future<void> login(String email, String password) async {
    state = state.copyWith(status: AuthStatus.loading);
    final result = await _repository.login(email, password);
    if (result["success"]) {
      final user = await _repository.getCurrentUser();
      state = AuthState(status: AuthStatus.authenticated, user: user);
    } else {
      state = AuthState(
        status: AuthStatus.unauthenticated,
        errorMessage: result["error"],
      );
    }
  }

  Future<void> register(String email, String password) async {
    state = state.copyWith(status: AuthStatus.loading);
    final result = await _repository.register(email, password);
    if (result["success"]) {
      // Auto login after registration
      await login(email, password);
    } else {
      state = AuthState(
        status: AuthStatus.unauthenticated,
        errorMessage: result["error"],
      );
    }
  }

  Future<void> logout() async {
    await _repository.logout();
    state = AuthState(status: AuthStatus.unauthenticated);
  }
}

final authControllerProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final repo = ref.watch(authRepositoryProvider);
  return AuthNotifier(repo);
});
