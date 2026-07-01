import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/features/auth/data/auth_repository.dart';

final stationRepositoryProvider = Provider((ref) {
  final dio = Dio(BaseOptions(
    baseUrl: const String.fromEnvironment('API_BASE_URL', defaultValue: 'http://localhost:8000'),
    connectTimeout: const Duration(seconds: 5),
    receiveTimeout: const Duration(seconds: 5),
  ));
  
  // Inject authentication header
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

  return StationRepository(dio);
});

class StationRepository {
  final Dio _dio;

  StationRepository(this._dio);

  Future<List<Map<String, dynamic>>> fetchStations() async {
    try {
      final response = await _dio.get("/api/stations");
      final List<dynamic> data = response.data;
      return List<Map<String, dynamic>>.from(data);
    } catch (e) {
      return [];
    }
  }

  Future<Map<String, dynamic>?> createStation({
    required String name,
    required String mood,
    required Map<String, dynamic> musicPreferences,
    required Map<String, dynamic> voiceConfig,
  }) async {
    try {
      final response = await _dio.post(
        "/api/stations",
        data: {
          "name": name,
          "mood": mood,
          "music_preferences": musicPreferences,
          "voice_config": voiceConfig,
        },
      );
      return Map<String, dynamic>.from(response.data);
    } catch (e) {
      return null;
    }
  }

  Future<Map<String, dynamic>?> updateStation({
    required int id,
    required String name,
    required String mood,
    required Map<String, dynamic> musicPreferences,
    required Map<String, dynamic> voiceConfig,
  }) async {
    try {
      final response = await _dio.put(
        "/api/stations/$id",
        data: {
          "name": name,
          "mood": mood,
          "music_preferences": musicPreferences,
          "voice_config": voiceConfig,
        },
      );
      return Map<String, dynamic>.from(response.data);
    } catch (e) {
      return null;
    }
  }

  Future<bool> deleteStation(int id) async {
    try {
      await _dio.delete("/api/stations/$id");
      return true;
    } catch (e) {
      return false;
    }
  }
}
