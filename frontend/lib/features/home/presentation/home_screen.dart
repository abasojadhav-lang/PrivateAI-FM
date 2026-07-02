import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:glass_kit/glass_kit.dart';
import 'package:frontend/core/theme/theme.dart';
import 'package:frontend/features/auth/presentation/auth_controller.dart';
import 'package:frontend/features/playback/presentation/playback_controller.dart';
import 'package:frontend/features/playback/presentation/now_playing_screen.dart';
import 'package:frontend/features/stations/presentation/station_controller.dart';
import 'package:frontend/features/stations/presentation/station_wizard_screen.dart';
import 'package:frontend/features/playback/data/playback_repository.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authControllerProvider);
    final userEmail = authState.user?['email'] ?? 'Listener';
    final stationState = ref.watch(stationControllerProvider);
    final stations = stationState.stations;

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: Text(
          "PrivateFM AI",
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
            letterSpacing: 1.1,
            color: Colors.white,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.library_music, color: AppColors.primary),
            tooltip: "Add a Song",
            onPressed: () {
              _showAddSongDialog(context, ref);
            },
          ),
          IconButton(
            icon: const Icon(Icons.logout, color: AppColors.textSecondary),
            onPressed: () {
              ref.read(authControllerProvider.notifier).logout();
            },
          )
        ],
      ),
      extendBodyBehindAppBar: true,
      body: Stack(
        children: [
          // Background neon gradients
          Container(color: AppColors.background),
          Positioned(
            top: -150,
            right: -50,
            child: Container(
              width: 300,
              height: 300,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: AppColors.primary.withOpacity(0.12),
                    blurRadius: 100,
                    spreadRadius: 50,
                  ),
                ],
              ),
            ),
          ),
          Positioned(
            bottom: -100,
            left: -50,
            child: Container(
              width: 350,
              height: 350,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: AppColors.secondary.withOpacity(0.1),
                    blurRadius: 120,
                    spreadRadius: 60,
                  ),
                ],
              ),
            ),
          ),
          
          // Content
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SizedBox(height: 20),
                  // User Greeting Header
                  Row(
                    children: [
                      CircleAvatar(
                        radius: 26,
                        backgroundColor: AppColors.primary,
                        child: Text(
                          userEmail[0].toUpperCase(),
                          style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white, fontSize: 18),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            "Welcome Back,",
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                          Text(
                            userEmail.split('@')[0],
                            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      )
                    ],
                  ),
                  const SizedBox(height: 40),
                  
                  Expanded(
                    child: stationState.isLoading
                        ? const Center(child: CircularProgressIndicator(color: AppColors.secondary))
                        : stations.isEmpty
                            ? _buildEmptyState(context)
                            : _buildStationsList(context, ref, stations, stationState.activeStation),
                  ),
                ],
              ),
            ),
          )
        ],
      ),
      floatingActionButton: stations.isNotEmpty
          ? FloatingActionButton(
              backgroundColor: AppColors.primary,
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const StationWizardScreen()),
              ),
              child: const Icon(Icons.add, color: Colors.white),
            )
          : null,
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        GlassContainer.clearGlass(
          height: 280,
          width: double.infinity,
          borderRadius: BorderRadius.circular(24),
          borderColor: AppColors.border,
          borderWidth: 1.0,
          gradient: LinearGradient(
            colors: [
              AppColors.cardBackground.withOpacity(0.4),
              AppColors.cardBackground.withOpacity(0.1),
            ],
          ),
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(
                  Icons.radio_outlined,
                  size: 64,
                  color: AppColors.secondary,
                ),
                const SizedBox(height: 20),
                Text(
                  "No stations created yet",
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 10),
                Text(
                  "Your Music Peon is waiting for instructions. Create your first station to start listening!",
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 32),
        ElevatedButton.icon(
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => const StationWizardScreen()),
            );
          },
          icon: const Icon(Icons.add),
          label: const Text("Create AI Station"),
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.symmetric(vertical: 18, horizontal: 36),
          ),
        ),
      ],
    );
  }

  Widget _buildStationsList(
    BuildContext context,
    WidgetRef ref,
    List<Map<String, dynamic>> stations,
    Map<String, dynamic>? activeStation,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          "Your Stations",
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.bold,
            color: Colors.white70,
          ),
        ),
        const SizedBox(height: 16),
        Expanded(
          child: ListView.builder(
            itemCount: stations.length,
            itemBuilder: (context, index) {
              final station = stations[index];
              final isPlaying = activeStation?['id'] == station['id'];
              final djConfig = station['voice_config'] ?? {};
              final personality = djConfig['personality'] ?? 'Friendly';
              
              return Padding(
                padding: const EdgeInsets.only(bottom: 16.0),
                child: GlassContainer.clearGlass(
                  height: 100,
                  width: double.infinity,
                  borderRadius: BorderRadius.circular(20),
                  borderColor: isPlaying ? AppColors.secondary : AppColors.border,
                  borderWidth: isPlaying ? 1.5 : 1.0,
                  gradient: LinearGradient(
                    colors: [
                      isPlaying
                          ? AppColors.primary.withOpacity(0.2)
                          : AppColors.cardBackground.withOpacity(0.4),
                      AppColors.cardBackground.withOpacity(0.1),
                    ],
                  ),
                  child: ListTile(
                    contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                    leading: CircleAvatar(
                      backgroundColor: isPlaying ? AppColors.secondary : AppColors.cardBackground,
                      child: Icon(
                        isPlaying ? Icons.play_arrow : Icons.radio,
                        color: isPlaying ? Colors.black : AppColors.textSecondary,
                      ),
                    ),
                    title: Text(
                      station['name'] ?? 'Custom Station',
                      style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white, fontSize: 16),
                    ),
                    subtitle: Text(
                      "Mood: ${station['mood'] ?? 'Neutral'} • DJ: $personality",
                      style: const TextStyle(color: AppColors.textSecondary, fontSize: 12),
                    ),
                    trailing: IconButton(
                      icon: const Icon(Icons.delete_outline, color: AppColors.error),
                      onPressed: () {
                        // Confirm deletion
                        showDialog(
                          context: context,
                          builder: (context) => AlertDialog(
                            title: const Text("Delete Station?"),
                            content: const Text("Are you sure you want to delete this station?"),
                            actions: [
                              TextButton(
                                onPressed: () => Navigator.pop(context),
                                child: const Text("Cancel"),
                              ),
                              TextButton(
                                onPressed: () {
                                  ref.read(stationControllerProvider.notifier).deleteStation(station['id']);
                                  Navigator.pop(context);
                                },
                                child: const Text("Delete", style: TextStyle(color: AppColors.error)),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
                    onTap: () {
                      // Set active station
                      ref.read(stationControllerProvider.notifier).setActiveStation(station);
                      // Open player
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => const NowPlayingScreen()),
                      );
                    },
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  void _showAddSongDialog(BuildContext context, WidgetRef ref) {
    final titleController = TextEditingController();
    final artistController = TextEditingController();
    final youtubeController = TextEditingController();
    final coverController = TextEditingController();
    final formKey = GlobalKey<FormState>();
    var isLoading = false;

    showDialog(
      context: context,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              backgroundColor: AppColors.background,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(20),
                side: BorderSide(color: AppColors.primary.withOpacity(0.3)),
              ),
              title: const Text(
                "Add Song to Library",
                style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
              ),
              content: Form(
                key: formKey,
                child: SingleChildScrollView(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      TextFormField(
                        controller: titleController,
                        style: const TextStyle(color: Colors.white),
                        decoration: const InputDecoration(
                          labelText: "Song Title *",
                          labelStyle: TextStyle(color: AppColors.textSecondary),
                        ),
                        validator: (value) => (value == null || value.trim().isEmpty) ? "Required" : null,
                      ),
                      const SizedBox(height: 10),
                      TextFormField(
                        controller: artistController,
                        style: const TextStyle(color: Colors.white),
                        decoration: const InputDecoration(
                          labelText: "Artist Name *",
                          labelStyle: TextStyle(color: AppColors.textSecondary),
                        ),
                        validator: (value) => (value == null || value.trim().isEmpty) ? "Required" : null,
                      ),
                      const SizedBox(height: 10),
                      TextFormField(
                        controller: youtubeController,
                        style: const TextStyle(color: Colors.white),
                        decoration: const InputDecoration(
                          labelText: "YouTube Video ID (Optional)",
                          labelStyle: TextStyle(color: AppColors.textSecondary),
                          helperText: "e.g. dQw4w9WgXcQ",
                          helperStyle: TextStyle(color: AppColors.textSecondary),
                        ),
                      ),
                      const SizedBox(height: 10),
                      TextFormField(
                        controller: coverController,
                        style: const TextStyle(color: Colors.white),
                        decoration: const InputDecoration(
                          labelText: "Cover Image URL (Optional)",
                          labelStyle: TextStyle(color: AppColors.textSecondary),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              actions: [
                TextButton(
                  onPressed: isLoading ? null : () => Navigator.of(context).pop(),
                  child: const Text("Cancel", style: TextStyle(color: AppColors.textSecondary)),
                ),
                ElevatedButton(
                  onPressed: isLoading
                      ? null
                      : () async {
                          if (formKey.currentState?.validate() == true) {
                            setState(() {
                              isLoading = true;
                            });
                            try {
                              await ref.read(playbackRepositoryProvider).linkCatalogSong(
                                    title: titleController.text,
                                    artist: artistController.text,
                                    youtubeId: youtubeController.text,
                                    coverUrl: coverController.text,
                                  );
                              Navigator.of(context).pop();
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text("Song added successfully!")),
                              );
                            } catch (e) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text("Failed to add song: ${e.toString()}")),
                              );
                            } finally {
                              setState(() {
                                isLoading = false;
                              });
                            }
                          }
                        },
                  style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary),
                  child: isLoading
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                        )
                      : const Text("Add"),
                ),
              ],
            );
          },
        );
      },
    );
  }
}
