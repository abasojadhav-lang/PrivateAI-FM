import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:glass_kit/glass_kit.dart';
import 'package:frontend/core/theme/theme.dart';
import 'package:frontend/features/stations/presentation/station_controller.dart';

class StationWizardScreen extends ConsumerStatefulWidget {
  const StationWizardScreen({super.key});

  @override
  ConsumerState<StationWizardScreen> createState() => _StationWizardScreenState();
}

class _StationWizardScreenState extends ConsumerState<StationWizardScreen> {
  int _currentStep = 0;
  final _formKey = GlobalKey<FormState>();

  // Form Fields
  final _nameController = TextEditingController();
  String _selectedMood = "Workout";
  String _selectedPersonality = "Funny";
  String _selectedVoice = "Male";
  final List<String> _selectedGenres = ["Pop"];
  final List<String> _selectedLanguages = ["Marathi"];
  final List<String> _languages = ["Marathi", "Hindi", "English"];
  String _newsFrequency = "Medium";
  String _weatherFrequency = "Medium";

  final List<String> _moods = ["Workout", "Sleep", "Study", "Driving", "Morning", "Coding"];
  final List<String> _personalities = ["Professional", "Funny", "Sarcastic", "Calm", "Energetic"];
  final List<String> _genres = ["Pop", "Rock", "Synthwave", "Hip-Hop", "Jazz", "Metal", "Classical"];

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  void _nextStep() {
    if (_currentStep == 0) {
      if (_formKey.currentState!.validate()) {
        setState(() => _currentStep++);
      }
    } else if (_currentStep < 2) {
      setState(() => _currentStep++);
    } else {
      _saveStation();
    }
  }

  void _prevStep() {
    if (_currentStep > 0) {
      setState(() => _currentStep--);
    }
  }

