import 'package:audio_service/audio_service.dart';
import 'package:just_audio/just_audio.dart';

Future<AudioHandler> initAudioService() async {
  return await AudioService.init(
    builder: () => MyAudioHandler(),
    config: const AudioServiceConfig(
      androidNotificationChannelId: 'com.privatefm.ai.channel.audio',
      androidNotificationChannelName: 'PrivateFM AI Playback',
      androidNotificationOngoing: true,
      androidShowNotificationBadge: true,
    ),
  );
}

class MyAudioHandler extends BaseAudioHandler with QueueHandler, SeekHandler {
  final AudioPlayer _player = AudioPlayer();
  final _playlist = ConcatenatingAudioSource(children: []);

  MyAudioHandler() {
    _init();
  }

  void _init() {
    // Forward just_audio player state changes to audio_service
    _player.playbackEventStream.map(_transformEvent).pipe(playbackState);

    // Track current item index change
    _player.currentIndexStream.listen((index) {
      if (index != null && queue.value.isNotEmpty) {
        mediaItem.add(queue.value[index]);
      }
    });

    // Setup audio source playlist
    _player.setAudioSource(_playlist);
  }

  Future<void> updateQueueItems(List<MediaItem> items) async {
    // Clear old items and add new ones
    await _playlist.clear();
    queue.add(items);
    
    for (var item in items) {
      _playlist.add(AudioSource.uri(
        Uri.parse(item.extras?['stream_url'] ?? ''),
        tag: item,
      ));
    }
  }

  @override
  Future<void> play() => _player.play();

  @override
  Future<void> pause() => _player.pause();

  @override
  Future<void> seek(Duration position) => _player.seek(position);

  @override
  Future<void> skipToNext() => _player.seekToNext();

  @override
  Future<void> skipToPrevious() => _player.seekToPrevious();

  @override
  Future<void> stop() async {
    await _player.stop();
    await playbackState.firstWhere((state) => state.processingState == AudioProcessingState.idle);
  }

  PlaybackState _transformEvent(PlaybackEvent event) {
    return PlaybackState(
      controls: [
        MediaControl.skipToPrevious,
        if (_player.playing) MediaControl.pause else MediaControl.play,
        MediaControl.stop,
        MediaControl.skipToNext,
      ],
      systemActions: const {
        MediaAction.seek,
        MediaAction.seekForward,
        MediaAction.seekBackward,
      },
      androidCompactActionIndices: const [0, 1, 3],
      processingState: const {
        ProcessingState.idle: AudioProcessingState.idle,
        ProcessingState.loading: AudioProcessingState.loading,
        ProcessingState.buffering: AudioProcessingState.buffering,
        ProcessingState.ready: AudioProcessingState.ready,
        ProcessingState.completed: AudioProcessingState.completed,
      }[_player.processingState]!,
      playing: _player.playing,
      updatePosition: _player.position,
      bufferedPosition: _player.bufferedPosition,
      speed: _player.speed,
      queueIndex: event.currentIndex,
    );
  }
}
