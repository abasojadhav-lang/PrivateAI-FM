import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:frontend/core/theme/theme.dart';
import 'package:frontend/features/auth/presentation/auth_controller.dart';
import 'package:frontend/features/auth/presentation/login_screen.dart';
import 'package:frontend/features/home/presentation/home_screen.dart';
import 'package:frontend/features/playback/data/audio_handler.dart';
import 'package:frontend/features/playback/presentation/playback_controller.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final audioHandler = await initAudioService();
  
  runApp(
    ProviderScope(
      overrides: [
        audioHandlerProvider.overrideWithValue(audioHandler),
      ],
      child: const PrivateFMAIApp(),
    ),
  );
}


class PrivateFMAIApp extends ConsumerWidget {
  const PrivateFMAIApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authControllerProvider);

    final router = GoRouter(
      initialLocation: '/',
      redirect: (context, state) {
        final status = authState.status;
        
        // Wait until initial auth check has completed
        if (status == AuthStatus.initial) {
          return null;
        }

        final isLoggingIn = state.matchedLocation == '/login';
        final isAuth = status == AuthStatus.authenticated;

        if (!isAuth && !isLoggingIn) {
          return '/login';
        }
        if (isAuth && isLoggingIn) {
          return '/';
        }
        return null;
      },
      routes: [
        GoRoute(
          path: '/',
          builder: (context, state) => const HomeScreen(),
        ),
        GoRoute(
          path: '/login',
          builder: (context, state) => const LoginScreen(),
        ),
      ],
    );

    return MaterialApp.router(
      title: 'PrivateFM AI',
      theme: AppTheme.darkTheme,
      routerConfig: router,
      debugShowCheckedModeBanner: false,
    );
  }
}