  Future<void> _saveStation() async {
    final success = await ref.read(stationControllerProvider.notifier).createStation(
      name: _nameController.text.trim(),
      mood: _selectedMood,
      musicPreferences: {
        "genres": _selectedGenres,
        "languages": _selectedLanguages,
      },
      voiceConfig: {
        "personality": _selectedPersonality,
        "voice": _selectedVoice,
        "news_frequency": _newsFrequency,
        "weather_frequency": _weatherFrequency,
      },
    );

    if (success && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Station Created Successfully!"), backgroundColor: AppColors.secondary),
      );
      Navigator.pop(context);
    }
  }

  @override
  Widget build(BuildContext context) {
    final isLoading = ref.watch(stationControllerProvider).isLoading;

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text("Create AI Station", style: TextStyle(color: Colors.white)),
        centerTitle: true,
      ),
      body: Stack(
        children: [
          // Background neon blur circles
          Container(color: AppColors.background),
          Positioned(
            top: -50,
            right: -50,
            child: Container(
              width: 250,
              height: 250,
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
          
          SafeArea(
            child: Center(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 24.0),
                child: Column(
                  children: [
                    // Wizard progress indicator
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: List.generate(3, (index) => _buildStepIndicator(index)),
                    ),
                    const SizedBox(height: 32),
                    
                    // Glassmorphism card body
                    GlassContainer.clearGlass(
                      height: 440,
                      width: double.infinity,
                      borderRadius: BorderRadius.circular(28),
                      borderColor: AppColors.border,
                      borderWidth: 1.0,
                      gradient: LinearGradient(
                        colors: [
                          AppColors.cardBackground.withOpacity(0.5),
                          AppColors.cardBackground.withOpacity(0.08),
                        ],
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(24.0),
                        child: isLoading
                            ? const Center(child: CircularProgressIndicator(color: AppColors.secondary))
                            : Form(
                                key: _formKey,
                                child: _buildStepContent(),
                              ),
                      ),
                    ),
                    const SizedBox(height: 32),
                    
                    // Nav Buttons
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        if (_currentStep > 0)
                          ElevatedButton(
                            onPressed: _prevStep,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppColors.cardBackground,
                              side: const BorderSide(color: AppColors.border),
                            ),
                            child: const Text("Back"),
                          )
                        else
                          const SizedBox(),
                        ElevatedButton(
                          onPressed: _nextStep,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.primary,
                          ),
                          child: Text(_currentStep == 2 ? "Create Station" : "Next"),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStepIndicator(int index) {
    final isActive = _currentStep == index;
    final isDone = _currentStep > index;
    
    return Row(
      children: [
        CircleAvatar(
          radius: 16,
          backgroundColor: isDone
              ? AppColors.secondary
              : (isActive ? AppColors.primary : AppColors.cardBackground),
          child: isDone
              ? const Icon(Icons.check, size: 16, color: Colors.white)
              : Text("${index + 1}", style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
        ),
        if (index < 2)
          Container(
            width: 40,
            height: 2,
            color: isDone ? AppColors.secondary : AppColors.border,
          ),
      ],
    );
  }

  Widget _buildStepContent() {
    switch (_currentStep) {
      case 0:
        return _buildStep1Basics();
      case 1:
        return _buildStep2DJ();
      case 2:
        return _buildStep3Music();
      default:
        return const SizedBox();
    }
  }

  Widget _buildStep1Basics() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text("Station Details", style: Theme.of(context).textTheme.headlineMedium),
        const SizedBox(height: 24),
        TextFormField(
          controller: _nameController,
          decoration: const InputDecoration(
            labelText: "Station Name",
            hintText: "e.g., Morning Chill, Coding FM",
            prefixIcon: Icon(Icons.radio, color: AppColors.textSecondary),
          ),
          validator: (value) {
            if (value == null || value.isEmpty) {
              return "Please enter a station name";
            }
            return null;
          },
        ),
        const SizedBox(height: 24),
        Text("Select Mood/Preset", style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: _moods.map((mood) {
            final isSelected = _selectedMood == mood;
            return ChoiceChip(
              label: Text(mood),
              selected: isSelected,
              onSelected: (selected) {
                if (selected) setState(() => _selectedMood = mood);
              },
              selectedColor: AppColors.primary,
              backgroundColor: AppColors.cardBackground,
              labelStyle: TextStyle(color: isSelected ? Colors.white : AppColors.textSecondary),
            );
          }).toList(),
        )
      ],
    );
  }

  Widget _buildStep2DJ() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text("DJ Configuration", style: Theme.of(context).textTheme.headlineMedium),
        const SizedBox(height: 20),
        
        Text("Voice Gender", style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: RadioListTile<String>(
                title: const Text("Male"),
                value: "Male",
                groupValue: _selectedVoice,
                onChanged: (val) => setState(() => _selectedVoice = val!),
                activeColor: AppColors.secondary,
              ),
            ),
            Expanded(
              child: RadioListTile<String>(
                title: const Text("Female"),
                value: "Female",
                groupValue: _selectedVoice,
                onChanged: (val) => setState(() => _selectedVoice = val!),
                activeColor: AppColors.secondary,
              ),
            ),
          ],
        ),
        
        const SizedBox(height: 16),
        Text("DJ Personality", style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 12),
        DropdownButtonFormField<String>(
          value: _selectedPersonality,
          decoration: const InputDecoration(
            prefixIcon: Icon(Icons.face, color: AppColors.textSecondary),
          ),
          dropdownColor: AppColors.background,
          items: _personalities.map((p) {
            return DropdownMenuItem<String>(
              value: p,
              child: Text(p),
            );
          }).toList(),
          onChanged: (val) => setState(() => _selectedPersonality = val!),
        ),
      ],
    );
  }

  Widget _buildStep3Music() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text("Music & Updates", style: Theme.of(context).textTheme.headlineMedium),
        const SizedBox(height: 16),
        
        Text("Favorite Genres", style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 10),
        Wrap(
          spacing: 6,
          runSpacing: 6,
          children: _genres.map((genre) {
            final isSelected = _selectedGenres.contains(genre);
            return FilterChip(
              label: Text(genre),
              selected: isSelected,
              onSelected: (selected) {
                setState(() {
                  if (selected) {
                    _selectedGenres.add(genre);
                  } else {
                    _selectedGenres.remove(genre);
                  }
                });
              },
              selectedColor: AppColors.primary,
              backgroundColor: AppColors.cardBackground,
              labelStyle: TextStyle(color: isSelected ? Colors.white : AppColors.textSecondary),
            );
          }).toList(),
        ),
        
        const SizedBox(height: 16),
        Text("Select Languages", style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 10),
        Wrap(
          spacing: 6,
          runSpacing: 6,
          children: _languages.map((lang) {
            final isSelected = _selectedLanguages.contains(lang);
            return FilterChip(
              label: Text(lang),
              selected: isSelected,
              onSelected: (selected) {
                setState(() {
                  if (selected) {
                    _selectedLanguages.add(lang);
                  } else {
                    if (_selectedLanguages.length > 1) {
                      _selectedLanguages.remove(lang);
                    }
                  }
                });
              },
              selectedColor: AppColors.primary,
              backgroundColor: AppColors.cardBackground,
              labelStyle: TextStyle(color: isSelected ? Colors.white : AppColors.textSecondary),
            );
          }).toList(),
        ),
        
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text("News Info", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                  DropdownButton<String>(
                    value: _newsFrequency,
                    dropdownColor: AppColors.background,
                    underline: const SizedBox(),
                    items: ["High", "Medium", "Low", "Off"].map((f) {
                      return DropdownMenuItem(value: f, child: Text(f));
                    }).toList(),
                    onChanged: (val) => setState(() => _newsFrequency = val!),
                  ),
                ],
              ),
            ),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text("Weather Info", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                  DropdownButton<String>(
                    value: _weatherFrequency,
                    dropdownColor: AppColors.background,
                    underline: const SizedBox(),
                    items: ["High", "Medium", "Low", "Off"].map((f) {
                      return DropdownMenuItem(value: f, child: Text(f));
                    }).toList(),
                    onChanged: (val) => setState(() => _weatherFrequency = val!),
                  ),
                ],
              ),
            ),
          ],
        )
      ],
    );
  }
}
