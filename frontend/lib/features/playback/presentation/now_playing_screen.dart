import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:glass_kit/glass_kit.dart';
import 'package:frontend/core/theme/theme.dart';
import 'package:frontend/features/playback/presentation/playback_controller.dart';

class NowPlayingScreen extends ConsumerStatefulWidget {
  const NowPlayingScreen({super.key});

  @override
  ConsumerState<NowPlayingScreen> createState() => _NowPlayingScreenState();
}

class _NowPlayingScreenState extends ConsumerState<NowPlayingScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _rotationController;

  @override
  void initState() {
    super.initState();
    _rotationController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 15),
    );
  }

  @override
  void dispose() {
    _rotationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final playerState = ref.watch(playbackControllerProvider);
    final currentItem = playerState.currentItem;
    final isPlaying = playerState.playbackState?.playing ?? false;
    final isSpeech = currentItem?.extras?['type'] != 'song';

    // Start/Stop rotating vinyl based on play state
    if (isPlaying && !isSpeech) {
      _rotationController.repeat();
    } else {
      _rotationController.stop();
    }

    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.keyboard_arrow_down, color: Colors.white, size: 30),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text("Now Playing", style: TextStyle(color: Colors.white)),
        centerTitle: true,
      ),
      body: Stack(
        children: [
          // Dark background with neon blur circles
          Container(color: AppColors.background),
          Positioned(
            top: 100,
            left: -50,
            child: Container(
              width: 250,
              height: 250,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: (isSpeech ? AppColors.secondary : AppColors.primary).withOpacity(0.12),
                    blurRadius: 100,
                    spreadRadius: 50,
                  ),
                ],
              ),
            ),
          ),
          
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  // 1. Rotating Vinyl or AI Speech Graphic
                  Center(
                    child: isSpeech
                        ? _buildDJConsole(currentItem?.extras?['transcript'] ?? '', currentItem?.title ?? '')
                        : _buildRotatingVinyl(),
                  ),
                  
                  // 2. Track Titles
                  Column(
                    children: [
                      Text(
                        currentItem?.title ?? "Offline Station",
                        style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                        textAlign: TextAlign.center,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        currentItem?.artist ?? "Connect to a Station to start",
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: AppColors.secondary,
                          fontWeight: FontWeight.w600,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                  
                  // 3. Playback Controls & Progress Bar
                  Column(
                    children: [
                      // Progress Bar / Seek slider (Simplified mockup for Phase 2)
                      SliderTheme(
                        data: SliderTheme.of(context).copyWith(
                          activeTrackColor: AppColors.secondary,
                          inactiveTrackColor: AppColors.border,
                          thumbColor: Colors.white,
                          trackHeight: 4,
                          thumbShape: const RoundSliderOverlayShape(overlayRadius: 8),
                        ),
                        child: Slider(
                          value: 0.3,
                          onChanged: (val) {},
                        ),
                      ),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16.0),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text("0:45", style: TextStyle(color: AppColors.textSecondary, fontSize: 12)),
                            Text(
                              currentItem != null 
                                ? "${currentItem.duration?.inMinutes}:${(currentItem.duration!.inSeconds % 60).toString().padLeft(2, '0')}"
                                : "3:00", 
                              style: TextStyle(color: AppColors.textSecondary, fontSize: 12)
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 16),
                      
                      // Glassmorphism controls layout
                      GlassContainer.clearGlass(
                        height: 90,
                        width: double.infinity,
                        borderRadius: BorderRadius.circular(24),
                        borderColor: AppColors.border,
                        borderWidth: 1.0,
                        gradient: LinearGradient(
                          colors: [
                            AppColors.cardBackground.withOpacity(0.3),
                            AppColors.cardBackground.withOpacity(0.05),
                          ],
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                          children: [
                            IconButton(
                              icon: const Icon(Icons.skip_previous, size: 36, color: Colors.white),
                              onPressed: () => ref.read(playbackControllerProvider.notifier).skipToPrevious(),
                            ),
                            CircleAvatar(
                              radius: 30,
                              backgroundColor: AppColors.primary,
                              child: IconButton(
                                icon: Icon(
                                  isPlaying ? Icons.pause : Icons.play_arrow,
                                  size: 34,
                                  color: Colors.white,
                                ),
                                onPressed: () {
                                  final controller = ref.read(playbackControllerProvider.notifier);
                                  isPlaying ? controller.pause() : controller.play();
                                },
                              ),
                            ),
                            IconButton(
                              icon: const Icon(Icons.skip_next, size: 36, color: Colors.white),
                              onPressed: () => ref.read(playbackControllerProvider.notifier).skipToNext(),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRotatingVinyl() {
    return AnimatedBuilder(
      animation: _rotationController,
      builder: (context, child) {
        return Transform.rotate(
          angle: _rotationController.value * 2 * math.pi,
          child: child,
        );
      },
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Outer vinyl body
          Container(
            width: 260,
            height: 260,
            decoration: const BoxDecoration(
              shape: BoxShape.circle,
              color: Colors.black,
              boxShadow: [
                BoxShadow(
                  color: AppColors.primary,
                  blurRadius: 25,
                  spreadRadius: 2,
                )
              ]
            ),
          ),
          // Vinyl lines
          Container(
            width: 250,
            height: 250,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(color: Colors.white12, width: 2),
            ),
          ),
          Container(
            width: 200,
            height: 200,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(color: Colors.white10, width: 2.5),
            ),
          ),
          // Center album art sticker
          Container(
            width: 90,
            height: 90,
            decoration: const BoxDecoration(
              shape: BoxShape.circle,
              color: AppColors.secondary,
              image: DecorationImage(
                image: NetworkImage("https://images.unsplash.com/photo-1614613535308-eb5fbd3d2c17"),
                fit: BoxFit.cover,
              )
            ),
          ),
          // Vinyl center hole
          Container(
            width: 16,
            height: 16,
            decoration: const BoxDecoration(
              shape: BoxShape.circle,
              color: AppColors.background,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDJConsole(String transcript, String title) {
    return GlassContainer.clearGlass(
      height: 280,
      width: 280,
      borderRadius: BorderRadius.circular(24),
      borderColor: AppColors.secondary.withOpacity(0.5),
      borderWidth: 1.5,
      gradient: LinearGradient(
        colors: [
          AppColors.cardBackground.withOpacity(0.4),
          AppColors.cardBackground.withOpacity(0.1),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Waveform pulse/indicator
            const Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.mic, color: AppColors.secondary, size: 28),
                SizedBox(width: 8),
                Text(
                  "ON AIR",
                  style: TextStyle(
                    color: AppColors.secondary,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1.5,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              title,
              style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white, fontSize: 16),
            ),
            const SizedBox(height: 12),
            // DJ voice script scrollable area
            Expanded(
              child: SingleChildScrollView(
                child: Text(
                  transcript,
                  style: const TextStyle(
                    color: AppColors.textSecondary,
                    fontSize: 14,
                    height: 1.4,
                    fontStyle: FontStyle.italic,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
