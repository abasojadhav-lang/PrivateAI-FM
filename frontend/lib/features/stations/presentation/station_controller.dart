import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/features/stations/data/station_repository.dart';
import 'package:frontend/features/playback/presentation/playback_controller.dart';

class StationState {
  final List<Map<String, dynamic>> stations;
  final Map<String, dynamic>? activeStation;
  final bool isLoading;
  final String? error;

  StationState({
    this.stations = const [],
    this.activeStation,
    this.isLoading = false,
    this.error,
  });

  StationState copyWith({
    List<Map<String, dynamic>>? stations,
    Map<String, dynamic>? activeStation,
    bool? isLoading,
    String? error,
  }) {
    return StationState(
      stations: stations ?? this.stations,
      activeStation: activeStation ?? this.activeStation,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }
}

class StationNotifier extends StateNotifier<StationState> {
  final StationRepository _repository;
  final Ref _ref;

  StationNotifier(this._repository, this._ref) : super(StationState()) {
    fetchStations();
  }

  Future<void> fetchStations() async {
    state = state.copyWith(isLoading: true);
    final list = await _repository.fetchStations();
    state = state.copyWith(stations: list, isLoading: false);
  }

  Future<bool> createStation({
    required String name,
    required String mood,
    required Map<String, dynamic> musicPreferences,
    required Map<String, dynamic> voiceConfig,
  }) async {
    state = state.copyWith(isLoading: true);
    final newStation = await _repository.createStation(
      name: name,
      mood: mood,
      musicPreferences: musicPreferences,
      voiceConfig: voiceConfig,
    );
    state = state.copyWith(isLoading: false);
    
    if (newStation != null) {
      await fetchStations();
      return true;
    }
    return false;
  }

  Future<void> deleteStation(int id) async {
    final success = await _repository.deleteStation(id);
    if (success) {
      if (state.activeStation?['id'] == id) {
        state = state.copyWith(activeStation: null);
      }
      await fetchStations();
    }
  }

  void setActiveStation(Map<String, dynamic> station) {
    state = state.copyWith(activeStation: station);
    // Reload queue for this active station!
    final stationId = station['id'] as int;
    _ref.read(playbackControllerProvider.notifier).loadStationQueue(stationId);
  }
}

final stationControllerProvider = StateNotifierProvider<StationNotifier, StationState>((ref) {
  final repo = ref.watch(stationRepositoryProvider);
  return StationNotifier(repo, ref);
});
