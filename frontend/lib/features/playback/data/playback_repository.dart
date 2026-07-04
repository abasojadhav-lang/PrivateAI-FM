import 'package:dio/dio.dart';
import 'package:audio_service/audio_service.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/features/auth/data/auth_repository.dart';

final playbackRepositoryProvider = Provider((ref) {
  final dio = Dio(BaseOptions(
    baseUrl: const String.fromEnvironment('API_BASE_URL', defaultValue: 'http://localhost:8000'),
    connectTimeout: const Duration(seconds: 5),
    receiveTimeout: const Duration(seconds: 5),
  ));
  
  // Inject auth repository token helper via interceptor
  final authRepo = ref.watch(authRepositoryProvider);
  dio.interceptors.add(InterceptorsWrapper(
    onRequest: (options, handler) async {
      final token = await authRepo.getToken();
      if (token != null) {
        options.headers["Authorization"] = "Bearer $token";
      }
      return handler.next(options);
    },
  ));

  return PlaybackRepository(dio);
});

class PlaybackRepository {
  final Dio _dio;

  PlaybackRepository(this._dio);

  Future<List<MediaItem>> fetchQueue({int? stationId, double? lat, double? lon}) async {
    try {
      final queryParams = <String, dynamic>{};
      if (stationId != null) queryParams["station_id"] = stationId;
      if (lat != null) queryParams["lat"] = lat;
      if (lon != null) queryParams["lon"] = lon;

      final response = await _dio.get(
        "/api/playback/queue",
        queryParameters: queryParams,
      );
      
      final List<dynamic> data = response.data;
      return data.map((item) {
        final rawStreamUrl = item["stream_url"] as String?;
        final resolvedStreamUrl = (rawStreamUrl == null || rawStreamUrl.isEmpty)
            ? ""
            : (rawStreamUrl.startsWith("http")
                ? rawStreamUrl
                : "${_dio.options.baseUrl}$rawStreamUrl");

        return MediaItem(
          id: item["id"].toString(),
          album: item["album"],
          title: item["title"],
          artist: item["artist"],
          duration: Duration(seconds: item["duration"]),
          artUri: Uri.parse(item["cover_url"]),
          extras: {
            "queue_id": item["queue_id"],
            "type": item["type"],
            "stream_url": resolvedStreamUrl,
            "transcript": item["transcript"]
          },
        );
      }).toList();
    } catch (e) {
      // Fallback local mock media items if backend query fails completely
      return [
        const MediaItem(
          id: "1001",
          album: "After Hours",
          title: "Blinding Lights",
          artist: "The Weeknd",
          duration: Duration(seconds: 200),
          artUri: null,
          extras: {
            "queue_id": "song_0",
            "type": "song",
            "stream_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
            "transcript": ""
          },
        ),
        const MediaItem(
          id: "2001",
          album: "Radio Broadcast",
          title: "AI DJ Commentary",
          artist: "AI Radio Service",
          duration: Duration(seconds: 6),
          artUri: null,
          extras: {
            "queue_id": "speech_1",
            "type": "dj",
            "stream_url": "https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg",
            "transcript": "Hope you're having an awesome day listening to PrivateFM AI. Let's get back into the music."
          },
        ),
      ];
    }
  }

  Future<void> recordPlaybackHistory(int songId, bool skipped, int durationPlayed) async {
    try {
      await _dio.post(
        "/api/playback/history",
        queryParameters: {
          "song_id": songId,
          "skipped": skipped,
          "duration_played": durationPlayed
        },
      );
    } catch (e) {
      // Ignore network errors for background telemetry
    }
  }

  Future<void> linkCatalogSong({
    required String title,
    required String artist,
    String? youtubeId,
    String? coverUrl,
  }) async {
    await _dio.post(
      "/api/music/link-catalog",
      data: {
        "title": title,
        "artist": artist,
        "youtube_id": (youtubeId == null || youtubeId.trim().isEmpty) ? null : youtubeId,
        "cover_url": (coverUrl == null || coverUrl.trim().isEmpty) ? null : coverUrl,
        "duration": 180,
      },
    );
  }
}
