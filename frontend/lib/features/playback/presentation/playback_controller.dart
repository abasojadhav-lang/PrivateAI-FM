import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:audio_service/audio_service.dart';
import 'package:frontend/features/playback/data/audio_handler.dart';
import 'package:frontend/features/playback/data/playback_repository.dart';
import 'package:frontend/core/services/location_service.dart';

final audioHandlerProvider = Provider<AudioHandler>((ref) {
  throw UnimplementedError("Initialize audioHandlerProvider override in main.dart");
});

class PlayerStateWrapper {
  final PlaybackState? playbackState;
  final MediaItem? currentItem;
  final List<MediaItem> queue;
  final bool isLoading;

  PlayerStateWrapper({
    this.playbackState,
    this.currentItem,
    this.queue = const [],
    this.isLoading = false,
  });

  PlayerStateWrapper copyWith({
    PlaybackState? playbackState,
    MediaItem? currentItem,
    List<MediaItem>? queue,
    bool? isLoading,
  }) {
    return PlayerStateWrapper(
      playbackState: playbackState ?? this.playbackState,
      currentItem: currentItem ?? this.currentItem,
      queue: queue ?? this.queue,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

class PlaybackController extends StateNotifier<PlayerStateWrapper> {
  final AudioHandler _audioHandler;
  final PlaybackRepository _repository;

  PlaybackController(this._audioHandler, this._repository) : super(PlayerStateWrapper()) {
    _listenToAudioHandler();
  }

  void _listenToAudioHandler() {
    // Listen to media item updates
    _audioHandler.mediaItem.listen((item) {
      if (item != null) {
        state = state.copyWith(currentItem: item);
        
        // Log telemetry: if it's a song, record history
        final isSong = item.extras?['type'] == 'song';
        if (isSong) {
          final id = int.tryParse(item.id) ?? 0;
          _repository.recordPlaybackHistory(id, false, 0);
        }
      }
    });

    // Listen to playback states
    _audioHandler.playbackState.listen((playbackState) {
      state = state.copyWith(playbackState: playbackState);
    });

    // Listen to queue changes
    _audioHandler.queue.listen((queueList) {
      state = state.copyWith(queue: queueList);
    });
  }

  Future<void> loadStationQueue(int? stationId) async {
    state = state.copyWith(isLoading: true);
    
    // Fetch GPS coordinates
    final position = await LocationService.getCurrentPosition();
    final lat = position?.latitude;
    final lon = position?.longitude;

    final items = await _repository.fetchQueue(
      stationId: stationId,
      lat: lat,
      lon: lon,
    );
    
    if (items.isNotEmpty) {
      // Pass the items to MyAudioHandler
      final myHandler = _audioHandler as MyAudioHandler;
      await myHandler.updateQueueItems(items);
      
      // Auto start playback
      await _audioHandler.play();
    }
    state = state.copyWith(isLoading: false);
  }

  Future<void> play() => _audioHandler.play();
  Future<void> pause() => _audioHandler.pause();
  Future<void> skipToNext() => _audioHandler.skipToNext();
  Future<void> skipToPrevious() => _audioHandler.skipToPrevious();
  Future<void> seek(Duration position) => _audioHandler.seek(position);
}

final playbackControllerProvider = StateNotifierProvider<PlaybackController, PlayerStateWrapper>((ref) {
  final handler = ref.watch(audioHandlerProvider);
  final repo = ref.watch(playbackRepositoryProvider);
  return PlaybackController(handler, repo);
});
