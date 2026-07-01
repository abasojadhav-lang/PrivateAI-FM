import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final secureStorageProvider = Provider((ref) => const FlutterSecureStorage());

final authRepositoryProvider = Provider((ref) {
  final dio = Dio(BaseOptions(
    // 10.0.2.2 is the special alias for localhost on Android emulators
    // Using http://localhost:8000 for standard web/desktop builds
    baseUrl: const String.fromEnvironment('API_BASE_URL', defaultValue: 'http://localhost:8000'),
    connectTimeout: const Duration(seconds: 5),
    receiveTimeout: const Duration(seconds: 5),
  ));
  
  final storage = ref.watch(secureStorageProvider);
  return AuthRepository(dio, storage);
});

class AuthRepository {
  final Dio _dio;
  final FlutterSecureStorage _storage;
  static const _tokenKey = "auth_jwt_token";

  AuthRepository(this._dio, this._storage) {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await getToken();
        if (token != null) {
          options.headers["Authorization"] = "Bearer $token";
        }
        return handler.next(options);
      },
    ));
  }

  Future<String?> getToken() async {
    return await _storage.read(key: _tokenKey);
  }

  Future<bool> isAuthenticated() async {
    final token = await getToken();
    return token != null;
  }

  Future<void> logout() async {
    await _storage.delete(key: _tokenKey);
  }

  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await _dio.post(
        "/api/auth/login",
        data: {
          "email": email,
          "password": password,
        },
      );
      
      final token = response.data["access_token"];
      if (token != null) {
        await _storage.write(key: _tokenKey, value: token);
      }
      return {"success": true, "data": response.data};
    } on DioException catch (e) {
      final errorMsg = e.response?.data["detail"] ?? "Login failed. Please check credentials.";
      return {"success": false, "error": errorMsg};
    } catch (e) {
      return {"success": false, "error": "An unexpected error occurred."};
    }
  }

  Future<Map<String, dynamic>> register(String email, String password) async {
    try {
      final response = await _dio.post(
        "/api/auth/register",
        data: {
          "email": email,
          "password": password,
        },
      );
      return {"success": true, "data": response.data};
    } on DioException catch (e) {
      final errorMsg = e.response?.data["detail"] ?? "Registration failed. Email might already be taken.";
      return {"success": false, "error": errorMsg};
    } catch (e) {
      return {"success": false, "error": "An unexpected error occurred."};
    }
  }

  Future<Map<String, dynamic>?> getCurrentUser() async {
    try {
      final response = await _dio.get("/api/auth/me");
      return response.data;
    } catch (e) {
      return null;
    }
  }
}
